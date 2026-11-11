# 海名·济南餐博会官网

独立项目：F:\信展官网\济南餐博会\官网项目。正式网站：https://csce.hm-d.cn 。未改动沈阳官网及展商展品分支。沿用既有 Astro 静态站、事实有来源、不制作假表单、发布前验收、备份与回滚的约定。

## 使用

Node.js 22.12+。首次运行 `npm ci`，随后 `npm run dev`，本地 http://127.0.0.1:4326/ 。
`npm run typecheck` 检查类型；`npm run build` 生成 dist。部署时仅上传 dist 内容。

## 内容维护

- 基础信息、电话、展品范围、FAQ：src/data/event.ts。
- 页面：src/pages；共享导航、SEO 和结构化数据：src/layouts/Base.astro；样式：src/styles/global.css。
- 图片本地存储在 public/images；原始来源见 docs/图片来源.json。
- 观众登记已按用户指定URL统一接入，唯一配置源为 src/data/event.ts 的 event.registration，保留全部参数与 #/index。
- 新闻恢复旧站50条展会资讯与5条行业动态；微信保留外链，可读站内历史文章文字整理为archive页面。菜单与素材取舍见 docs/菜单与首页调整记录.md。

## SEO / GEO

静态输出正文、独立标题描述、canonical、Open Graph、Event/Organization JSON-LD、站点地图和 robots。语义标题、文字展品分类与问答便于检索和机器理解，不能保证搜索排名或AI引用。正式域名为 csce.hm-d.cn。

## 发布

用户已授权发布到118.89.192.96的独立站点csce.hm-d.cn。原站www.hmjncbh.com保持原状；部署脚本见scripts/deploy_server.py，运维记录见docs/服务器部署说明.md。更新前备份本站与Nginx配置，按 docs/旧地址迁移.conf 检查301规则。原文章页不得批量跳转首页；有价值文章后续迁移正文或保持原地址服务。删除空页可使用410，不能全部重定向到无关页面。

## 仓库

- GitHub：https://github.com/Nadiamaxreed/CSCE
- Gitee：https://gitee.com/nadia20109/csce
- main为正式源码分支；推送代码与服务器发布分开操作。
- research为本地采集及截图临时目录，不提交；源码、网站图片、维护与发布文档一并管理。
