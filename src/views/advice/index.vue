<template>
  <main class="clinical-page">
    <clinical-header title="转诊与随访" description="从复核后的报告出发，逐项落实处置安排与持续随访。">
      <el-button icon="el-icon-printer" @click="printPlan">打印演示清单</el-button>
      <el-button type="primary" icon="el-icon-document" @click="$router.push('/screening/evidence')">查看分级证据</el-button>
    </clinical-header>
    <demo-notice :text="report ? '当前显示已签发合成报告与关联任务，仅用于流程演示。' : '当前检查尚未签发报告，下方为准备事项，不构成正式诊疗安排。'" />
    <div class="print-only">糖网诊疗 · 转诊与随访演示清单 · {{ report ? '合成签发示例' : '报告未签发，安排待确认' }}</div>
    <patient-strip />
    <div class="two-column">
      <section class="panel">
        <div class="panel-heading"><h2>处置前的确认事项</h2><span class="status-pill" :class="report ? 'success' : 'warning'">{{ report ? '合成确认记录' : '等待医生复核' }}</span></div>
        <div class="care-summary"><div class="care-summary-icon"><i class="el-icon-document-checked" /></div><div><h3>{{ report ? '依据签发记录查看确认计划' : '先确认报告，再建立处置安排' }}</h3><p>{{ report ? report.plan : '双眼 DR 候选分级、DME 评估和既往病史需要分别核对，当前尚未签发。' }}</p></div></div>
        <div class="care-checklist">
          <div><span class="check-index">01</span><div><strong>核对双眼原始影像与候选分级</strong><p>右眼 OD 与左眼 OS 独立记录，缺失资料保留未评估状态。</p></div><router-link class="text-link" to="/screening/evidence">查看证据</router-link></div>
          <div><span class="check-index">02</span><div><strong>确认黄斑评估与补充检查需求</strong><p>DME 当前未评估；补充哪些检查由医生结合实际情况决定。</p></div><router-link class="text-link" to="/screening/intake">补全资料</router-link></div>
          <div><span class="check-index">03</span><div><strong>医生签发报告并确认计划</strong><p>转诊、复查日期与治疗安排在复核签发后建立。</p></div><span class="status-pill" :class="report ? 'success' : ''">{{ report ? '合成签发示例' : '待签发' }}</span></div>
        </div>
      </section>
      <section class="panel">
        <div class="panel-heading"><h2>当前计划状态</h2><i class="el-icon-date muted" /></div>
        <dl class="plan-state">
          <div><dt>报告签发</dt><dd><span class="status-pill" :class="report ? 'success' : 'warning'">{{ report ? '合成示例已签发' : '未完成' }}</span></dd></div>
          <div><dt>处置计划</dt><dd>{{ report ? '合成确认计划' : '待医生确认' }}</dd></div>
          <div><dt>转诊 / 复查</dt><dd>{{ followupTask ? planTypeLabel(followupTask.planType) : '待医生签发确认' }}</dd></div>
          <div><dt>确认日期</dt><dd>{{ followupTask && followupTask.dueAt ? followupTask.dueAt : '待医生指定' }}</dd></div>
          <div><dt>用药与治疗</dt><dd>未生成处方</dd></div>
        </dl>
        <div class="plan-note"><i class="el-icon-info" /><span>AI 草稿不能自动转为已签发报告或已执行任务。</span></div>
      </section>
    </div>
    <section class="panel section-gap">
      <div class="panel-heading"><div><h2>准备与随访任务</h2><p>准备事项、医生已确认计划及患者反馈均关联到当前检查记录。</p></div><span class="status-pill">流程演示</span></div>
      <div class="care-tasks">
        <article v-for="task in tasks" :key="task.id" class="care-task">
          <div class="care-task-icon" :class="task.tone"><i :class="task.icon" /></div>
          <div class="care-task-content"><div class="care-task-title"><h3>{{ task.title }}</h3><task-status :status="task.status" /></div><p>{{ task.type === 'followup' ? (task.plan || task.description) : task.description }}</p><small v-if="task.type === 'followup'">确认日期：{{ task.dueAt || '未指定' }} · {{ task.patientConfirmedAt ? '患者已确认收到提醒' : '患者尚未确认提醒' }}</small><small v-if="task.type === 'followup' && task.patientFeedback">患者反馈：{{ task.patientFeedback }}</small><small v-if="taskStatus(task.id)">本次备注：{{ taskStatus(task.id).note || '已记录准备进展' }}</small></div>
          <el-button v-if="task.recordable" size="small" @click="openTask(task)">{{ taskStatus(task.id) ? '更新进展' : '记录进展' }}</el-button>
          <el-button v-else-if="task.type === 'followup'" size="small" type="primary" plain @click="openTask(task)">管理随访</el-button>
          <el-button v-else size="small" disabled>{{ task.button || '待医生确认' }}</el-button>
        </article>
      </div>
    </section>
    <div class="care-footer"><i class="el-icon-chat-dot-round" /><span>需要了解页面流程或报告状态？</span><router-link class="text-link" to="/patient/help">打开眼健康助手 <i class="el-icon-right" /></router-link></div>
    <el-dialog :title="activeTask.type === 'followup' ? '管理转诊与随访任务' : '记录演示任务进展'" :visible.sync="dialogVisible" width="520px" :close-on-click-modal="false">
      <p class="dialog-task-title">{{ activeTask.title }}</p>
      <template v-if="activeTask.type === 'followup'">
        <p class="muted small-text">仅用于演示的本地流程；状态更新会同步到患者服务页和区域看板。</p>
        <el-form label-position="top">
          <el-form-item label="随访状态"><el-select v-model="followupDraft.status" style="width:100%"><el-option v-for="option in followupStatusOptions" :key="option.value" :label="option.label" :value="option.value" /></el-select></el-form-item>
          <el-form-item label="确认日期"><el-date-picker v-model="followupDraft.dueAt" type="date" value-format="yyyy-MM-dd" placeholder="选择日期" style="width:100%" /></el-form-item>
          <el-form-item label="机构随访备注"><el-input v-model.trim="followupDraft.note" type="textarea" :rows="3" maxlength="300" show-word-limit placeholder="记录联系、预约或随访核实情况" /></el-form-item>
        </el-form>
      </template>
      <template v-else>
        <p class="muted small-text">记录保存在当前浏览器，状态为“已自报 · 待核实”，不会发送给医院或变更医生计划。</p>
        <el-input v-model="taskNote" type="textarea" :rows="4" maxlength="300" show-word-limit placeholder="选填：已整理的资料、准备进展或需要核对的信息" aria-label="任务进展备注" />
      </template>
      <span slot="footer"><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="activeTask.type === 'followup' ? saveFollowup() : recordTask()">{{ activeTask.type === 'followup' ? '保存随访更新' : '保存演示记录' }}</el-button></span>
    </el-dialog>
  </main>
</template>
<script>
import ClinicalHeader from '@/components/ClinicalHeader'
import DemoNotice from '@/components/DemoNotice'
import PatientStrip from '@/components/PatientStrip'
import { taskViews } from '@/services/dr/selectors'
import TaskStatus from '@/components/dr/TaskStatus'
import { demoState, setTaskState, currentBundle } from '@/data/retina-demo'
import { drService, TASK_STATES } from '@/services/dr'
export default {
  name: 'Advice',
  components: { ClinicalHeader, DemoNotice, PatientStrip, TaskStatus },
  data() {
    return {
      dialogVisible: false, activeTask: {}, taskNote: '', followupDraft: { status: '', dueAt: '', note: '' }
    }
  },
  computed: { patient() { return demoState.patient }, bundle: currentBundle, tasks() { return taskViews(this.bundle) }, report() { return this.bundle.reports.find(item => item.status === 'signed') }, followupTask() { return this.bundle.tasks.find(item => item.type === 'followup') || null }, followupStatusOptions() { const current = this.followupDraft.status; const allowed = { pending_contact: ['reminded', 'scheduled', 'overdue', 'lost'], reminded: ['scheduled', 'completed', 'overdue', 'lost'], scheduled: ['reminded', 'completed', 'overdue', 'lost'], overdue: ['reminded', 'scheduled', 'completed', 'lost'], lost: ['reminded', 'scheduled'], completed: [] }; return [current, ...(allowed[current] || [])].filter((value, index, list) => value && list.indexOf(value) === index).map(value => ({ value, label: (TASK_STATES[value] || {}).label || value })) } },
  watch: { patient() { this.dialogVisible = false; this.activeTask = {}; this.taskNote = '' } },
  methods: {
    taskStatus(id) { const task = this.tasks.find(item => item.id === id); return task && task.status === 'self_reported' ? { note: task.note } : null },
    openTask(task) { this.activeTask = task; this.taskNote = this.taskStatus(task.id) ? this.taskStatus(task.id).note : ''; this.followupDraft = { status: task.status, dueAt: task.dueAt || '', note: task.note || '' }; this.dialogVisible = true },
    recordTask() { setTaskState(this.activeTask.id, { note: this.taskNote.trim() }); this.dialogVisible = false; this.$message.success('本次演示进展已记录，等待核实。') },
    async saveFollowup() { try { await drService.updateTask(this.activeTask.id, { status: this.followupDraft.status, dueAt: this.followupDraft.dueAt || null, note: this.followupDraft.note.trim() }); this.dialogVisible = false; this.$message.success('随访状态已更新，患者页和区域看板已同步。') } catch (error) { this.$message.error(error.message || '随访更新失败。') } },
    planTypeLabel(value) { return { followup: '复查随访', referral: '转诊', both: '转诊与复查' }[value] || '已确认安排' },
    printPlan() { window.print() }
  }
}
</script>
<style scoped>
.care-summary { padding: 24px; display: flex; align-items: flex-start; gap: 16px; background: #F4F8F5; }
.care-summary-icon { flex-shrink: 0; width: 44px; height: 44px; display: grid; place-items: center; background: var(--primary-soft); color: var(--primary); border-radius: 8px; font-size: 24px; }
.care-summary h3 { margin: 0 0 7px; font-size: 18px; font-weight: 600; }
.care-summary p { margin: 0; font-size: 13px; color: var(--muted); }
.care-checklist { padding: 0 24px; }
.care-checklist > div { display: flex; gap: 14px; align-items: flex-start; padding: 21px 0; border-bottom: 1px solid var(--border); }
.care-checklist > div:last-child { border-bottom: 0; }
.check-index { color: var(--input-border); font-size: 12px; margin-top: 3px; }
.care-checklist strong { font-size: 14px; color: var(--heading); font-weight: 500; }
.care-checklist p { color: var(--muted); font-size: 12px; margin: 5px 0 0; }
.care-checklist .text-link, .care-checklist .status-pill { margin-left: auto; flex-shrink: 0; font-size: 12px; margin-top: 2px; }
.plan-state { padding: 6px 24px; margin: 0; font-size: 13px; }
.plan-state > div { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 15px 0; border-bottom: 1px solid #E7EEEB; }
.plan-state > div:last-child { border-bottom: 0; }
.plan-state dt { color: var(--muted); }
.plan-state dd { margin: 0; color: var(--heading); }
.plan-note { display: flex; gap: 9px; padding: 14px 18px; margin: 5px 24px 24px; background: var(--blue-soft); border-radius: 5px; color: var(--blue); font-size: 12px; }
.care-tasks { padding: 0 24px; }
.care-task { display: flex; gap: 16px; align-items: center; padding: 23px 0; border-bottom: 1px solid var(--border); }
.care-task:last-child { border-bottom: 0; }
.care-task-icon { width: 40px; height: 40px; display: grid; place-items: center; font-size: 20px; border-radius: 7px; background: #EDF1F0; color: var(--muted); flex-shrink: 0; }
.care-task-icon.info { background: var(--blue-soft); color: var(--blue); }
.care-task-icon.primary { background: var(--primary-soft); color: var(--primary); }
.care-task-content { flex: 1; min-width: 0; }
.care-task-title { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.care-task-title h3 { margin: 0; font-size: 15px; font-weight: 500; }
.care-task-content p { margin: 5px 0 0; font-size: 13px; color: var(--muted); }
.care-task-content small { display: block; color: var(--blue); margin-top: 8px; font-size: 12px; white-space: pre-wrap; overflow-wrap: anywhere; }
.care-footer { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; padding: 22px 0 0; font-size: 13px; color: var(--muted); }
.care-footer > i { font-size: 20px; color: var(--primary); }
.dialog-task-title { color: var(--heading); font-weight: 500; margin: 0 0 8px; }
@media (max-width: 767px) {
  .care-summary { padding: 20px 18px; }
  .care-checklist { padding: 0 18px; }
  .care-checklist > div { flex-wrap: wrap; gap: 10px; }
  .care-checklist > div > div { flex: 1; min-width: 200px; }
  .care-tasks { padding: 0 18px; }
  .care-task { flex-wrap: wrap; gap: 12px; }
  .care-task-content { flex-basis: calc(100% - 52px); }
  .care-task > .el-button { margin-left: 52px; }
}
</style>
