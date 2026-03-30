/**
 * GitHub Trending Search - 恢复 GitHub 搜索功能
 * 用于智能发布功能的内容来源
 */

/**
 * 获取 GitHub Trending 项目
 * @param {string} language - 编程语言
 * @param {string} since - 时间范围 (daily/weekly/monthly)
 * @param {number} limit - 结果数量
 * @param {string} query - 搜索关键词
 */
async function getGitHubTrending(language = '', since = 'daily', limit = 10, query = '') {
  const url = buildTrendingUrl(language, since)
  
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml'
      }
    })
    
    if (!response.ok) {
      throw new Error(`GitHub request failed: ${response.status}`)
    }
    
    const html = await response.text()
    const repos = parseTrendingHTML(html, limit, query)
    
    return {
      success: true,
      data: repos,
      source: 'github-trending'
    }
    
  } catch (error) {
    // Fallback to GitHub API
    return await fallbackToAPI(language, query, limit)
  }
}

/**
 * 构建 GitHub Trending URL
 */
function buildTrendingUrl(language, since) {
  let url = 'https://github.com/trending'
  const params = []
  
  if (language) {
    params.push(`spoken_language_code=${language}`)
  }
  if (since) {
    params.push(`since=${since}`)
  }
  
  return params.length ? `${url}?${params.join('&')}` : url
}

/**
 * 解析 HTML 提取项目信息
 */
function parseTrendingHTML(html, limit, query) {
  const repos = []
  const repoRegex = /<article[\s\S]*?<h2[\s\S]*?<a\s+href="([^"]+)"[\s\S]*?<p[\s\S]*?>([\s\S]*?)<\/p>[\s\S]*?<\/article>/g
  
  let match
  let count = 0
  
  while ((match = repoRegex.exec(html)) !== null && count < limit) {
    const fullName = match[1].trim()
    const description = match[2].trim().replace(/\s+/g, ' ')
    
    // 关键词过滤
    if (query && !matchesQuery(description, fullName, query)) {
      continue
    }
    
    const [author, name] = fullName.split('/').filter(Boolean)
    const stars = extractMetric(html, match.index, 'star')
    const forks = extractMetric(html, match.index, 'fork')
    const lang = extractLanguage(html, match.index)
    
    repos.push({
      name: fullName,
      author: author || '',
      repo: name || '',
      description: description || '暂无描述',
      url: `https://github.com${fullName}`,
      stars,
      forks,
      language: lang
    })
    
    count++
  }
  
  return repos
}

/**
 * 检查是否匹配查询
 */
function matchesQuery(description, fullName, query) {
  const q = query.toLowerCase()
  return description.toLowerCase().includes(q) || 
         fullName.toLowerCase().includes(q)
}

/**
 * 提取指标数据（stars/forks）
 */
function extractMetric(html, startIndex, type) {
  const snippet = html.substring(startIndex, startIndex + 2000)
  const regex = new RegExp(`svg[^>]*${type}[^>]*>[\\s\\S]*?(\\d{1,3}(?:,\\d{3})*(?:\\.\\d+k)?)\\s*<\\/span>`)
  const match = snippet.match(regex)
  return match ? parseNumber(match[1]) : 0
}

/**
 * 提取编程语言
 */
function extractLanguage(html, startIndex) {
  const snippet = html.substring(startIndex, startIndex + 2000)
  const match = snippet.match(/itemprop="programmingLanguage"[^>]*>([^<]+)</)
  return match ? match[1].trim() : 'Unknown'
}

/**
 * 解析数字
 */
function parseNumber(str) {
  if (!str) return 0
  str = str.replace(/,/g, '').trim()
  return str.endsWith('k') ? Math.round(parseFloat(str) * 1000) : parseInt(str) || 0
}

/**
 * 备用方案：使用 GitHub API
 */
async function fallbackToAPI(language, query, limit) {
  const searchQuery = buildSearchQuery(language, query)
  const url = `https://api.github.com/search/repositories?q=${searchQuery}&sort=stars&order=desc&per_page=${limit}`
  
  const response = await fetch(url, {
    headers: {
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'Workflow-Agent'
    }
  })
  
  if (!response.ok) {
    throw new Error('GitHub API unavailable')
  }
  
  const data = await response.json()
  
  return {
    success: true,
    data: data.items.map(repo => ({
      name: repo.full_name,
      author: repo.owner.login,
      repo: repo.name,
      description: repo.description || '暂无描述',
      url: repo.html_url,
      stars: repo.stargazers_count,
      forks: repo.forks_count,
      language: repo.language || 'Unknown'
    })),
    source: 'github-api'
  }
}

/**
 * 构建搜索查询
 */
function buildSearchQuery(language, query) {
  if (query && language) {
    return `${query}+language:${language}`
  }
  if (language) {
    return `language:${language}`
  }
  if (query) {
    return query
  }
  return 'language:javascript'
}

/**
 * 将 GitHub 项目转换为产品格式
 */
function repoToProduct(repo, tag = '开源') {
  return {
    name: repo.name,
    content: repo.description,
    pic: [],
    tag: tag,
    hot: Math.floor(repo.stars / 1000),
    url: repo.url
  }
}

module.exports = {
  getGitHubTrending,
  repoToProduct
}
