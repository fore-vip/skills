# 主流云厂商对象存储（OSS）助手参考

> 各厂商对同一概念命名不同，本文统一对照后再看分节：

| 概念 | 阿里云 | 腾讯云 | AWS | 华为云 | MinIO | 七牛云 |
|------|--------|--------|-----|--------|-------|--------|
| 服务名 | OSS | COS | S3 | OBS | MinIO | Kodo（对象存储） |
| 存储空间 | Bucket | 存储桶 Bucket | Bucket | Bucket | Bucket | 空间（Bucket） |
| 官方 CLI | ossutil | coscli | AWS CLI | obsutil | mc | qshell |
| 访问凭证 | AccessKey ID / Secret | SecretId / SecretKey | Access Key ID / Secret | AK / SK | Access Key / Secret Key | AccessKey / SecretKey |

> 版本与下载地址可能随官方更新，命令执行失败时以各节「官方文档」链接为准。

---

## 阿里云 OSS（ossutil）

> **现行版本是 ossutil 2.0**（2.4.0+）。2.0 与 1.x 命令/配置差异大，以下步骤按 2.0 编写；
> 若本机是 1.x（`ossutil version` 输出 `v1.x.x`），跳到本节末尾「1.x → 2.0 关键差异」再操作。

**安装 ossutil 2.0（官方二进制，按架构选一个）**

```bash
# macOS Intel / x86_64
curl -O https://gosspublic.alicdn.com/ossutil/v2/2.4.0/ossutil-2.4.0-mac-amd64.zip
# macOS Apple Silicon / arm64
curl -O https://gosspublic.alicdn.com/ossutil/v2/2.4.0/ossutil-2.4.0-mac-arm64.zip
# Linux x86_64
curl -O https://gosspublic.alicdn.com/ossutil/v2/2.4.0/ossutil-2.4.0-linux-amd64.zip

unzip ossutil-2.4.0-mac-amd64.zip && cd ossutil-2.4.0-mac-amd64
chmod 755 ossutil
mv ossutil ~/.local/bin/          # 用户级；系统级用 sudo mv ossutil /usr/local/bin/
ossutil version                   # 验证：输出 2.4.0
```

> 升级时**先备份旧二进制**（`cp $(which ossutil) $(which ossutil)-v1.7.19.bak`）再覆盖，方便回滚。
> 一键脚本 `curl https://gosspublic.alicdn.com/ossutil/install.sh | sudo bash` 装的是 **1.x**，新装不要用。

**获取 AK/SK**
- 控制台：https://ram.console.aliyun.com/users → 创建用户 → 勾选 `OpenAPI 调用访问` → 生成 AccessKey（仅创建时可见，立即保存）
- 强烈建议使用 RAM 子账号并仅授予 `AliyunOSSFullAccess`（或按桶最小化授权），不要用主账号 AK

**配置凭证（2.0 必填 region，不是 endpoint）**

```bash
ossutil config
# 交互式输入：AccessKey ID / AccessKey Secret / Region（如 cn-hangzhou）
# 2.0 签名已升到 V4，region 为必填项；endpoint 由 region 自动推导（内网/自定义域名再单独指定）
ossutil ls            # 验证连通
```

生成的 `~/.ossutilconfig` 格式（支持多套配置，用 `--profile` 引用）：

```ini
[default]
accessKeyID=your_accesskey_id
accessKeySecret=your_accesskey_secret
region=cn-hangzhou

[profile shenzhen]
accessKeyID=your_accesskey_id_1
accessKeySecret=your_accesskey_secret_1
region=cn-shenzhen
```

**1.x → 2.0 关键差异（升级必看）**

| 项 | 1.x | 2.0 |
|---|---|---|
| 必填配置 | AK / SK / **Endpoint** | AK / SK / **Region**（漏配报 `region must be set in sign version 4`） |
| 帮助 | `ossutil help` | `ossutil --help`（`help` 子命令已移除） |
| 删除 Bucket | `rm` | `rb`；且 `-m`（分片）与 `-r` 必须分两次执行 |
| 签名 URL | `sign` | `presign`（`sign` 保留为别名但选项不同，V4 签名最长 7 天） |
| 追加写 | `appendfromfile` | `append`（数据源支持本地 / OSS / stdin） |
| 对象属性 | `set-acl` / `set-meta` | `set-props`（别名保留，选项不同） |
| Bucket 配置 | `logging` / `lifecycle` 等根命令 | `ossutil api put-bucket-xxx`（参数支持 XML / JSON） |
| 增量上传 | `--snapshot-path` | 已移除，改用 `-u` / `--update` |
| `--include/--exclude` | 只匹配文件名，全规则顺序求值 | 匹配全路径，**首个匹配即停止** |
| 对象间拷贝 | 只拷数据 | 默认连带元数据与标签，用 `--copy-props` 控制 |

- 官方文档：https://help.aliyun.com/zh/oss/developer-reference/ossutil
- 迁移指南：https://help.aliyun.com/document_detail/2804545.html
- 差异对照：https://help.aliyun.com/document_detail/2804546.html

**域名绑定**
1. 控制台 → 对应 Bucket → 概览/传输管理 → 绑定自定义域名（bucket 绑定域名需同账号下已备案域名，中国大陆 region 强制备案）
2. DNS 添加 CNAME：`cdn.example.com` → `<bucket>.<endpoint域名>`（如 `my-bucket.oss-cn-hangzhou.aliyuncs.com`）
3. 需 HTTPS 时在 OSS 控制台对该域名申请免费证书或上传已有证书
- 文档：https://help.aliyun.com/zh/oss/user-guide/bind-custom-domain-names

---

## 腾讯云 COS（coscli）

**安装（官方下载二进制）**

```bash
# 下载地址（按系统选择，macOS Apple Silicon 为 coscli-darwin-arm64）
# https://cloud.tencent.com/document/product/436/63144
chmod +x coscli && sudo mv coscli /usr/local/bin/
coscli --version   # 验证
```

**获取 SecretId/SecretKey**
- 控制台：https://console.cloud.tencent.com/cam/capi → 新建密钥
- 建议使用子账号（CAM）并按存储桶授权

**配置凭证**

```bash
coscli config init   # 或 coscli config generate 生成 ~/.coscli.yaml 后填写
coscli ls cos://     # 验证连通
```

**域名绑定**
1. 控制台 → 存储桶 → 域名与传输管理 → 自定义源站域名（中国大陆地域需备案）
2. DNS 添加 CNAME：`img.example.com` → `<bucket-appid>.cos.<region>.myqcloud.com`
3. HTTPS：可在腾讯云 SSL 控制台申请免费证书后对域名开启
- 文档：https://cloud.tencent.com/document/product/436/18424

---

## AWS S3（AWS CLI）

**安装（macOS）**

```bash
brew install awscli    # 或官方 pkg：https://aws.amazon.com/cli/
aws --version          # 验证
```

**获取 Access Key**
- 控制台：https://console.aws.amazon.com/iam/ → Users → Security credentials → Create access key
- 必须使用 IAM 用户 AK，禁止 AWS 根账号 AK；策略最小化（如 `AmazonS3FullAccess`）

**配置凭证**

```bash
aws configure
# Access Key ID / Secret / 默认区域（如 ap-northeast-1）/ 输出格式 json
aws s3 ls   # 验证
```

**域名绑定**
- 方式 A（推荐）：S3 作为源站 + CloudFront 分发 → CloudFront 里 Alternate domain name 填自定义域名 → CNAME 指向 CloudFront 域名（HTTPS 用 ACM 免费证书）
- 方式 B（仅 HTTP 或证书覆盖）：直接 CNAME 到 `<bucket>.s3.<region>.amazonaws.com`（根域名需 Route 53 ALIAS）
- 文档：https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/CNAMEs.html

---

## 华为云 OBS（obsutil）

**安装（官方下载）**

```bash
# 下载地址（tar.gz 解压后为单二进制）：
# https://support.huaweicloud.com/utiltg-obs/obs_11_0001.html
chmod +x obsutil && sudo mv obsutil /usr/local/bin/
obsutil version   # 验证
```

**获取 AK/SK**
- 控制台：https://console.huaweicloud.com/iam/ → 我的凭证 → 访问密钥 → 新增访问密钥（CSV 下载，仅一次）
- 建议使用 IAM 子用户并授予 OBS 权限

**配置凭证**

```bash
obsutil config -i=<AK> -k=<SK> -e=obs.cn-north-4.myhuaweicloud.com
obsutil ls -s   # 验证
```

**域名绑定**
1. 控制台 → 桶 → 概览 → 自定义域名（中国大陆 region 需备案域名）
2. DNS 添加 CNAME：`static.example.com` → `<bucket>.<endpoint域名>`
3. HTTPS 需在 CDN/OBS 侧配置证书
- 文档：https://support.huaweicloud.com/usermanual-obs/obs_03_0034.html

---

## MinIO（mc，自建/S3 兼容）

**安装（macOS）**

```bash
brew install minio-mc    # 或 curl 官方二进制：https://dl.min.io/client/mc/release/
mc --version             # 验证
```

**获取 Access Key**
- 自建 MinIO：启动时由 `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` 指定，或 `mc admin user add` 创建子用户
- MinIO 商业云（console.min.io）在控制台 Access Keys 页生成

**配置凭证**

```bash
mc alias set myminio https://<your-minio-endpoint> <ACCESS_KEY> <SECRET_KEY>
mc ls myminio   # 验证
```

**域名绑定**
- DNS 直接 A/CNAME 指向 MinIO 服务端域名/IP，客户端 `mc alias` 里使用该域名即可；S3 风格路径建议用 `--config-dir` 与 `MINIO_DOMAIN` 环境变量启用虚拟主机风格域名
- 文档：https://min.io/docs/minio/linux/reference/minio-mc.html

---

## 七牛云 Kodo（qshell）

**安装（官方 GitHub Release）**

```bash
# https://github.com/qiniu/qshell/releases 下载对应系统二进制
chmod +x qshell && sudo mv qshell /usr/local/bin/
qshell version   # 验证
```

**获取 AK/SK**
- 控制台：https://portal.qiniu.com/user/key → 密钥管理

**配置凭证**

```bash
qshell account <AK> <SK> <name>
qshell buckets   # 验证
```

**域名绑定（七牛必须绑定自定义域名）**
1. 空间创建后仅提供 30 天测试域名，正式使用必须绑定已备案的自定义域名
2. 控制台 → 空间设置 → 域名管理 → 绑定加速域名 → 按提示 CNAME 到七牛分配的 CDN 域名
3. HTTPS 需在七牛 SSL 证书管理上传/申请证书后开启
- 文档：https://developer.qiniu.com/kodo/6555/the-domain-name-management
