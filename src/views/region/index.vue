<template>
  <main class="clinical-page">
    <clinical-header title="区域看板" description="按机构查看筛查、质量确认、审核和随访进度。" />
    <demo-notice text="所有统计由同一批合成检查、报告和任务汇总，机构为演示名称。" />
    <section class="panel"><div class="region-totals"><div><span>演示患者</span><strong>{{ totals.patients }}<small>人</small></strong></div><div><span>检查记录</span><strong>{{ totals.examinations }}<small>次</small></strong></div><div><span>待医生审核</span><strong>{{ totals.awaitingReview }}<small>次</small></strong></div><div><span>待执行随访</span><strong>{{ totals.openTasks }}<small>项</small></strong></div><div><span>患者已确认提醒</span><strong>{{ totals.patientConfirmed }}<small>项</small></strong></div><div><span>逾期 / 失访</span><strong>{{ totals.overdueOrLost }}<small>项</small></strong></div></div></section>
    <section class="panel section-gap"><div class="panel-heading"><div><h2>机构筛查与随访进度</h2><p>检查总数包含历史检查；质控通过按双眼均通过计数；随访状态只统计关联已签发报告的正式任务。</p></div></div><div class="table-scroll"><table class="clinical-table"><thead><tr><th scope="col">机构</th><th scope="col">患者</th><th scope="col">检查</th><th scope="col">双眼质控通过</th><th scope="col">需重拍 / 不可判读</th><th scope="col">待审核</th><th scope="col">已签发报告</th><th scope="col">待联系</th><th scope="col">已提醒</th><th scope="col">已预约</th><th scope="col">逾期 / 失访</th><th scope="col">患者已确认</th><th scope="col">已收到反馈</th><th scope="col">待执行</th><th scope="col">已完成</th></tr></thead><tbody><tr v-for="row in rows" :key="row.id"><td class="name-cell">{{ row.name }}</td><td>{{ row.patients }}</td><td>{{ row.examinations }}</td><td>{{ row.qualityPassed }}</td><td>{{ row.retake }}</td><td>{{ row.awaitingReview }}</td><td>{{ row.signedReports }}</td><td>{{ row.pendingContact }}</td><td>{{ row.reminded }}</td><td>{{ row.scheduled }}</td><td>{{ row.overdueOrLost }}</td><td>{{ row.patientConfirmed }}</td><td>{{ row.feedbackReceived }}</td><td>{{ row.openTasks }}</td><td>{{ row.completedTasks }}</td></tr></tbody></table></div></section>
    <section class="panel section-gap"><div class="panel-heading"><h2>统计口径</h2></div><div class="panel-body region-notes"><p>待审核：检查状态为等待医生审核；已签发：报告具有签发人和签发时间。</p><p>随访状态：来自已签发报告关联任务，分别统计待联系、已提醒、已预约、逾期 / 失访和已完成。</p><p>患者已确认与已收到反馈：分别按患者服务页提交的提醒确认时间和反馈时间统计。</p><p>所有数字从同一份本地演示数据汇总，不包含准备清单，也不代表真实机构或临床效果。</p></div></section>
  </main>
</template>
<script>
import ClinicalHeader from '@/components/ClinicalHeader'
import DemoNotice from '@/components/DemoNotice'
import { regionView } from '@/services/dr/selectors'
export default { name: 'RegionDashboard', components: { ClinicalHeader, DemoNotice }, computed: { rows: regionView, totals() { return this.rows.reduce((total, row) => { Object.keys(total).forEach(key => { total[key] += row[key] }); return total }, { patients: 0, examinations: 0, awaitingReview: 0, openTasks: 0, patientConfirmed: 0, overdueOrLost: 0 }) } }}
</script>
<style scoped>
.region-totals { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); padding: 24px; gap: 24px; }
.region-totals > div { display: flex; flex-direction: column; gap: 12px; color: var(--muted); }
.region-totals strong { color: var(--heading); font-size: 30px; font-weight: 600; }
.region-totals small { font-size: 12px; margin-left: 8px; color: var(--muted); font-weight: 400; }
.region-notes p { margin: 0 0 8px; font-size: 13px; color: var(--muted); }
@media (max-width: 1000px) { .region-totals { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; } }
@media (max-width: 767px) { .region-totals { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; } }
</style>
