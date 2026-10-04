# 糖网诊疗 · 多模态筛查与管理

基于 Vue 2、Vue CLI、Element UI 的糖尿病视网膜病变筛查演示前端。当前采用青绿色后台、浅色页面与微软雅黑；登录页使用本地真实眼科场景照片与连续轮换。

## 当前实施状态

任务一的前端底座已补齐：七类业务入口、统一合成数据、八类共用组件、DR 模拟服务和患者/检查路由上下文。任务二、三可继续在同一批数据和服务上实现完整审核签发及随访交互。

验收结果见 [任务一补齐验收](docs/design-review/2026-10-04-任务一补齐验收.md)。

- 医生审核页已展示双眼质控、候选等级、合成签发示例和审核记录，尚未实现用户接受、修改、退回和新签发操作。
- 患者服务页只展示当前患者已签发的合成报告及其关联计划。
- 区域看板从同一批检查、报告和正式任务汇总，不展示模型准确率。
- 采集文件只在当前浏览器选择和预览，不上传、不推理；文件内容和 blob URL 不保存。
- 合成档案与任务编辑保存在当前浏览器；病例与检查通过 URL 编号恢复。原图预览和对话刷新后不保留。

本项目不包含真实诊疗模型、临床签发或多人权限后端。所有病例、机构、设备、候选分级、质控和签发记录均明确标记为合成演示数据。

## 页面入口

| 页面 | 路由 |
| --- | --- |
| 诊疗工作台 | /dashboard |
| 患者档案 | /patients/index |
| 筛查采集 | /screening/intake |
| 质控与共识草稿 | /screening/consensus |
| 双眼分级与证据 | /screening/evidence |
| 医生审核 | /review/index |
| 转诊与随访 | /followup/index |
| 患者服务 | /patient/index |
| 区域看板 | /region/index |
| 流程帮助 | /patient/help |

业务页面通过 patientId 与 examinationId 查询参数定位对象，例如：

`/#/review/index?patientId=DR-202610-004&examinationId=EX-202610-004`

省略编号时补入当前选中对象；无效或不匹配的编号进入异常页。旧 personal、prediction、advice 和 chat 链接通过隐藏重定向保持兼容，不再出现在菜单中。

## 数据与组件

- src/mock/dr/：确定性合成数据、状态枚举和纯 JavaScript 模拟仓库。
- src/services/dr/：共用响应式数据、异步服务接口和页面选择器。
- src/data/retina-demo.js：既有页面的兼容 facade，读取同一个仓库。
- src/components/dr/：患者栏、左右眼切换、图片预览、来源/设备标签、质控状态、审核记录、检查时间线和任务状态。
- src/router/modules/dr.js：DR 业务路由。
- mock/dr.js：初始合成数据的只读 HTTP 调试接口。页面实际读写统一使用浏览器模拟服务，HTTP 调试数据不随浏览器编辑变化。

字段、服务签名和持久化约定见 [DR 数据与服务约定](docs/dr-data-contract.md)。八类共用组件允许继续复用或扩展，页面不再独立构造病例、历史检查或任务数组。

## 本地运行

- 安装依赖：`npm ci`
- 启动：`npm run dev -- --port 19527`
- 生产构建：`npm run build:prod`
- 单元测试：`node node_modules/@vue/cli-service/bin/vue-cli-service.js test:unit --runInBand --watchAll=false`

演示账户：用户名 admin 或 editor，密码 111111。

登录照片来源记录在 public/images/login/SOURCES.md。业务查看器中的眼底 SVG 是明确标记的合成结构示意，不能作为真实眼底图或诊断证据。
