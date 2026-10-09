<template>
  <main class="clinical-page review-page">
    <clinical-header title="医生审核与签发" description="逐眼核对质控、候选草稿与资料来源；签发后才会生成患者可见报告和随访任务。">
      <el-button icon="el-icon-upload2" @click="$router.push({ path: '/screening/intake', query: $route.query })">补全采集资料</el-button>
    </clinical-header>
    <demo-notice :text="realInference ? '候选等级来自“算法创新7”本机研究推理；病灶空间证据与 DME 未接入模型，审核和签发仍是演示流程，不替代真实阅片或电子签名。' : '候选等级、病灶说明和审核记录均为合成演示数据。当前页面不替代真实阅片、诊断或电子签名。'" />
    <patient-bar />

    <div class="two-column">
      <image-preview :examination="bundle.examination" :images="bundle.images" :files="files" :institution="bundle.institution.name" />
      <section class="panel review-decision">
        <div class="panel-heading">
          <div><h2>{{ report ? (report.researchInference ? '已签发的研究演示报告' : '已签发的演示报告') : '审核决策' }}</h2><p>{{ report ? '签发内容会同步至患者服务与随访模块。' : '先确认质控状态，再接受、修订或退回候选草稿。' }}</p></div>
          <span class="status-pill" :class="report ? 'success' : qualityBlocked ? 'warning' : 'info'">{{ report ? '已签发' : qualityBlocked ? '待补全资料' : '待审核' }}</span>
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

        <el-alert v-if="qualityBlocked && !report" class="quality-block" type="warning" :closable="false" show-icon title="当前资料不能签发" description="存在需重拍、严重不可判读、设备未知或资料缺失的眼别。请先补充采集；DME 始终保持未提供 / 未评估。" />
        <p v-if="!bundle.draft && !report" class="draft-empty"><i class="el-icon-info" />本次资料没有可接受的 AI 草稿。医生可填写人工 ICDR 分级后签发，所有结果均会标记为演示。</p>
        <p v-if="bundle.draft && bundle.draft.disagreements.length && !report" class="review-disagreement"><i class="el-icon-warning-outline" />{{ bundle.draft.disagreements.join('；') }}</p>

        <div v-if="report" class="review-signature">
          <div><span>演示报告编号</span><strong>{{ report.id }}</strong></div>
          <div><span>签发信息</span><strong>{{ report.signedBy }} · {{ formatTime(report.signedAt) }} · 版本 {{ report.version }}</strong></div>
          <p>{{ report.conclusion }}</p>
          <router-link class="text-link" :to="{ path: '/followup/index', query: $route.query }">查看已建立的随访任务 <i class="el-icon-right" /></router-link>
        </div>

        <el-form v-else ref="reviewForm" :model="review" label-position="top" class="review-form">
          <el-form-item label="审核决定" required>
            <el-radio-group v-model="review.action">
              <el-radio label="accepted" :disabled="!bundle.draft">接受候选草稿</el-radio>
              <el-radio label="modified">修改后签发</el-radio>
              <el-radio label="returned">退回补采</el-radio>
            </el-radio-group>
            <p v-if="!bundle.draft" class="form-help">本次未调用模型，不能“接受草稿”；可按人工复核结果修改分级。</p>
          </el-form-item>

          <el-form-item label="审核医生" required><el-input v-model.trim="review.doctor" maxlength="30" placeholder="例如：王医生（演示）" /></el-form-item>

          <template v-if="review.action !== 'returned'">
            <div class="confirmed-plan-box">
              <strong>已确认的转诊 / 复查安排</strong>
              <p>只填写医生已确认、可展示给患者的计划；这是流程演示，不生成临床建议。</p>
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

          <el-form-item :label="review.action === 'returned' ? '退回说明' : '审核意见'"><el-input v-model.trim="review.opinion" type="textarea" :rows="3" maxlength="300" show-word-limit :placeholder="review.action === 'returned' ? '请说明需要补采或重拍的原因' : '选填；会写入演示审核记录'" /></el-form-item>

          <div class="review-actions">
            <el-button v-if="review.action !== 'returned'" :loading="saving" :disabled="!canSubmit" @click="submit(false)">保存审核意见</el-button>
            <el-button type="primary" :loading="saving" :disabled="!canSubmit" @click="submit(true)">{{ review.action === 'returned' ? '确认退回补采' : '确认并签发演示报告' }}</el-button>
          </div>
        </el-form>
        <router-link v-if="!report" class="text-link evidence-link" :to="{ path: '/screening/consensus', query: $route.query }">返回查看质控与候选草稿 <i class="el-icon-right" /></router-link>
      </section>
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
import { currentBundle, demoState, grades, gradeInfo, submitReview } from '@/data/retina-demo'

export default {
  name: 'DoctorReview',
  components: { ClinicalHeader, DemoNotice, PatientBar, ImagePreview, QualityStatus, ReviewHistory },
  data() {
    return {
      eyes: ['OD', 'OS'],
      grades,
      saving: false,
      review: { action: 'accepted', doctor: '演示眼科医生', opinion: '', modificationReason: '', eyeGrades: { OD: null, OS: null }, planType: 'followup', plan: '', dueAt: '' }
    }
  },
  computed: {
    bundle: currentBundle,
    examinationId() { return demoState.examinationId },
    files() { return this.bundle.examination.sourceType === 'local' ? demoState.files : {} },
    report() { return this.bundle.reports.find(item => item.status === 'signed') },
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
      const results = this.bundle.draft ? this.bundle.draft.eyeResults : this.bundle.examination.eyes
      this.review = {
        action: this.bundle.draft ? 'accepted' : 'modified',
        doctor: '演示眼科医生',
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
          this.$message.success('已退回补采，记录已保存。')
          this.$router.push('/screening/intake')
        } else if (sign) {
          this.$message.success('演示报告已签发，并建立了随访任务。')
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
.panel-heading p { margin: 5px 0 0; color: var(--muted); font-size: 12px; font-weight: 400; }
.review-eyes { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.dr-review-eye { padding: 22px 24px; }
.dr-review-eye + .dr-review-eye { border-left: 1px solid var(--border); }
.review-eye-heading { display: flex; align-items: center; gap: 9px; margin-bottom: 13px; }
.eye-token { display: grid; place-items: center; width: 31px; height: 31px; border-radius: 7px; background: var(--primary-soft); color: var(--primary); font-size: 12px; font-weight: 700; }
.dr-review-eye h3 { margin: 0; color: var(--heading); font-size: 15px; }
.review-fields { margin: 17px 0 0; font-size: 12px; }
.review-fields > div { display: flex; justify-content: space-between; gap: 16px; padding: 8px 0; border-top: 1px solid #EDF1F0; }
.review-fields dt { color: var(--muted); }
.review-fields dd { margin: 0; color: var(--heading); text-align: right; }
.model-output { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 13px; color: var(--muted); font-size: 12px; }
.model-output span { padding: 5px 7px; border-radius: 4px; background: var(--page); }
.quality-block { margin: 0 24px 18px; }
.draft-empty, .review-disagreement { margin: 0 24px 18px; padding: 12px 14px; border-radius: 6px; font-size: 13px; line-height: 1.7; }
.draft-empty { color: var(--blue); background: var(--blue-soft); }
.review-disagreement { color: #8A5A14; background: var(--warning-soft); }
.draft-empty i, .review-disagreement i { margin-right: 6px; }
.review-form { padding: 4px 24px 22px; }
.review-form /deep/ .el-radio { margin: 0 20px 10px 0; }
.form-help { margin: 7px 0 0; color: var(--muted); font-size: 12px; line-height: 1.6; }
.manual-grade-box { padding: 15px 16px 1px; margin: 2px 0 18px; background: var(--page); border: 1px solid var(--border); border-radius: 7px; }
.confirmed-plan-box { padding: 15px 16px 1px; margin: 2px 0 18px; background: #F4F8F5; border: 1px solid var(--border); border-radius: 7px; }
.confirmed-plan-box > strong { color: var(--heading); font-size: 13px; }
.confirmed-plan-box > p { margin: 6px 0 12px; color: var(--muted); font-size: 12px; line-height: 1.6; }
.manual-grade-box > strong { color: var(--heading); font-size: 13px; }
.manual-grade-box > p { margin: 6px 0 12px; color: var(--muted); font-size: 12px; }
.manual-grade-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.manual-grade-grid /deep/ .el-select { width: 100%; }
.review-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; padding-top: 4px; }
.evidence-link { display: inline-block; margin: 0 24px 24px; }
.review-signature { margin: 0 24px 24px; padding: 18px; background: var(--primary-soft); border: 1px solid #CFE4E6; border-radius: 8px; font-size: 13px; overflow-wrap: anywhere; }
.review-signature > div { display: grid; grid-template-columns: 92px 1fr; gap: 8px; margin-bottom: 8px; }
.review-signature span { color: var(--muted); }
.review-signature strong { color: var(--heading); font-weight: 500; }
.review-signature p { margin: 13px 0; line-height: 1.7; color: var(--heading); }
@media (max-width: 767px) {
  .review-eyes { grid-template-columns: minmax(0, 1fr); }
  .dr-review-eye { padding: 18px; }
  .dr-review-eye + .dr-review-eye { border-left: 0; border-top: 1px solid var(--border); }
  .quality-block, .draft-empty, .review-disagreement { margin-left: 18px; margin-right: 18px; }
  .review-form { padding-left: 18px; padding-right: 18px; }
  .manual-grade-grid { grid-template-columns: minmax(0, 1fr); gap: 0; }
  .review-signature { margin-left: 18px; margin-right: 18px; }
  .review-signature > div { grid-template-columns: 1fr; gap: 3px; }
  .evidence-link { margin-left: 18px; }
}
</style>
