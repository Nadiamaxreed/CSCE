# SEO 与 GEO 维护说明

更新日期：2026-11-23。

## 本次实现

- 首页提供可直接读取的业务问答。企业站新增五条问答；餐博会保留既有问答，使用同源数据生成 FAQPage，避免正文与标记不一致。
- 公共 SeoHead 输出 WebSite、WebPage、内部页 BreadcrumbList；企业站增加 Organization，静态新闻正文增加 NewsArticle，仅使用已有标题和真实发布日期，不伪造作者或修改时间。
- 展会 Event 只在主首页描述整场展会，避免将联系、隐私、新闻等页面误标为展会详情。
- 保留唯一 canonical，补充站点名称、语言、Open Graph 与 Twitter 分享信息；企业站内页标题包含公司身份，默认描述包含当前页面主题。
- 首页问答使用静态 HTML 与可键盘操作的 details/summary；提供相关栏目链接，方便用户及机器定位业务事实。
- 404 使用 noindex；餐博会依赖接口、查询参数的新闻详情壳页不索引，不进入 sitemap。实时新闻仍由原接口加载，本次没有将接口正文伪装为构建时静态内容。
- 企业站 sitemap 在完整构建后从实际 HTML 生成，排除跳转页、noindex 页面及 404；沈阳站先完成旧 .html 地址整理。餐博会继续使用 Astro sitemap 集成，并过滤详情壳页。
- robots 指向实际 sitemap，不添加无依据的爬虫限制。未增加伪造评价、关键词堆砌、隐藏答案或专用 AI 文本文件。

## 维护位置

- src/components/SeoHead.astro：公共搜索元信息和结构化数据。
- src/data/seo.ts：首页问答适配、站点身份和默认分享图。
- 企业站 src/components/HomeFaq.astro：可见问答；餐博会继续使用已有首页问答组件及数据。
- 企业站 scripts/sitemap.mjs：构建后生成地图；不要再手工修改发布产物中的 sitemap。
- scripts/verify_seo.py：核验元信息、JSON-LD、问答正文一致性、地图目标与站内资源。

修改问答应以已有公开资料为依据；展会时间、费用、名单和登记入口须核实。正文数据与 FAQ 标记共用来源。历史新闻不作为最新展期依据，不给尚未公布的事项编造答案。

## 验证与边界

执行 npm run typecheck、npm run build、python scripts/verify_seo.py；企业站另执行既有 scripts/verify.py。验证为静态内容检查，不等同于浏览器视觉检查、搜索引擎实际收录或富结果资格验证。

FAQPage 帮助表达问答关系，不承诺 Google FAQ 富结果。GEO 主要改善真实事实、回答内容与页面关系的可读性和可引用性，不保证 AI 引用或搜索排名。实时接口新闻如需可索引全文，后续需要按真实文章 URL 提供可抓取正文；当前详情壳页采用保守的不索引策略。

参考：
- [Google AI 搜索与网站](https://developers.google.com/search/docs/appearance/ai-features)
- [Google FAQ 展示限制](https://developers.google.com/search/blog/2023/08/howto-faq-changes)
- [Bing 网站指南](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a)


## 本次发布验证

四站已于2026-11-23发布至各自正式站点。服务器保留旧版本备份，完整产物已逐文件核对 SHA-256；公网首页、robots、sitemap 与构建产物一致，HTTP 跳转 HTTPS，未知页面返回404。本站发布没有修改 Nginx 配置或新闻服务。
