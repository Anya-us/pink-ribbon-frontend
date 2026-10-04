# DR 共用数据与模拟服务

版本：1。实现目录：src/mock/dr、src/services/dr。所有 fixture 对象为合成数据；原图示意明确标记 isSchematic。

## 实体与关联

| 集合 | 关键字段 |
| --- | --- |
| patients | id、currentExaminationId、institutionId、姓名、年龄、性别、糖尿病病程、HbA1c、血压、note、isSynthetic |
| examinations | id、patientId、institutionId、performedAt、sourceType、status、eyes.OD、eyes.OS |
| images | id、patientId、examinationId、eye、modality、capturedAt、deviceId、sourceType、fileName、previewUrl、quality |
| drafts | id、patientId、examinationId、status、modelVersion、eyeResults、disagreements、createdAt |
| reports | id、patientId、examinationId、draftId、status、version、signedBy、signedAt、eyeResults、conclusion、plan |
| tasks | id、patientId、examinationId、reportId、type、status、dueAt、note、updatedAt |
| reviewRecords | id、examinationId、reportId、actor、action、comment、createdAt |
| institutions / devices | 稳定 id、显示名称；设备另有 modality |

眼别统一使用 OD（右眼）、OS（左眼）；模态为 CFP、OCT。每眼保存 imageIds、quality、drGrade 和 dmeStatus。未评估等级为 null，不能映射为 0；DME 的 not_assessed 不能显示为阴性。

患者上的 cfp、oct、rightGrade、leftGrade、date、status 是兼容工作台的当前检查投影，不是独立检查。新增本地检查同时更新投影；历史结果从 examinations 读取，不根据当前等级计算。

## 状态

质控：passed、retake、ungradable、missing、pending、unknown_device、error。统一文案和语义色在 schema.js。

任务：preparing、self_reported、awaiting_signoff、pending_contact、reminded、scheduled、completed、overdue、lost。准备任务 type=preparation，可记录待准备和已自报状态；不能冒充正式随访。正式任务必须关联同一患者、同一检查的已签发报告。

当前检查状态包括 awaiting_collection、pending_quality、awaiting_review、signed。AI 草稿 status 为 ready 或 needs_review；签发报告 status=signed，须有签发人、时间和草稿引用。

## 浏览器服务接口

src/services/dr/index.js 导出 drService，接口返回 Promise，失败通过 rejected Promise 返回中文原因；读取结果为独立副本。共用选择器从同一响应式仓库读取，保证组件之间同步。

| 方法 | 参数与结果 |
| --- | --- |
| listPatients() | 全部合成患者 |
| getPatient(patientId) | 单个患者 |
| listExaminations(patientId) | 患者检查列表 |
| getExamination(patientId, examinationId?) | 患者、检查、机构、影像/设备、草稿、报告、任务与审核记录 |
| updatePatient(patientId, patch) | 更新允许的基础字段与备注，不修改关联编号 |
| createIntake(patientId, form, files) | 创建待质控检查，双眼候选等级为空；只登记文件元数据 |
| updateTask(taskId, patch) | 更新状态/备注，校验任务状态与任务类型 |
| getPatientService(patientId) | 仅该患者已签发报告及其正式任务 |
| getRegion() | 按机构汇总同一个仓库的检查、质控、审核、报告和正式任务 |

患者服务结果不包含 drafts，也不包含其他患者数据。页面选择器位于 selectors.js，集中组织历史记录、共识视角、准备/随访任务和区域汇总。

新增签发、退回与任务创建操作时，应扩展此服务，保持报告、检查和任务关联校验；不得在任务二、三页面再创建独立数据副本。

## 路由和刷新

需要病例的路由标记 meta.drContext。beforeResolve 校验 patientId 与 examinationId，缺失时填入选中对象。错误或不匹配编号进入 /404，并显示中文原因。选中信息和合成元数据在本地保存，显式 URL 编号优先于本地选择。

模拟元数据使用 localStorage 的 retina-dr-demo-v1，选择上下文使用 retina-dr-context-v1。读取先校验版本和关联；不可用或损坏时回退初始 fixture，仍可由有效 URL 恢复上下文。File 和 blob URL 只在当前会话的 files 中保留，绝不序列化到模拟仓库。

## HTTP 调试接口

根目录 mock 注册以下只读接口，开发时在 VUE_APP_BASE_API 前缀下访问：

- GET /dr/patients
- GET /dr/patient?patientId=…
- GET /dr/examinations?patientId=…
- GET /dr/examination?patientId=…&examinationId=…
- GET /dr/patient-service?patientId=…
- GET /dr/region

统一响应 { code: 20000, data }；错误 { code: 40000, message }。这些接口读取初始合成 fixture，专用于结构调试，不接受写入。页面的可写状态始终在浏览器服务内。未来若切换 HTTP 后端，须整体切换适配与状态同步，避免产生两个可写数据源。

## 初始数据

6 个患者、7 次检查、12 条逐眼影像记录、5 个草稿、2 个合成签发报告、14 个准备/随访任务、2 条审核记录、2 个机构与2个设备。新采集会增加检查与任务，不影响初始 fixture。

覆盖双眼不同等级、资料缺失、待复核、需重拍、已有签发记录及待联系/已完成随访。所有 DME 均未评估。
