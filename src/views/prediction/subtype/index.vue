<template>
  <main class="clinical-page evidence-page">
    <clinical-header title="双眼分级与证据" description="将眼别、影像来源与候选结论放在一起，方便逐项复核。">
      <el-button icon="el-icon-printer" @click="printDraft">打印演示草稿</el-button>
      <el-button type="primary" icon="el-icon-connection" @click="$router.push('/screening/consensus')">返回共识评估</el-button>
    </clinical-header>
    <demo-notice :text="custom ? '本次选择的影像未进行推理，所有候选分级保持未评估。影像仅作原图预览。' : '下方分级为预置演示草稿，未附病例原图，未由医生签发；不能作为实际诊疗报告。'" />
    <div class="print-only">糖网诊疗 · 演示草稿 · 未签发 · 不作为实际诊疗报告</div>
    <patient-strip />
    <div class="two-column">
      <eye-evidence />
      <section class="panel">
        <div class="panel-heading"><h2>候选评估摘要</h2><span class="status-pill warning">待复核</span></div>
        <div class="grade-summaries">
          <div v-for="eye in eyes" :key="eye.label" class="grade-summary">
            <div class="grade-eye-heading"><strong>{{ eye.label }}</strong><span class="status-pill" :class="gradeInfo(eye.grade).tone">{{ gradeInfo(eye.grade).short }}</span></div>
            <dl><div><dt>DR 候选分级</dt><dd>{{ gradeInfo(eye.grade).label }}</dd></div><div><dt>DME</dt><dd>未评估</dd></div><div><dt>证据来源</dt><dd>{{ custom ? '本地选择 · 未推理' : '合成演示草稿' }}</dd></div></dl>
          </div>
        </div>
        <div class="signature-state"><i class="el-icon-document-checked" /><div><strong>{{ report ? '合成报告已签发' : '医生签发：未完成' }}</strong><p>{{ report ? report.id + ' · ' + report.signedBy : '报告编号、签名与处置建议待医生确认。' }}</p></div></div>
      </section>
    </div>
    <section class="panel section-gap">
      <div class="panel-heading"><div><h2>DR 分级索引</h2><p>分级标签用于统一记录；实际分级由影像评估及医生复核确定。</p></div><span class="muted small-text">ICDR 五级</span></div>
      <div class="grade-reference">
        <div v-for="grade in grades" :key="grade.code" class="grade-reference-item" :class="grade.tone"><span class="grade-index">{{ grade.code }}</span><strong>{{ grade.label }}</strong><small>{{ grade.short }}</small></div>
      </div>
      <div class="reference-foot"><span class="status-pill">未评估</span><span>单独记录，不能映射为 0 级或“无明显 DR”。</span></div>
    </section>
    <section class="evidence-checks section-gap">
      <div><i class="el-icon-view" /><strong>保持原始影像</strong><span>不改变图像颜色，不在示意图上生成病灶标注。</span></div>
      <div><i class="el-icon-document-copy" /><strong>分别记录双眼</strong><span>右眼 OD 与左眼 OS 独立展示和复核。</span></div>
      <div><i class="el-icon-edit-outline" /><strong>保留人工确认</strong><span>共识草稿与医生签发报告状态分开呈现。</span></div>
    </section>
  </main>
</template>
<script>
import ClinicalHeader from '@/components/ClinicalHeader'
import DemoNotice from '@/components/DemoNotice'
import PatientStrip from '@/components/PatientStrip'
import EyeEvidence from '@/components/EyeEvidence'
import { assessmentView } from '@/services/dr/selectors'
import { demoState, gradeInfo, grades, currentBundle } from '@/data/retina-demo'
export default {
  name: 'Subtype',
  components: { ClinicalHeader, DemoNotice, PatientStrip, EyeEvidence },
  data() { return { grades } },
  computed: {
    patient() { return demoState.patient },
    custom() { return !!demoState.intake || Object.keys(demoState.files).length > 0 },
    bundle: currentBundle,
    report() { return this.bundle.reports.find(item => item.status === 'signed') },
    eyes() { return assessmentView(this.bundle, this.custom).eyes.map(eye => ({ label: eye.label + ' ' + eye.abbr, grade: eye.grade })) }
  },
  methods: { gradeInfo, printDraft() { window.print() } }
}
</script>
<style scoped>
.grade-summaries { padding: 0 24px; }
.grade-summary { padding: 20px 0; border-bottom: 1px solid var(--border); }
.grade-summary:last-child { border-bottom: 0; }
.grade-eye-heading { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.grade-eye-heading strong { font-size: 15px; color: var(--primary); }
.grade-summary dl { margin: 14px 0 0; font-size: 12px; }
.grade-summary dl > div { display: flex; gap: 16px; justify-content: space-between; margin-top: 8px; }
.grade-summary dt { color: var(--muted); }
.grade-summary dd { margin: 0; color: var(--heading); text-align: right; }
.signature-state { border-top: 1px solid var(--border); background: #F6F9F7; padding: 18px 24px; display: flex; gap: 12px; align-items: center; }
.signature-state i { font-size: 25px; color: var(--input-border); }
.signature-state strong { font-size: 13px; font-weight: 500; }
.signature-state p { margin: 3px 0 0; font-size: 12px; color: var(--muted); }
.grade-reference { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); padding: 24px; gap: 14px; }
.grade-reference-item { border-left: 3px solid var(--border); padding-left: 14px; }
.grade-reference-item.success { border-color: var(--success); }
.grade-reference-item.info { border-color: var(--blue); }
.grade-reference-item.warning { border-color: var(--warning); }
.grade-reference-item.danger { border-color: var(--danger); }
.grade-index { color: var(--muted); font-size: 11px; }
.grade-reference-item strong { display: block; font-size: 14px; color: var(--heading); margin: 6px 0 4px; font-weight: 500; }
.grade-reference-item small { font-size: 11px; color: var(--muted); }
.reference-foot { display: flex; gap: 12px; align-items: center; padding: 13px 24px; background: #F6F9F7; border-top: 1px solid var(--border); font-size: 12px; color: var(--muted); }
.evidence-checks { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; padding: 8px 0; }
.evidence-checks > div { display: grid; grid-template-columns: 25px 1fr; column-gap: 8px; }
.evidence-checks i { color: var(--primary); font-size: 19px; grid-row: span 2; margin-top: 2px; }
.evidence-checks strong { font-size: 13px; font-weight: 500; }
.evidence-checks span { color: var(--muted); font-size: 12px; margin-top: 4px; }
@media (max-width: 1100px) { .evidence-page .two-column { grid-template-columns: minmax(0, 1fr); } .grade-summaries { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px; } .grade-summary:first-child { border-bottom: 0; } }
@media (max-width: 767px) {
  .grade-reference { grid-template-columns: repeat(2, minmax(0, 1fr)); padding: 20px; gap: 22px; }
  .grade-summaries { display: block; }
  .grade-summary:first-child { border-bottom: 1px solid var(--border); }
  .evidence-checks { grid-template-columns: minmax(0, 1fr); gap: 20px; }
  .reference-foot { align-items: flex-start; }
}
</style>
