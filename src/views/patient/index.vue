<template>
  <main class="clinical-page">
    <clinical-header title="患者服务" description="查看已签发报告和已确认计划，准备复查所需资料。"><router-link class="text-link" :to="{ path: '/patient/help', query: $route.query }">了解筛查与报告流程 <i class="el-icon-right" /></router-link></clinical-header>
    <demo-notice text="本页为合成患者服务示例，只展示当前患者已签发的报告与关联计划。" />
    <patient-bar />
    <section v-if="!portal.reports.length" class="panel empty-state"><i class="el-icon-document" /><h3>暂无已签发报告</h3><p>完成医生审核后，签发报告和确认计划将显示在这里。</p><p>候选草稿不会出现在患者服务页。</p></section>
    <section v-for="report in portal.reports" :key="report.id" class="panel section-gap"><div class="panel-heading"><div><h2>已签发报告</h2><p>{{ report.signedAt.slice(0, 10) }} · {{ report.examinationId }}</p></div><span class="status-pill success">合成签发示例</span></div><div class="panel-body"><dl class="detail-grid"><div><dt>右眼 OD</dt><dd>{{ gradeInfo(report.eyeResults.OD.drGrade).label }}</dd></div><div><dt>左眼 OS</dt><dd>{{ gradeInfo(report.eyeResults.OS.drGrade).label }}</dd></div><div><dt>黄斑水肿</dt><dd>未评估</dd></div><div><dt>报告编号</dt><dd>{{ report.id }}</dd></div><div><dt>签发人</dt><dd>{{ report.signedBy }}</dd></div><div><dt>版本</dt><dd>{{ report.version }}</dd></div></dl><p class="patient-conclusion">{{ report.conclusion }}</p><p class="muted">{{ report.plan }}</p></div></section>
    <section v-if="portal.tasks.length" class="panel section-gap"><div class="panel-heading"><div><h2>已签发报告关联计划</h2><p>只展示医生已签发报告中的安排；患者确认与反馈为本地演示记录。</p></div><span class="muted small-text">{{ portal.tasks.length }} 项</span></div><ul class="patient-plans"><li v-for="task in portal.tasks" :key="task.id"><div class="patient-plan-main"><div class="patient-plan-heading"><h3>{{ task.title }}</h3><task-status :status="task.status" /></div><p class="plan-date">{{ task.dueAt || '日期待医生确认' }} · 报告 {{ task.reportId }}</p><p class="plan-copy">{{ task.plan || task.description || linkedReport(task.reportId).plan }}</p><p v-if="task.patientConfirmedAt" class="patient-action-state"><i class="el-icon-circle-check" /> 已于 {{ formatTime(task.patientConfirmedAt) }} 确认收到提醒</p><p v-if="task.patientFeedback" class="patient-action-state"><i class="el-icon-chat-line-round" /> 已提交反馈：{{ task.patientFeedback }} <span v-if="task.patientFeedbackAt">（{{ formatTime(task.patientFeedbackAt) }}）</span></p><div class="patient-actions"><el-button v-if="['reminded', 'scheduled'].includes(task.status) && !task.patientConfirmedAt" size="small" type="primary" @click="confirmReminder(task)">确认收到提醒</el-button><div class="feedback-form"><el-input v-model="feedbackDrafts[task.id]" type="textarea" :rows="2" maxlength="240" show-word-limit placeholder="选填：记录本次复查 / 转诊后的反馈" aria-label="随访反馈" /><el-button size="small" :disabled="!feedbackDrafts[task.id] || !feedbackDrafts[task.id].trim()" @click="submitFeedback(task)">提交随访反馈</el-button></div></div></div></li></ul></section>
  </main>
</template>
<script>
import ClinicalHeader from '@/components/ClinicalHeader'
import DemoNotice from '@/components/DemoNotice'
import PatientBar from '@/components/dr/PatientBar'
import TaskStatus from '@/components/dr/TaskStatus'
import { portalView } from '@/services/dr/selectors'
import { demoState, gradeInfo } from '@/data/retina-demo'
import { drService } from '@/services/dr'
export default {
  name: 'PatientService',
  components: { ClinicalHeader, DemoNotice, PatientBar, TaskStatus },
  data() {
    return {
      feedbackDrafts: {}
    }
  },
  computed: { portal() { return portalView(demoState.patient.id) } },
  watch: { 'portal.patient.id'() { this.loadFeedbackDrafts() } },
  created() { this.loadFeedbackDrafts() },
  methods: {
    gradeInfo,
    loadFeedbackDrafts() { this.portal.tasks.forEach(task => this.$set(this.feedbackDrafts, task.id, task.patientFeedback || '')) },
    linkedReport(reportId) { return this.portal.reports.find(report => report.id === reportId) || { plan: '' } },
    formatTime(value) { return value ? value.slice(0, 16).replace('T', ' ') : '' },
    async confirmReminder(task) {
      try { await drService.updateTask(task.id, { patientConfirmedAt: new Date().toISOString() }); this.$message.success('已记录“确认收到提醒”，区域看板将同步更新。') } catch (error) { this.$message.error(error.message || '确认失败。') }
    },
    async submitFeedback(task) {
      const feedback = (this.feedbackDrafts[task.id] || '').trim()
      if (!feedback) return
      try { await drService.updateTask(task.id, { patientFeedback: feedback, patientFeedbackAt: new Date().toISOString() }); this.$message.success('随访反馈已保存到本地演示记录。') } catch (error) { this.$message.error(error.message || '反馈保存失败。') }
    }
  }
}
</script>
<style scoped>
.detail-grid dd { overflow-wrap: anywhere; }
.patient-conclusion { margin: 24px 0 8px; }
.patient-plans { list-style: none; padding: 0 24px; margin: 0; }
.patient-plans li { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; padding: 20px 24px; border-bottom: 1px solid var(--border); }
.patient-plans li:last-child { border: 0; }
.patient-plan-main { flex: 1; min-width: 0; }
.patient-plan-heading { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }
.patient-plans h3 { font-size: 15px; margin: 0; }
.patient-plans p { font-size: 12px; color: var(--muted); margin: 7px 0 0; overflow-wrap: anywhere; }
.patient-plans .plan-date { margin-top: 7px; }
.patient-plans .plan-copy { color: var(--heading); line-height: 1.7; }
.patient-action-state { color: var(--primary) !important; }
.patient-action-state i { margin-right: 4px; }
.patient-actions { display: flex; align-items: flex-start; gap: 12px; margin-top: 14px; }
.feedback-form { display: flex; align-items: flex-start; gap: 8px; flex: 1; min-width: 250px; }
.feedback-form .el-textarea { flex: 1; }
@media (max-width: 767px) { .patient-plans li { align-items: flex-start; flex-direction: column; padding-left: 18px; padding-right: 18px; } .patient-actions, .feedback-form { width: 100%; flex-direction: column; } .feedback-form { min-width: 0; } .feedback-form .el-textarea { width: 100%; } }
</style>
