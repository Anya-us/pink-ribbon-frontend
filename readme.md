# 糖网诊疗：DR 筛查与随访演示平台

面向算法创新赛的糖尿病视网膜病变（DR）筛查流程演示平台。项目采用 Vue 2、Vue CLI、Element UI 与本机 FastAPI 推理服务，覆盖患者档案、双眼采集、质控、研究模型草稿、医生审核签发，以及转诊随访等页面。

> 本项目是比赛演示软件，不是医疗器械或临床诊疗系统。仓库中的病例、机构、设备、报告和流程记录均为合成演示数据；页面中的研究模型结果必须经医生审核，不能直接作为诊断结论。

## 已实现内容

- 患者档案、检查列表，以及按右眼 / 左眼 / 时间组织的检查记录。
- 采集向导：确认患者与眼别、选择眼底彩照、登记设备与检查时间后提交。
- 质控状态：通过、需重拍、严重不可判读、设备未知，并提供对应原因与下一步建议。
- ICDR 候选等级、模态完整性、AI 草稿和人工复核提醒；没有 OCT 时固定显示“未提供 / 未评估”，不会确认 DME。
- 医生审核支持接受、修改、退回和签发，并保留医生、意见、修改原因和签发时间。
- 已签发报告才能流入患者服务与转诊随访页面。
- 仓库已内置 ResNet18 研究推理服务与相匹配的不确定性工件；返回内容仍以“研究模型草稿”展示，病灶证据未真实训练时会保留“演示草稿 / 未提供”标记。

## 页面入口

| 页面 | 路由 |
| --- | --- |
| 诊疗工作台 | `/dashboard` |
| 患者档案 | `/patients/index` |
| 筛查采集 | `/screening/intake` |
| 质控与共识草稿 | `/screening/consensus` |
| 双眼分级与证据 | `/screening/evidence` |
| 医生审核 | `/review/index` |
| 转诊与随访 | `/followup/index` |
| 患者服务 | `/patient/index` |
| 区域看板 | `/region/index` |

登录演示账号：`admin` 或 `editor`；密码：`111111`。

## 一键启动

建议安装 Node.js 20 LTS（当前也已验证 Node.js 24 可用）以及 Python 3.10 或更高版本。首次启动会自动创建 Python 虚拟环境、安装推理依赖与前端依赖，因此时间会稍长；之后会快很多。

在 Windows 资源管理器中双击：

```text
启动演示.cmd
```

或者在项目根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\start-demo.ps1
```

脚本会打开一个推理服务窗口，并在当前窗口启动前端。前端启动后按终端显示的地址访问即可。关闭前端窗口会结束页面服务；推理服务窗口可单独关闭。

## 仅启动前端

如只需查看合成演示流程，不需要新图片的实际研究推理，可单独启动前端：

```powershell
npm ci
npm run dev
```

默认启动后按终端显示的地址访问。生产构建可运行：

```powershell
npm run build:prod
```

## 研究推理服务

`inference-backend/` 已包含一套可在本机运行的 ResNet18 研究推理服务、模型权重与运行所需的不确定性工件。使用一键启动即可同时打开前端和推理服务；也可以单独运行：

```powershell
cd inference-backend
.\start-inference.ps1
```

后端默认运行在 `http://127.0.0.1:8000`，前端会自动连接它。如后端地址不同，请将 `.env.example` 复制为 `.env.local`，再填写：

```ini
VUE_APP_DR_API_BASE_URL=http://127.0.0.1:8000
```

`.env.local` 已被忽略，不会上传到 GitHub。推理服务未启动时，前端仍可继续使用合成演示流程；它不会把失败情况伪装成模型结果。

## 给队友的协作方式

这是一个可独立运行的单仓库：队友拉取后不需要再单独取得“算法创新7”。首次运行 `启动演示.cmd` 即可安装依赖并启动界面与研究推理服务。

推荐团队将 GitHub 仓库设为私有，并把下面内容排除在提交之外：

- `node_modules`、`dist`、测试覆盖率和运行日志；
- `.env.local`、密码、密钥和任何本机配置；
- 数据库、上传目录、真实患者图像、真实报告及可识别个人信息；
- 模型训练数据集。

本仓库包含一个约 45MB 的研究模型权重，便于比赛协作；请保持仓库私有，且不要加入训练数据、真实患者信息或额外模型。模型输出仅供研究和竞赛演示，不能作为临床结论。

首次上传前，请检查将要提交的文件：

```powershell
git status
git add .
git commit -m "feat: 完成 DR 筛查与审核演示流程"
git push
```

如果需要改为新的 GitHub 仓库地址，请先在 GitHub 创建空仓库，再执行：

```powershell
git remote set-url origin <你的新仓库地址>
git push -u origin main
```

## 项目结构

```text
inference-backend/        本机研究推理服务、模型权重和不确定性工件
├─ backend/app/          FastAPI 接口与 ResNet18 推理逻辑
└─ artifacts/            运行所需模型权重和严格拆分工件
src/
├─ components/dr/        DR 共用组件：患者信息、眼别、质控、时间线等
├─ data/retina-demo.js   既有页面的兼容数据入口
├─ mock/dr/              合成病例和浏览器模拟仓库
├─ services/dr/          页面选择器、状态服务和研究推理接口
└─ views/
   ├─ patients/          患者档案
   ├─ prediction/        采集、质控、证据页面
   └─ review/            医生审核与签发
start-demo.ps1            前端与推理服务的一键启动脚本
启动演示.cmd               双击启动入口
```

更多字段说明见 [DR 数据与服务约定](docs/dr-data-contract.md)。
