/**
 * 前凌智选 Chrome 插件 - popup.js
 * 版本：v2.0
 * 活动列表：POST https://mcp.fore.vip/act/search （免鉴权）
 * 活动详情：https://fore.vip/pages/activity/detail?id=<_id>
 * 发布活动：跳转 Open Key 管理页 https://fore.vip/web/key
 *            （在 web 端用 Open Key 调 act/create 创建活动，Key = ai-key._id）
 */

// MCP 端点与页面
const MCP_ACT_SEARCH_URL = 'https://mcp.fore.vip/act/search';
const DETAIL_BASE = 'https://fore.vip/pages/activity/detail?id=';
const KEY_PAGE = 'https://fore.vip/web/key';
const DOC_PAGE = 'https://doc.fore.vip';
const PAGE_SIZE = 20;

// 状态
let currentKeyword = '';
let currentPage = 1;
let total = 0;
let hasMore = true;
let isLoading = false;

// 初始化
document.addEventListener('DOMContentLoaded', function () {
    initPublishMenu();
    initSearch();
    initAutoLoad();
    loadActivities(true);
});

// 发布菜单
function initPublishMenu() {
    const publishBtn = document.getElementById('publishBtn');
    const publishMenu = document.getElementById('publishMenu');

    publishBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        publishMenu.classList.toggle('show');
    });

    document.addEventListener('click', function () {
        publishMenu.classList.remove('show');
    });

    // 发布活动 → 跳转 Open Key 管理页（生成/复制 Open Key 后可在 web 端创建活动）
    document.getElementById('publishActivity').addEventListener('click', function (e) {
        e.preventDefault();
        window.open(KEY_PAGE, '_blank');
    });

    document.getElementById('aboutLink').addEventListener('click', function (e) {
        e.preventDefault();
        window.open(DOC_PAGE, '_blank');
    });
}

// 搜索
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');

    searchBtn.addEventListener('click', function () {
        currentKeyword = searchInput.value.trim();
        resetAndLoad();
    });

    searchInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            currentKeyword = searchInput.value.trim();
            resetAndLoad();
        }
    });
}

// 重置并重新加载（搜索/清空关键词时）
function resetAndLoad() {
    currentPage = 1;
    total = 0;
    hasMore = true;
    loadActivities(true);
}

// 自动加载（滚动到底部加载下一页）
function initAutoLoad() {
    const list = document.getElementById('activityList');
    list.addEventListener('scroll', function () {
        if (this.scrollTop + this.clientHeight >= this.scrollHeight - 100 && hasMore && !isLoading) {
            currentPage += 1;
            loadActivities(false);
        }
    });
}

// 加载活动列表
async function loadActivities(clear = false) {
    if (isLoading) return;
    isLoading = true;

    const list = document.getElementById('activityList');
    const autoLoadIndicator = document.getElementById('autoLoadIndicator');
    const noMore = document.getElementById('noMore');
    const errorEl = document.getElementById('errorMessage');

    if (clear) {
        list.innerHTML = '<div class="loading">加载中...</div>';
        autoLoadIndicator.classList.remove('show');
        noMore.classList.remove('show');
        errorEl.style.display = 'none';
    }

    try {
        const response = await fetch(MCP_ACT_SEARCH_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                keyword: currentKeyword || undefined,
                page: currentPage,
                pageSize: PAGE_SIZE
            })
        });

        const result = await response.json();

        if (clear) list.innerHTML = '';

        const activities = Array.isArray(result.list) ? result.list : [];
        if (activities.length === 0 && clear) {
            list.innerHTML = '<div class="empty-state">暂无活动</div>';
            hasMore = false;
            noMore.classList.add('show');
        } else {
            activities.forEach(a => list.appendChild(createActivityCard(a)));
            total = result.total || 0;
            // 已加载数量 < 总数 → 还有更多
            hasMore = (currentPage * PAGE_SIZE) < total;
            if (!hasMore) noMore.classList.add('show');
        }
    } catch (error) {
        console.error('活动加载失败:', error);
        if (clear) {
            errorEl.textContent = '活动加载失败，请检查网络或稍后重试';
            errorEl.style.display = 'block';
        }
    } finally {
        isLoading = false;
        const loadingEl = list.querySelector('.loading');
        if (loadingEl) loadingEl.style.display = 'none';
    }
}

// 创建活动卡片
function createActivityCard(a) {
    const card = document.createElement('div');
    card.className = 'activity-card';
    card.addEventListener('click', function () {
        if (a._id) window.open(DETAIL_BASE + a._id, '_blank');
    });

    const tags = Array.isArray(a.tags) ? a.tags : [];
    const tagHtml = tags.map(t => `<span class="activity-tag">${escapeHtml(t)}</span>`).join('');
    const joinHtml = (typeof a.participant_count === 'number')
        ? `<span class="activity-join">👥 ${formatCount(a.participant_count)}</span>` : '';

    card.innerHTML = `
        <div class="activity-content">${escapeHtml(a.content || '未命名活动')}</div>
        <div class="activity-address">📍 ${escapeHtml(a.address || '地点待定')}</div>
        ${tagHtml ? `<div class="activity-tags">${tagHtml}</div>` : ''}
        <div class="activity-meta">
            <span class="activity-views">👁 ${formatCount(a.view_count || 0)}</span>
            ${joinHtml}
        </div>
    `;

    // 封面图（有则显示，加载失败自动隐藏）
    if (a.cover) {
        const img = document.createElement('img');
        img.className = 'activity-cover';
        img.loading = 'lazy';
        img.alt = '';
        img.addEventListener('error', function () {
            img.style.display = 'none';
        });
        img.src = a.cover;
        card.insertBefore(img, card.firstChild);
    }

    return card;
}

// HTML 转义
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 数字格式化（万 / 千）
function formatCount(n) {
    n = Number(n) || 0;
    if (n >= 10000) return (n / 10000).toFixed(1) + 'w';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
    return n.toString();
}
