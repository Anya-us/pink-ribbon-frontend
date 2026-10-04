<template>
  <main class="clinical-page">
    <clinical-header title="质控与共识草稿" description="汇集不同评估视角，呈现证据、缺失信息与待复核事项。">
      <el-button icon="el-icon-upload2" @click="$router.push('/screening/intake')">补全资料</el-button>
      <el-button type="primary" icon="el-icon-document" @click="$router.push('/screening/evidence')">查看双眼证据</el-button>
    </clinical-header>
    <demo-notice :text="custom ? '当前只记录了本地资料，未调用模型，因此没有 AI 结论。可切换演示病例查看页面结构。' : '以下共识内容来自预置示例，不是对上传影像的实际推理；全部为未签发的演示草稿。'" />
    <patient-strip />
    <section class="review-progress panel">
      <div v-for="(stage, index) in stages" :key="stage.title" class="review-stage" :class="{ ready: stage.ready }"><span class="stage-index"><i v-if="stage.ready" class="el-icon-check" /><template v-else>{{ index + 1 }}</template></span><div><strong>{{ stage.title }}</strong><small>{{ stage.description }}</small></div><i v-if="index < stages.length - 1" class="el-icon-arrow-right stage-arrow" /></div>
    </section>

    <div class="two-column section-gap">
      <section class="panel">
        <div class="panel-heading"><div><h2>双眼 DR 候选分级</h2><p>{{ custom ? '尚未完成模型推理' : '合成病例中的候选分级，与签发报告分别记录' }}</p></div><span class="status-pill warning">草稿</span></div>
        <div class="bilateral-summary">
          <div v-for="eye in eyes" :key="eye.key" class="summary-eye">
            <span class="eye-abbr">{{ eye.abbr }}</span><span class="muted small-text">{{ eye.label }}</span>
            <h3>{{ gradeInfo(eye.grade).label }}</h3><span class="status-pill" :class="gradeInfo(eye.grade).tone">{{ eye.grade == null ? '资料 / 评估未完成' : '演示候选 · 待复核' }}</span>
            <quality-status :status="bundle.examination.eyes[eye.abbr].quality.status" /><div class="eye-meta"><span>黄斑水肿 DME</span><strong>未评估</strong></div>
          </div>
        </div>
        <div class="consensus-foot"><i class="el-icon-info" />DR 分级、DME 与长期风险分别评估；当前不提供长期风险评分。</div>
      </section>
      <section class="panel">
        <div class="panel-heading"><h2>需要医生关注</h2><span class="status-pill warning">待复核</span></div>
        <ul class="review-points">
          <li><span class="point-dot" /><div><strong>{{ custom ? '本次影像尚未进行质量检查' : hasCfp ? '复核双眼候选分级与原始影像' : '眼底彩照尚未提供' }}</strong><p>图像质量与诊断分级需要独立确认。</p></div></li>
          <li><span class="point-dot blue" /><div><strong>{{ hasOct ? 'OCT 待判读，DME 保持未评估' : 'OCT 缺失，DME 保持未评估' }}</strong><p>资料缺失不会自动转为阴性或正常。</p></div></li>
          <li><span class="point-dot neutral" /><div><strong>{{ report ? '当前检查已有合成签发记录' : '报告尚未由医生签发' }}</strong><p>共识草稿与签发报告分开存档，处置任务关联签发报告。</p></div></li>
        </ul>
        <div v-if="custom" class="demo-case-action"><el-button type="text" @click="loadDemo">切换到预置演示病例 <i class="el-icon-right" /></el-button><p>将清除本次选择的文件。</p></div>
      </section>
    </div>

    <section class="panel section-gap">
      <div class="panel-heading"><div><h2>六个评估视角</h2><p>各视角的证据与可用性分别呈现，不以多数意见替代医生判读。</p></div><span class="status-pill info">{{ custom ? '未调用模型' : '演示共识草稿' }}</span></div>
      <div class="agent-grid">
        <article v-for="agent in agents" :key="agent.number" class="agent-item">
          <div class="agent-title"><span class="agent-number">{{ agent.number }}</span><h3>{{ agent.name }}</h3><span class="status-pill" :class="agent.tone">{{ agent.status }}</span></div>
          <p>{{ agent.description }}</p>
          <div class="agent-result"><span>当前输出</span><strong>{{ agent.result }}</strong></div>
        </article>
      </div>
    </section>
    <div class="review-end"><i class="el-icon-document-checked" /><span>共识草稿 → 医生复核 → 报告签发 → 随访任务</span><router-link class="text-link" to="/followup/index">查看处置与随访 <i class="el-icon-right" /></router-link></div>
  </main>
</template>
<script>
import ClinicalHeader from '@/components/ClinicalHeader'
import DemoNotice from '@/components/DemoNotice'
import PatientStrip from '@/components/PatientStrip'
import { assessmentView } from '@/services/dr/selectors'
import QualityStatus from '@/components/dr/QualityStatus'
import { demoState, patients, selectPatient, gradeInfo, currentBundle } from '@/data/retina-demo'
export default {
  name: 'Assess',
  components: { ClinicalHeader, DemoNotice, PatientStrip, QualityStatus },
  computed: {
    patient() { return demoState.patient },
    custom() { return !!demoState.intake || Object.keys(demoState.files).length > 0 },
    hasCfp() { return this.bundle.images.some(item => item.modality === 'CFP') || !!(demoState.files.rightCfp || demoState.files.leftCfp) },
    hasOct() { return this.bundle.images.some(item => item.modality === 'OCT') || !!(demoState.files.rightOct || demoState.files.leftOct) },
    bundle: currentBundle,
    report() { return this.bundle.reports.find(item => item.status === 'signed') },
    assessment() { return assessmentView(this.bundle, this.custom) },
    eyes() { return this.assessment.eyes },
    stages() { return this.assessment.stages },
    agents() { return this.assessment.agents }
  },
  methods: {
    gradeInfo,
    loadDemo() { selectPatient(patients[0]); this.$message.info('已切换到预置演示病例，本次文件已清除。') }
  }
}
</script>
<style scoped>
.review-progress { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); padding: 20px 24px; gap: 18px; }
.review-stage { display: flex; gap: 12px; align-items: center; min-width: 0; }
.stage-index { display: grid; place-items: center; flex-shrink: 0; width: 30px; height: 30px; background: #EDF1F0; color: var(--muted); border: 1px solid var(--border); border-radius: 50%; font-size: 13px; }
.ready .stage-index { color: var(--primary); background: var(--primary-soft); border-color: #B5D1C3; }
.review-stage strong { font-size: 14px; font-weight: 500; display: block; }
.review-stage small { display: block; color: var(--muted); font-size: 11px; margin-top: 3px; }
.stage-arrow { margin-left: auto; color: var(--input-border); font-size: 12px; }
.bilateral-summary { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.summary-eye { padding: 24px; }
.summary-eye + .summary-eye { border-left: 1px solid var(--border); }
.eye-abbr { font-size: 13px; font-weight: 600; color: var(--primary); margin-right: 7px; }
.summary-eye h3 { font-size: 23px; font-weight: 600; margin: 13px 0 10px; }
.eye-meta { display: flex; gap: 10px; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); margin-top: 24px; padding-top: 16px; font-size: 12px; color: var(--muted); }
.eye-meta strong { font-weight: 500; }
.consensus-foot { border-top: 1px solid var(--border); font-size: 12px; color: var(--muted); padding: 13px 24px; }
.consensus-foot i { margin-right: 6px; }
.review-points { list-style: none; margin: 0; padding: 7px 24px; }
.review-points li { display: flex; gap: 10px; padding: 14px 0; border-bottom: 1px solid #E7EEEB; }
.review-points li:last-child { border-bottom: 0; }
.point-dot { width: 6px; height: 6px; flex-shrink: 0; margin-top: 8px; background: var(--warning); border-radius: 50%; }
.point-dot.blue { background: var(--blue); }
.point-dot.neutral { background: var(--muted); }
.review-points strong { font-size: 13px; font-weight: 500; color: var(--heading); }
.review-points p { margin: 4px 0 0; font-size: 12px; color: var(--muted); }
.demo-case-action { margin: 0 24px 18px; }
.demo-case-action p { margin: 0; font-size: 12px; color: var(--muted); }
.agent-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); }
.agent-item { padding: 22px 24px; border-right: 1px solid var(--border); border-bottom: 1px solid var(--border); }
.agent-item:nth-child(3n) { border-right: 0; }
.agent-item:nth-child(n+4) { border-bottom: 0; }
.agent-title { display: flex; align-items: center; gap: 9px; flex-wrap: wrap; }
.agent-title h3 { font-size: 15px; font-weight: 600; margin: 0; }
.agent-title .status-pill { margin-left: auto; }
.agent-number { color: var(--input-border); font-size: 12px; }
.agent-item > p { color: var(--muted); font-size: 12px; margin: 13px 0 18px; }
.agent-result { padding: 10px 12px; background: #F4F7F6; border-radius: 5px; }
.agent-result > span { font-size: 11px; color: var(--muted); display: block; margin-bottom: 4px; }
.agent-result strong { font-size: 12px; color: var(--heading); font-weight: 500; }
.review-end { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; padding: 20px 0 0; font-size: 13px; color: var(--muted); }
.review-end > i { font-size: 18px; color: var(--primary); }
.review-end .text-link { margin-left: auto; }
@media (max-width: 1100px) {
  .review-progress { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .agent-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .agent-item:nth-child(n) { border-right: 1px solid var(--border); border-bottom: 1px solid var(--border); }
  .agent-item:nth-child(2n) { border-right: 0; }
  .agent-item:nth-last-child(-n+2) { border-bottom: 0; }
}
@media (max-width: 767px) {
  .review-progress { padding: 18px; }
  .stage-arrow { display: none; }
  .bilateral-summary { grid-template-columns: minmax(0, 1fr); }
  .summary-eye { padding: 20px; }
  .summary-eye + .summary-eye { border-left: 0; border-top: 1px solid var(--border); }
  .agent-grid { grid-template-columns: minmax(0, 1fr); }
  .agent-item:nth-child(n) { border-right: 0; border-bottom: 1px solid var(--border); }
  .agent-item:last-child { border-bottom: 0; }
  .review-end .text-link { margin-left: 0; }
}
</style>
