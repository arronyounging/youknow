# Custyle Blog 0-1 搭建规划（Nuxt.js / 内部写作 / SEO 优先）

> 适用背景：Custyle 的定位为 **Agentic Commerce 时代的 AI Merch Agent**，核心价值是把意图转成可交易 SKU，并完成履约闭环。本规划围绕该定位构建从 0-1 的 Blog 架构与执行路径，以 SEO 为首要目标。

---

## 0) 现有官网接入 Blog 需要补齐的点（基于 https://custyle.ai/）

> 现状要点：当前官网导航以 **Beta / Gallery / Features / Community** 为主，顶栏 CTA 为 **Sign In / Start Creating**；页脚以产品与支持为主，没有 Blog/Resources 入口。

**建议补齐**
- **导航与页脚入口**：新增 Blog（或 Resources）主入口，并在页脚补充 Blog / Newsletter / RSS；用“Resources”承载白皮书/案例/Blog 的统一入口，利于 SEO 结构化聚合。
- **信息架构联动**：在首页 Hero 或中部增加 Blog 卡片区，展示 Featured + Latest 1-2 篇，引导爬虫与用户进入内容路径。
- **多语言策略**：如果官网支持中英双语，Blog 需要同步语言策略（zh/en 路由、hreflang、翻译节奏），避免双语混杂导致索引稀释。
- **品牌一致性**：Blog 的标题区、CTA 语气与官网“Start Creating”保持一致，避免调性割裂（建议统一为“Build with Custyle / Start Creating / Book a Demo”）。
- **搜索与分类页**：在 Blog 列表页加入分类/标签筛选与搜索，避免仅靠时间序列；分类页需带引导文案，防止“薄内容”。
- **SEO 基建**：为 Blog 补齐 sitemap、RSS、OpenGraph、JSON-LD、面包屑、canonical，防止与产品页结构冲突。
- **转化路径**：在正文内加入“Build with Custyle / Start Creating / 联系我们”CTA，并结合“Approval Gates / Prompt-to-Product”形成明确价值闭环。

---

## 1) 目标与指标（Week 0）

**目标优先级**：SEO（核心） → 品牌权威 → 线索转化。

**关键指标（建议季度目标）**
- 自然搜索流量（UV / Session）。
- 收录篇数 + 关键词覆盖数（核心词 + 长尾词）。
- 详情页平均停留时长、滚动深度。
- CTA 转化率（订阅 / 咨询 / 预约演示）。

**产出物**
- KPI 表（季度 / 月度）
- 目标用户画像 + 关键词意图矩阵

---

## 2) 信息架构（IA）与页面结构（Week 1）

### 站点结构
- `/blog`（列表页）
- `/blog/[slug]`（详情页）
- `/blog/category/[slug]`（分类页）
- `/blog/tag/[slug]`（可选）
- `/blog/search`（可选）

### 列表页模块（SEO 友好）
- Hero 区（品牌定位 + 主题引导）
- Featured（1-2 篇主推）
- Latest（按时间排序）
- 分类筛选 + 搜索
- 分页 / 加载更多

### 详情页模块（参照 commercetools 结构）
- Hero 图 / 头图
- 标题 + 作者 + 日期 + 阅读时长
- TOC 目录（H2 / H3 自动生成）
- 摘要 / What you’ll learn（5 条要点）
- 正文（图 / 表 / 案例）
- 作者介绍 + 资历背书
- 相关文章推荐 + CTA（咨询 / 预约演示 / 订阅）
- FAQ（可选，用于长尾关键词）

**产出物**
- IA 结构图（可用于内部对齐）
- 页面线框（低保真）
- 组件与模块清单

---

## 3) 内容体系与选题策略（Week 2-3）

### 分类建议（6-8 个）
1. Agentic Commerce 趋势与洞察
2. Merch Agent 实践方法论
3. Prompt-to-Product 案例拆解
4. 供应链 / 履约 / 信任机制
5. 设计与商品化策略
6. 行业场景与应用（社群、活动、创作者、送礼）

### 关键词矩阵（示例）
- 核心词：Agentic Commerce / AI Merch Agent / Prompt-to-Product / Merchandising Agent
- 方法论：意图到 SKU / 设计到履约 / 可授权下单 / Approval Gates
- 行业词：创作者变现 / 个性化商品 / POD / 社群周边 / 活动周边
- 转化词：如何生成可售卖商品 / 商品化工作流 / AI 生成商品页

### 首批选题（12-16 篇）
- 行业趋势（4-5 篇）：Agentic Commerce 2025/2026、ACP 标准解读等
- 实战方法（4-5 篇）：Prompt-to-Product 模型、SKU 生成流程
- 业务案例（3-4 篇）：创作者、社群、活动场景拆解
- 信任机制（1-2 篇）：Approval Gates + 合规与风控

**产出物**
- 选题库（含目标关键词、标题结构）
- 写作模板（标题 / 摘要 / 结构化内容）

---

## 4) 技术实现路径（Nuxt.js）（Week 3-4）

### 内容管理
- **优先建议：Markdown/MDX + Git 管理**（内部写作、成本低、可审阅）
- 可选：轻量 CMS（Strapi / Contentful）

### 需要实现的关键能力
- 文章解析与路由（slug）
- TOC 自动生成
- SEO 元信息（Title / Meta / OG）
- JSON-LD Schema（BlogPosting / Article）
- 图片优化（Nuxt Image / lazy load）
- 站点地图（sitemap）
- RSS（可选）

### 发布流程
- 内部写作 → 评审 → 合并 → 发布
- 每篇文章有标准化 metadata（title/summary/author/date/tags）

**产出物**
- Nuxt 路由与内容模块设计
- 内容模板 + 元数据规范
- 发布 SOP（简版）

---

## 5) SEO 重点动作（Week 4 + 持续）

### 站内 SEO
- 每篇文章 ≥3 个内部链接
- 分类页增加引导段落（避免薄内容）
- 文内引用权威来源（提升可信度）
- H2/H3 结构清晰，含关键词

### 外部 SEO
- 行业引用、权威媒体/报告链接
- 可通过社媒/Newsletter 引流

### 监控与优化
- 2-4 周一轮数据回看
- 旧内容更新（标题优化 / 内链增强）

**产出物**
- SEO 检查清单
- 关键词更新与内容复盘表

---

## 6) 90 天执行节奏（示例）

**第 1-2 周**
- IA + 线框 + 内容模板完成
- 选题库 / 关键词矩阵确定

**第 3-4 周**
- Nuxt Blog 模块开发
- 首批 6-8 篇文章上线

**第 5-8 周**
- 文章持续产出（每周 1-2 篇）
- SEO 监测、结构化数据优化

**第 9-12 周**
- 重点文章更新与内链优化
- 分析转化路径并调整 CTA

---

## 6.1) 执行清单（可直接落地）

### A. Nuxt 代码落地（Sprint 1）
1. **新增路由**：`/blog`、`/blog/[slug]`、`/blog/category/[slug]`。  
2. **内容目录**：新增 `content/blog/`（Markdown/MDX），统一 frontmatter：  
   - `title`、`summary`、`author`、`date`、`tags`、`category`、`cover`、`draft`  
3. **模块与依赖**：  
   - `@nuxt/content`（内容解析）  
   - `@nuxt/image`（图片优化）  
   - `@nuxtjs/sitemap`（站点地图）  
4. **SEO 基础**：  
   - `useHead()` 设置 Title / Meta / OG / Twitter  
   - JSON-LD（BlogPosting）  
   - canonical + breadcrumb  
5. **页面组件**：  
   - `BlogList.vue`（筛选、分页）  
   - `BlogCard.vue`（标题/日期/摘要）  
   - `BlogTOC.vue`（目录）  
   - `BlogAuthor.vue`（作者信息）  
   - `BlogCTA.vue`（转化 CTA）  
6. **站内链接**：  
   - 详情页末尾“相关文章”  
   - 文内至少 3 条内链  

### B. 内容落地（Sprint 2）
1. **首批 6-8 篇 SEO 稳态内容**（趋势 + 方法论）。  
2. **每篇文章遵循模板**：  
   - Title（含关键词）  
   - Summary（120-180 字）  
   - H2/H3 结构化  
   - 引用权威来源  
3. **首批分类上线**：建议先启用 4-6 个核心分类，避免稀疏。  

### C. 上线前检查（Sprint 2 末）
- sitemap 是否包含 blog 路由  
- JSON-LD 是否正确输出  
- OpenGraph 是否在社媒预览正常  
- 404 / 301 是否规范（尤其旧链接迁移）  

---

## 7) 推荐的对外表达（Blog 统一口径）

**主定位（一致口径）**
- Custyle = AI Merch Agent for Agentic Commerce

**一句话释义**
- 把灵感转成可售卖、可履约的商品，并通过审批闸门确保可控可信。

**SEO 关键词聚焦**
- Agentic Commerce
- AI Merch Agent
- Prompt-to-Product
- Merchandising Agent

---

## 下一步建议（可直接执行）

1. 确认 Blog 分类与首批 12-16 篇选题。
2. 采用 Markdown/MDX + Git 管理方式落地。
3. Nuxt 搭建 blog 路由与 SEO 模块。
4. 先完成 6-8 篇“稳态 SEO 内容”，再逐步引入案例与转化型文章。

如果需要，我可以继续输出：
- 选题清单（带关键词与标题模板）
- IA 线框草图与页面模块优先级
- Nuxt 具体组件设计与路由方案
