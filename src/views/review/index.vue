<template>
  <main class="clinical-page">
    <clinical-header title="医生审核" description="核对双眼影像、质控结果和候选草稿，查看人工审核记录。"><el-button icon="el-icon-upload2" @click="$router.push({ path: '/screening/intake', query: $route.query })">补全采集资料</el-button></clinical-header>
    <demo-notice text="当前显示合成检查与审核记录，仅用于流程演示。候选草稿与已签发示例分别展示。" />
    <patient-bar />
    <div class="two-column">
      <image-preview :examination="bundle.examination" :images="bundle.images" :files="files" :institution="bundle.institution.name" />
      <section class="panel"><div class="panel-heading"><h2>{{ report ? '已签发合成报告' : '待审核的候选草稿' }}</h2><span class="status-pill" :class="report ? 'success' : 'warning'">{{ report ? '合成签发示例' : '未签发' }}</span></div><div class="panel-body"><div v-for="eye in eyes" :key="eye" class="dr-review-eye"><h3>{{ eye === 'OD' ? '右眼 OD' : '左眼 OS' }}</h3><quality-status :status="bundle.examination.eyes[eye].quality.status" :reason="bundle.examination.eyes[eye].quality.reason" show-reason /><dl class="review-fields"><div><dt>{{ report ? '报告等级' : '候选等级' }}</dt><dd>{{ gradeInfo(results[eye].drGrade).label }}</dd></div><div><dt>黄斑水肿</dt><dd>未评估</dd></div></dl></div><p v-if="!bundle.draft" class="muted">该检查尚无候选草稿，请先完成资料采集与质量确认。</p><p v-if="bundle.draft && bundle.draft.disagreements.length" class="review-disagreement">{{ bundle.draft.disagreements.join('；') }}</p><div v-if="report" class="review-signature"><strong>{{ report.id }}</strong><p>{{ report.signedBy }} · {{ report.signedAt.slice(0, 16).replace('T', ' ') }} · 版本 {{ report.version }}</p><p>{{ report.conclusion }}</p></div><router-link class="text-link" :to="{ path: '/screening/consensus', query: $route.query }">查看质控与共识草稿 <i class="el-icon-right" /></router-link></div></section>
    </div>
    <review-history class="section-gap" :records="bundle.reviewRecords" />
  </main>
</template>
<script>
import ClinicalHeader from '@/components/ClinicalHeader'
import DemoNotice from '@/components/DemoNotice'
import PatientBar from '@/components/dr/PatientBar'
import ImagePreview from '@/components/dr/ImagePreview'
import QualityStatus from '@/components/dr/QualityStatus'
import ReviewHistory from '@/components/dr/ReviewHistory'
import { currentBundle, demoState, gradeInfo } from '@/data/retina-demo'
export default { name: 'DoctorReview', components: { ClinicalHeader, DemoNotice, PatientBar, ImagePreview, QualityStatus, ReviewHistory }, data() { return { eyes: ['OD', 'OS'] } }, computed: { bundle: currentBundle, files() { return this.bundle.examination.sourceType === 'local' ? demoState.files : {} }, report() { return this.bundle.reports.find(item => item.status === 'signed') }, results() { return this.report ? this.report.eyeResults : this.bundle.draft ? this.bundle.draft.eyeResults : this.bundle.examination.eyes } }, methods: { gradeInfo }}
</script>
<style scoped>
.dr-review-eye + .dr-review-eye { margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border); }
.dr-review-eye h3 { font-size: 16px; margin: 0 0 12px; }
.review-fields { margin: 16px 0; font-size: 13px; }
.review-fields > div { display: flex; justify-content: space-between; gap: 12px; margin: 8px 0; }
.review-fields dt { color: var(--muted); }
.review-fields dd { margin: 0; color: var(--heading); }
.review-signature { padding: 16px; background: var(--primary-soft); border-radius: 8px; margin: 20px 0; overflow-wrap: anywhere; font-size: 13px; }
.review-signature p { margin: 6px 0; }
.review-disagreement { color: var(--warning); background: var(--warning-soft); padding: 12px; border-radius: 6px; font-size: 13px; }
</style>
