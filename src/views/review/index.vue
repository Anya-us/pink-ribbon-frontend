<template>
  <main class="clinical-page review-page">
    <patient-bar><template slot="tools"><el-button icon="el-icon-upload2" @click="$router.push({ path: '/screening/intake', query: $route.query })">补全采集资料</el-button></template></patient-bar>
    <demo-notice :text="realInference ? '候选等级来自本机研究推理；病灶空间证据与 DME 未接入模型，审核和签发遵循当前流程，不替代真实阅片或电子签名。' : '候选等级、病灶说明和审核记录均为合成样本数据。当前页面不替代真实阅片、诊断或电子签名。'" />

    <div class="review-workspace">
      <div class="review-evidence-column">
        <image-preview :examination="bundle.examination" :images="bundle.images" :files="files" :institution="bundle.institution.name" />
        <section class="panel review-evidence-summary">
          <div class="panel-heading">
            <div><h2>双眼资料与候选分级</h2><p>按右眼和左眼分别查看本次影像、质控结果与候选等级。</p></div>
          </div>
          <div class="review-eyes">
            <article v-for="eye in eyes" :key="eye" class="dr-review-eye">
              <div class="review-eye-heading"><span class="eye-token">{{ eye }}</span><h3>{{ eyeLabel(eye) }}</h3></div>
              <quality-status :status="bundle.examination.eyes[eye].quality.status" :reason="bundle.examination.eyes[eye].quality.reason" show-reason show-next-step />
              <div v-if="realInference && inferenceFor(eye)" class="model-output"><span>研究模型置信度 {{ formatPercent(inferenceFor(eye).confidence) }}</span><span>{{ consensusLabel(inferenceFor(eye).consensus) }}</span></div>
              <dl class="review-fields">
                <div><dt>{{ report ? '已签发等级' : '候选等级' }}</dt><dd>{{ gradeInfo(resultFor(eye).drGrade).label }}</dd></div>
                <div><dt>黄斑水肿 DME</dt><dd>未提供 / 未评估</dd></div>
                <div><dt>影像模态</dt><dd>{{ modalityText(eye) }}</dd></div>
              </dl>
            </article>
          </div>
        </section>
      </div>
      <div class="review-action-column">
        <section class="panel review-decision">
          <div class="panel-heading">
            <div><h2>{{ report ? (report.researchInference ? '已签发的研究报告' : '已签发的样本报告') : '审核决策' }}</h2><p>{{ report ? '签发内容会同步至患者服务与随访模块。' : '先确认质控状态，再接受、修订或退回候选草稿。' }}</p></div>
            <span class="status-pill" :class="report ? 'success' : qualityBlocked ? 'warning' : 'info'">{{ report ? '已签发' : qualityBlocked ? '待补全资料' : '待审核' }}</span>
          </div>

          <div class="review-brief">
            <template v-if="report">
              <dl class="brief-list">
                <div><dt>报告编号</dt><dd>{{ report.id }}</dd></div>
                <div><dt>签发信息</dt><dd>{{ report.signedBy }} · {{ formatTime(report.signedAt) }}</dd></div>
                <div><dt>后续安排</dt><dd>{{ planTypeLabel(report.planType) }}</dd></div>
              </dl>
              <p class="brief-description">{{ report.conclusion }}</p>
              <div class="brief-actions">
                <el-button icon="el-icon-view" @click="openDialog('eyes')">查看双眼结论</el-button>
                <el-button type="primary" plain icon="el-icon-date" @click="openDialog('plan')">查看后续安排</el-button>
              </div>
              <router-link class="text-link signed-followup-link" :to="{ path: '/followup/index', query: $route.query }">进入随访任务 <i class="el-icon-right" /></router-link>
            </template>
            <template v-else>
              <div class="brief-status"><i :class="qualityBlocked ? 'el-icon-warning-outline' : 'el-icon-circle-check'" /><strong>{{ qualityBlocked ? '资料待补全' : '可以开始审核' }}</strong></div>
              <p class="brief-description">{{ qualityBlocked ? '部分资料仍待补充。可打开审核签发表记录退回说明，或返回质控页面继续处理。' : '已完成双眼资料核对，可在签发表中接受、修改或退回本次记录。' }}</p>
              <dl class="brief-list">
                <div><dt>质控状态</dt><dd>{{ qualityBlocked ? '待补全资料' : '双眼质控通过' }}</dd></div>
                <div><dt>候选草稿</dt><dd>{{ bundle.draft ? '已生成，待审核' : '待人工分级' }}</dd></div>
              </dl>
              <div class="brief-actions">
                <el-button type="primary" icon="el-icon-edit-outline" @click="openDialog('sign')">打开审核签发表</el-button>
                <router-link class="text-link" :to="{ path: '/screening/consensus', query: $route.query }">查看质控与候选草稿 <i class="el-icon-right" /></router-link>
              </div>
            </template>
          </div>
        </section>
        <review-history class="review-history-panel" :records="bundle.reviewRecords" />
      </div>
    </div>
    <el-dialog :visible.sync="dialogVisible" :title="dialogTitle" width="560px" append-to-body @closed="dialogMode = ''">
      <el-form v-if="dialogMode === 'sign'" ref="reviewForm" :model="review" label-position="top" class="review-form">
        <el-form-item label="审核决定" required>
          <el-radio-group v-model="review.action">
            <el-radio label="accepted" :disabled="!bundle.draft">接受候选草稿</el-radio>
            <el-radio label="modified">修改后签发</el-radio>
            <el-radio label="returned">退回补采</el-radio>
          </el-radio-group>
          <p v-if="!bundle.draft" class="form-help">本次未调用模型，不能“接受草稿”；可按人工复核结果修改分级。</p>
        </el-form-item>
        <el-alert v-if="qualityBlocked" class="dialog-quality-block" type="warning" :closable="false" show-icon title="当前资料待补全" description="可以记录退回说明；签发前请先完成需要补充的采集资料。" />
        <el-form-item label="审核医生" required><el-input v-model.trim="review.doctor" maxlength="30" placeholder="例如：王医生" /></el-form-item>
        <template v-if="review.action !== 'returned'">
          <div class="confirmed-plan-box">
            <strong>已确认的转诊 / 复查安排</strong>
            <p>只填写医生已确认、可展示给患者的计划；相关安排由医生结合实际情况确认。</p>
            <el-form-item label="安排类型" required><el-select v-model="review.planType" style="width:100%"><el-option label="复查随访" value="followup" /><el-option label="转诊" value="referral" /><el-option label="转诊与复查" value="both" /></el-select></el-form-item>
            <el-form-item label="计划内容" required><el-input v-model.trim="review.plan" type="textarea" :rows="2" maxlength="300" show-word-limit placeholder="填写已确认的联系、转诊或复查安排" /></el-form-item>
            <el-form-item label="确认日期（选填）"><el-date-picker v-model="review.dueAt" type="date" value-format="yyyy-MM-dd" placeholder="选择已确认的日期" style="width:100%" /></el-form-item>
          </div>
        </template>
        <template v-if="review.action === 'modified'">
          <div class="manual-grade-box">
            <strong>人工确认的 ICDR 分级</strong>
            <p>仅为有眼底彩照且质控通过的眼别选择最终等级。</p>
            <div class="manual-grade-grid">
              <el-form-item v-for="eye in collectedEyes" :key="eye" :label="eyeLabel(eye) + '最终等级'" required>
                <el-select v-model="review.eyeGrades[eye]" placeholder="请选择"><el-option v-for="grade in grades" :key="grade.code" :label="grade.label" :value="grade.code" /></el-select>
              </el-form-item>
            </div>
          </div>
          <el-form-item label="修改原因" required><el-input v-model.trim="review.modificationReason" type="textarea" :rows="2" maxlength="240" show-word-limit placeholder="例如：人工复核后调整候选等级的原因" /></el-form-item>
        </template>
        <el-form-item :label="review.action === 'returned' ? '退回说明' : '审核意见'"><el-input v-model.trim="review.opinion" type="textarea" :rows="3" maxlength="300" show-word-limit :placeholder="review.action === 'returned' ? '请说明需要补采或重拍的原因' : '选填；会写入审核记录'" /></el-form-item>
        <div class="review-actions">
          <el-button v-if="review.action !== 'returned'" :loading="saving" :disabled="!canSubmit" @click="submit(false)">保存审核意见</el-button>
          <el-button type="primary" :loading="saving" :disabled="!canSubmit" @click="submit(true)">{{ review.action === 'returned' ? '确认退回补采' : '确认并签发报告' }}</el-button>
        </div>
      </el-form>
      <div v-else-if="dialogMode === 'eyes' && report" class="report-detail-dialog">
        <div v-for="eye in eyes" :key="eye" class="dialog-eye-result">
          <div><span>{{ eyeLabel(eye) }}</span><strong>{{ gradeInfo(report.eyeResults[eye].drGrade).label }}</strong></div>
          <p>黄斑水肿：未评估</p>
        </div>
      </div>
      <div v-else-if="dialogMode === 'plan' && report" class="report-detail-dialog dialog-plan-detail">
        <span class="dialog-plan-tag">{{ planTypeLabel(report.planType) }}</span>
        <p>{{ report.plan || '后续安排将在随访模块中持续更新。' }}</p>
        <time v-if="report.dueAt"><i class="el-icon-date" /> 计划日期：{{ report.dueAt }}</time>
        <router-link class="text-link" :to="{ path: '/followup/index', query: $route.query }" @click.native="dialogVisible = false">进入随访任务 <i class="el-icon-right" /></router-link>
      </div>
    </el-dialog>
  </main>
</template>

<script>
import DemoNotice from '@/components/DemoNotice'
import PatientBar from '@/components/dr/PatientBar'
import ImagePreview from '@/components/dr/ImagePreview'
import QualityStatus from '@/components/dr/QualityStatus'
import ReviewHistory from '@/components/dr/ReviewHistory'
import { currentBundle, demoState, grades, gradeInfo, submitReview } from '@/data/retina-demo'

export default {
  name: 'DoctorReview',
  components: { DemoNotice, PatientBar, ImagePreview, QualityStatus, ReviewHistory },
  data() {
    return {
      eyes: ['OD', 'OS'],
      grades,
      saving: false,
      dialogVisible: false,
      dialogMode: '',
      review: { action: 'accepted', doctor: '样本眼科医生', opinion: '', modificationReason: '', eyeGrades: { OD: null, OS: null }, planType: 'followup', plan: '', dueAt: '' }
    }
  },
  computed: {
    bundle: currentBundle,
    examinationId() { return demoState.examinationId },
    files() { return this.bundle.examination.sourceType === 'local' ? demoState.files : {} },
    report() { return this.bundle.reports.find(item => item.status === 'signed') },
    dialogTitle() {
      return { sign: '审核与签发表', eyes: '本次双眼结论', plan: '已确认后续安排' }[this.dialogMode] || '医生审核'
    },
    realInference() { return !!(this.bundle.draft && this.bundle.draft.source === 'algorithm7_local_api') },
    collectedEyes() {
      return this.eyes.filter(eye => this.bundle.images.some(image => image.eye === eye && image.modality === 'CFP'))
    },
    qualityBlocked() {
      return this.collectedEyes.length === 0 || this.collectedEyes.some(eye => this.bundle.examination.eyes[eye].quality.status !== 'passed')
    },
    canSubmit() {
      if (!this.review.doctor) return false
      if (this.review.action === 'returned') return true
      if (this.qualityBlocked) return false
      if (this.review.action === 'accepted') return !!this.bundle.draft
      return !!this.review.modificationReason && this.collectedEyes.every(eye => Number.isInteger(this.review.eyeGrades[eye]))
    }
  },
  watch: {
    examinationId() { this.resetReview() }
  },
  created() { this.resetReview() },
  methods: {
    gradeInfo,
    eyeLabel(eye) { return eye === 'OD' ? '右眼 OD' : '左眼 OS' },
    formatTime(value) { return value ? value.slice(0, 16).replace('T', ' ') : '—' },
    planTypeLabel(value) { return { followup: '复查随访', referral: '转诊安排', both: '转诊与复查' }[value] || '后续安排' },
    openDialog(mode) {
      this.dialogMode = mode
      this.dialogVisible = true
    },
    modalityText(eye) {
      const modalities = this.bundle.images.filter(image => image.eye === eye).map(image => image.modality)
      return modalities.length ? modalities.join(' + ') : '未提供'
    },
    resultFor(eye) {
      const results = this.report ? this.report.eyeResults : this.bundle.draft ? this.bundle.draft.eyeResults : this.bundle.examination.eyes
      return results[eye] || { drGrade: null }
    },
    inferenceFor(eye) { return this.bundle.examination.eyes[eye] && this.bundle.examination.eyes[eye].inference },
    formatPercent(value) { return Number.isFinite(value) ? (value * 100).toFixed(1) + '%' : '未返回' },
    consensusLabel(consensus) {
      const state = consensus && consensus.status
      return { accept: '共识：可进入人工复核', review: '共识：建议人工复核', reject: '共识：需补充采集' }[state] || '共识：未返回'
    },
    resetReview() {
      this.dialogVisible = false
      this.dialogMode = ''
      const results = this.bundle.draft ? this.bundle.draft.eyeResults : this.bundle.examination.eyes
      this.review = {
        action: this.bundle.draft ? 'accepted' : 'modified',
        doctor: '样本眼科医生',
        opinion: '',
        modificationReason: '',
        eyeGrades: { OD: results.OD ? results.OD.drGrade : null, OS: results.OS ? results.OS.drGrade : null },
        planType: 'followup',
        plan: '',
        dueAt: ''
      }
    },
    submit(sign) {
      if (!this.canSubmit) return
      if (sign && this.review.action !== 'returned' && !this.review.plan.trim()) { this.$message.error('请填写医生已确认的转诊 / 复查安排。'); return }
      this.saving = true
      try {
        const result = submitReview({ ...this.review, eyeGrades: { ...this.review.eyeGrades }, sign: sign && this.review.action !== 'returned' })
        if (this.review.action === 'returned') {
          this.dialogVisible = false
          this.$message.success('已退回补采，记录已保存。')
          this.$router.push('/screening/intake')
        } else if (sign) {
          this.dialogVisible = false
          this.$message.success('报告已签发，并建立了随访任务。')
        } else {
          this.$message.success('审核意见已保存，尚未签发。')
        }
        return result
      } catch (error) {
        this.$message.error(error.message || '审核提交失败，请检查资料。')
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.panel-heading p { margin: 5px 0 0; color: var(--muted); font-size: 14px; font-weight: 400; }
.review-workspace { display: grid; grid-template-columns: minmax(0, 1.08fr) minmax(430px, .92fr); gap: 20px; align-items: stretch; }
.review-evidence-column { display: grid; min-width: 0; gap: 20px; }
.review-action-column { display: flex; min-width: 0; flex-direction: column; gap: 20px; }
.review-decision { min-width: 0; }
.review-eyes { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.dr-review-eye { padding: 22px 24px; }
.dr-review-eye + .dr-review-eye { border-left: 1px solid var(--border); }
.review-eye-heading { display: flex; align-items: center; gap: 9px; margin-bottom: 13px; }
.eye-token { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 7px; background: var(--primary-soft); color: var(--primary); font-size: 14px; font-weight: 700; }
.dr-review-eye h3 { margin: 0; color: var(--heading); font-size: 15px; }
.review-fields { margin: 17px 0 0; font-size: 14px; }
.review-fields > div { display: flex; justify-content: space-between; gap: 16px; padding: 8px 0; border-top: 1px solid #EDF1F0; }
.review-fields dt { color: var(--muted); }
.review-fields dd { margin: 0; color: var(--heading); text-align: right; }
.model-output { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 13px; color: var(--muted); font-size: 14px; }
.model-output span { padding: 5px 7px; border-radius: 4px; background: var(--page); }
.review-decision { display: flex; flex-direction: column; min-height: 310px; }
.review-history-panel { display: flex; flex: 1; flex-direction: column; }
.review-history-panel /deep/ .empty-state { display: flex; flex: 1; flex-direction: column; justify-content: center; }
.review-brief { display: flex; flex: 1; flex-direction: column; align-items: flex-start; padding: 24px; }
.brief-status { display: flex; align-items: center; gap: 9px; color: var(--heading); font-size: 17px; }
.brief-status i { color: var(--primary); font-size: 20px; }
.brief-list { width: 100%; margin: 19px 0 0; }
.brief-list > div { display: flex; justify-content: space-between; gap: 20px; padding: 11px 0; border-top: 1px solid var(--border); }
.brief-list dt { color: var(--muted); }
.brief-list dd { margin: 0; color: var(--heading); text-align: right; overflow-wrap: anywhere; }
.brief-description { margin: 16px 0 0; color: var(--text); line-height: 1.75; }
.brief-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin-top: auto; padding-top: 22px; }
.review-form { padding: 4px 0 0; }
.review-form /deep/ .el-radio { margin: 0 20px 10px 0; }
.form-help { margin: 7px 0 0; color: var(--muted); font-size: 14px; line-height: 1.6; }
.dialog-quality-block { margin: 0 0 18px; }
.manual-grade-box { padding: 15px 16px 1px; margin: 2px 0 18px; background: var(--page); border: 1px solid var(--border); border-radius: 7px; }
.confirmed-plan-box { padding: 15px 16px 1px; margin: 2px 0 18px; background: #F4F8F5; border: 1px solid var(--border); border-radius: 7px; }
.confirmed-plan-box > strong { color: var(--heading); font-size: 15px; }
.confirmed-plan-box > p { margin: 6px 0 12px; color: var(--muted); font-size: 14px; line-height: 1.6; }
.manual-grade-box > strong { color: var(--heading); font-size: 15px; }
.manual-grade-box > p { margin: 6px 0 12px; color: var(--muted); font-size: 14px; }
.manual-grade-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.manual-grade-grid /deep/ .el-select { width: 100%; }
.review-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; padding-top: 4px; }
.signed-followup-link { display: inline-block; margin-top: 16px; }
.report-detail-dialog { display: grid; gap: 12px; }
.dialog-eye-result { display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 15px 16px; background: var(--page); border: 1px solid var(--border); border-radius: 8px; }
.dialog-eye-result > div { display: grid; gap: 3px; }
.dialog-eye-result strong { color: var(--heading); font-size: 17px; }
.dialog-eye-result p { margin: 0; color: var(--muted); font-size: 14px; }
.dialog-plan-detail { align-items: start; }
.dialog-plan-tag { padding: 4px 9px; border-radius: 5px; background: var(--primary-soft); color: var(--primary-hover); font-size: 14px; }
.dialog-plan-detail p { margin: 2px 0; line-height: 1.8; color: var(--heading); }
.dialog-plan-detail time { color: var(--muted); font-size: 14px; }
.dialog-plan-detail time i { margin-right: 4px; color: var(--primary); }
@media (max-width: 1180px) {
  .review-workspace { grid-template-columns: minmax(0, 1fr); }
  .review-action-column { display: grid; }
  .review-decision { max-width: none; }
  .review-history-panel { display: block; }
}
@media (max-width: 767px) {
  .review-eyes { grid-template-columns: minmax(0, 1fr); }
  .dr-review-eye { padding: 18px; }
  .dr-review-eye + .dr-review-eye { border-left: 0; border-top: 1px solid var(--border); }
  .review-brief { padding: 18px; }
  .manual-grade-grid { grid-template-columns: minmax(0, 1fr); gap: 0; }
  .dialog-eye-result { align-items: flex-start; flex-direction: column; gap: 6px; }
  .brief-list > div { align-items: flex-start; flex-direction: column; gap: 3px; }
  .brief-list dd { text-align: left; }
}
</style>
