<template>
  <main class="clinical-page intake-page">
    <clinical-header title="影像与数据采集" description="按左右眼核对资料，为后续共识评估建立清晰的输入。">
      <router-link class="text-link" to="/patients/index">查看患者档案 <i class="el-icon-right" /></router-link>
    </clinical-header>
    <patient-strip />
    <demo-notice text="文件只在当前浏览器会话中选择与预览，尚未上传至服务器或调用模型；影像内容不保存，刷新后请重新选择；已确认的合成检查信息会保留。" />
    <section class="panel">
      <div class="intake-steps">
        <el-steps :active="step" finish-status="success" align-center>
          <el-step title="核对基础信息" />
          <el-step title="采集双眼影像" />
          <el-step title="确认资料" />
        </el-steps>
      </div>
      <div v-show="step === 0" class="intake-content">
        <div class="form-section-title"><h2>基础信息与糖尿病史</h2><p>带 * 的项目为必填，其余资料可后续补全。</p></div>
        <el-form ref="intakeForm" :model="form" :rules="rules" label-position="top">
          <div class="form-grid">
            <el-form-item label="姓名 / 脱敏称呼" prop="name"><el-input v-model.trim="form.name" label="姓名或脱敏称呼" maxlength="24" placeholder="请输入演示患者称呼" /></el-form-item>
            <el-form-item label="年龄" prop="age"><el-input-number v-model="form.age" label="年龄" :min="1" :max="120" :precision="0" controls-position="right" /></el-form-item>
            <el-form-item label="性别" prop="sex" for="intake-sex"><el-select id="intake-sex" v-model="form.sex" placeholder="请选择"><el-option label="男" value="男" /><el-option label="女" value="女" /><el-option label="未填写" value="未填写" /></el-select></el-form-item>
            <el-form-item label="糖尿病病程（年）"><el-input-number v-model="form.duration" label="糖尿病病程（年）" :min="0" :max="100" :precision="0" controls-position="right" /></el-form-item>
            <el-form-item label="近期 HbA1c（%）"><el-input v-model.trim="form.hba1c" label="HbA1c（%）" placeholder="选填，例如 7.8" /></el-form-item>
            <el-form-item label="血压（mmHg）"><el-input v-model.trim="form.bp" label="血压（mmHg）" placeholder="选填，例如 132 / 82" /></el-form-item>
            <el-form-item label="眼部症状与既往史" class="field-wide"><el-input v-model="form.notes" label="眼部症状与既往史" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="选填：症状、眼部手术史、既往治疗或待核对的信息" /></el-form-item>
          </div>
        </el-form>
      </div>
      <div v-show="step === 1" class="intake-content">
        <div class="form-section-title"><h2>双眼影像资料</h2><p>眼底彩照至少选择一眼；另一眼或 OCT 缺失时，保留明确的未评估状态。</p></div>
        <div class="equal-columns">
          <section v-for="eye in eyes" :key="eye.key" class="eye-upload-panel">
            <div class="eye-heading"><span class="eye-marker">{{ eye.abbr }}</span><h3>{{ eye.label }}</h3></div>
            <div v-for="slot in eye.slots" :key="slot.key" class="upload-slot" @dragover.prevent @drop.prevent="dropFile($event, slot)">
              <div class="upload-label"><strong>{{ slot.label }}</strong><span class="status-pill" :class="files[slot.key] ? 'info' : ''">{{ files[slot.key] ? '已选择 · 未上传' : '未提供' }}</span></div>
              <div v-if="files[slot.key]" class="selected-file">
                <img v-if="files[slot.key].url && !previewErrors[slot.key]" :src="files[slot.key].url" :alt="eye.label + slot.label + '本地预览'" @error="$set(previewErrors, slot.key, true)">
                <span v-else class="file-symbol"><i class="el-icon-document" aria-hidden="true" /></span>
                <div class="file-info"><strong>{{ files[slot.key].name }}</strong><span>{{ fileSize(files[slot.key].size) }} · {{ files[slot.key].url ? (previewErrors[slot.key] ? '无法预览此文件' : '本地原图预览') : 'DICOM 仅选择文件，暂不支持预览' }}</span></div>
                <button type="button" class="remove-file" :aria-label="'移除' + eye.label + slot.label" @click="removeFile(slot.key)"><i class="el-icon-close" /></button>
              </div>
              <div v-else class="upload-placeholder"><i class="el-icon-upload2" aria-hidden="true" /><p>选择文件，或拖放到这里</p></div>
              <input :id="'retina-file-' + slot.key" class="file-input" type="file" :accept="slot.accept" :aria-label="eye.label + slot.label" @change="changeFile($event, slot)">
              <div class="upload-bottom"><el-button size="small" :icon="files[slot.key] ? 'el-icon-refresh' : 'el-icon-folder-opened'" @click="chooseFile(slot.key)">{{ files[slot.key] ? '更换文件' : '选择文件' }}</el-button><span>{{ slot.hint }}</span></div>
            </div>
          </section>
        </div>
        <div v-if="uploadError" class="upload-error" role="alert"><i class="el-icon-warning-outline" />{{ uploadError }}</div>
      </div>
      <div v-show="step === 2" class="intake-content">
        <div class="form-section-title"><h2>确认本次采集资料</h2><p>提交后进入资料检查页面；当前环境不会生成真实 AI 诊断。</p></div>
        <dl class="detail-grid confirmation-summary">
          <div><dt>患者</dt><dd>{{ form.name }} · {{ form.sex }} · {{ form.age }} 岁</dd></div>
          <div><dt>糖尿病病程</dt><dd>{{ form.duration == null ? '未提供' : form.duration + ' 年' }}</dd></div>
          <div><dt>已选择影像</dt><dd>{{ fileCount }} 份</dd></div>
        </dl>
        <div class="table-scroll review-table">
          <table class="clinical-table">
            <thead><tr><th scope="col">眼别 / 模态</th><th scope="col">文件</th><th scope="col">资料状态</th></tr></thead>
            <tbody><template v-for="eye in eyes"><tr v-for="slot in eye.slots" :key="slot.key"><td>{{ eye.label }} · {{ slot.label }}</td><td class="review-filename">{{ files[slot.key] ? files[slot.key].name : '—' }}</td><td><span class="status-pill" :class="files[slot.key] ? 'info' : ''">{{ files[slot.key] ? '已选择 · 未上传' : '未提供 · 未评估' }}</span></td></tr></template></tbody>
          </table>
        </div>
        <div class="confirmation-note"><i class="el-icon-info" /><span>未连接影像质控与推理接口。文件选择完成不代表图像质量合格，DR 与 DME 评估仍需模型处理及医生复核。</span></div>
      </div>
      <footer class="intake-footer">
        <span class="muted small-text">步骤 {{ step + 1 }} / 3</span>
        <div class="inline-actions"><el-button v-if="step > 0" @click="step--">上一步</el-button><el-button v-if="step < 2" type="primary" @click="next">下一步 <i class="el-icon-right" /></el-button><el-button v-else type="primary" @click="submit">确认资料并查看评估状态</el-button></div>
      </footer>
    </section>
  </main>
</template>
<script>
import ClinicalHeader from '@/components/ClinicalHeader'
import DemoNotice from '@/components/DemoNotice'
import PatientStrip from '@/components/PatientStrip'
import { demoState, setFile, saveIntake } from '@/data/retina-demo'

const slot = (key, label, oct = false) => ({ key, label, oct, accept: oct ? '.jpg,.jpeg,.png,.dcm' : '.jpg,.jpeg,.png', hint: oct ? 'JPG / PNG / DICOM · ≤ 50 MB' : 'JPG / PNG · ≤ 20 MB' })
export default {
  name: 'Input',
  components: { ClinicalHeader, DemoNotice, PatientStrip },
  data() {
    return {
      step: 0,
      form: {},
      uploadError: '',
      previewErrors: {},
      rules: {
        name: [{ required: true, whitespace: true, message: '请填写姓名或脱敏称呼', trigger: 'blur' }],
        age: [{ required: true, type: 'number', message: '请填写年龄', trigger: 'blur' }],
        sex: [{ required: true, message: '请选择性别', trigger: 'change' }]
      },
      eyes: [
        { key: 'right', abbr: 'OD', label: '右眼', slots: [slot('rightCfp', '眼底彩照 CFP'), slot('rightOct', 'OCT', true)] },
        { key: 'left', abbr: 'OS', label: '左眼', slots: [slot('leftCfp', '眼底彩照 CFP'), slot('leftOct', 'OCT', true)] }
      ]
    }
  },
  computed: {
    patient() { return demoState.patient },
    files() { return demoState.files },
    fileCount() { return Object.keys(this.files).length }
  },
  watch: {
    patient() { this.step = 0; this.uploadError = ''; this.previewErrors = {}; this.loadForm() }
  },
  created() { this.loadForm() },
  activated() { this.loadForm() },
  methods: {
    loadForm() {
      const p = demoState.patient
      this.form = { name: p.name, age: p.age, sex: p.sex, duration: p.duration, hba1c: p.hba1c, bp: p.bp, notes: demoState.profileNote }
    },
    fileSize(bytes) { return (bytes / 1024 / 1024).toFixed(1) + ' MB' },
    chooseFile(key) { this.$el.querySelector('#retina-file-' + key).click() },
    changeFile(event, target) {
      const file = event.target.files[0]
      if (file) this.acceptFile(file, target)
      event.target.value = ''
    },
    dropFile(event, target) {
      if (event.dataTransfer.files.length !== 1) {
        this.uploadError = '每个影像位请选择一个文件。'
        return
      }
      this.acceptFile(event.dataTransfer.files[0], target)
    },
    acceptFile(file, target) {
      const valid = target.oct ? /\.(jpe?g|png|dcm)$/i : /\.(jpe?g|png)$/i
      if (!valid.test(file.name)) { this.uploadError = '文件格式不支持，请按该影像位标注的格式选择。'; return }
      if (!file.size || file.size > (target.oct ? 50 : 20) * 1024 * 1024) { this.uploadError = '文件为空或超过大小限制，请重新选择。'; return }
      setFile(target.key, file)
      this.$delete(this.previewErrors, target.key)
      this.uploadError = ''
    },
    removeFile(key) { setFile(key, null); this.$delete(this.previewErrors, key) },
    next() {
      if (this.step === 0) {
        this.$refs.intakeForm.validate(valid => { if (valid) this.step++ })
      } else {
        if (!this.files.rightCfp && !this.files.leftCfp) { this.uploadError = '请至少选择一眼的眼底彩照，未提供的另一眼将保持未评估。'; return }
        this.uploadError = ''
        this.step++
      }
      window.scrollTo({ top: 0, behavior: 'auto' })
    },
    submit() {
      saveIntake(this.form)
      demoState.profileNote = this.form.notes
      this.$message.success('本次浏览器会话已记录资料，尚未上传或推理。')
      this.$router.push('/screening/consensus')
    }
  }
}
</script>
<style scoped>
.intake-steps { padding: 26px 24px 24px; background: #F7FAF8; border-bottom: 1px solid var(--border); }
.intake-steps /deep/ .el-step__title { font-size: 14px; }
.intake-content { padding: 26px 32px; }
.form-section-title { margin-bottom: 22px; }
.form-section-title h2 { margin: 0 0 6px; font-size: 19px; }
.form-section-title p { margin: 0; font-size: 13px; color: var(--muted); }
.eye-upload-panel { border: 1px solid var(--border); border-radius: 8px; padding: 20px; }
.eye-heading { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.eye-marker { display: grid; place-items: center; height: 40px; width: 40px; background: var(--primary-soft); color: var(--primary); border-radius: 7px; font-weight: 600; }
.eye-heading h3 { margin: 0; font-size: 16px; }
.upload-slot { border: 1px dashed var(--input-border); border-radius: 6px; padding: 14px; margin-top: 12px; background: #F8FBF9; }
.upload-label { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.upload-label strong { font-size: 13px; font-weight: 500; color: var(--heading); }
.upload-placeholder { text-align: center; padding: 18px 0 13px; color: var(--muted); }
.upload-placeholder i { font-size: 25px; color: var(--primary); }
.upload-placeholder p { margin: 7px 0 0; font-size: 12px; }
.upload-bottom { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.upload-bottom > span { font-size: 11px; color: var(--muted); }
.file-input { display: none; }
.selected-file { display: flex; align-items: center; gap: 12px; padding: 18px 0; min-height: 96px; }
.selected-file img { width: 70px; height: 58px; object-fit: contain; background: var(--viewer); border-radius: 4px; }
.file-symbol { width: 58px; height: 58px; display: grid; place-items: center; border-radius: 4px; background: var(--blue-soft); color: var(--blue); font-size: 26px; flex-shrink: 0; }
.file-info { min-width: 0; }
.file-info strong { display: block; font-size: 13px; font-weight: 500; overflow-wrap: anywhere; }
.file-info span { display: block; font-size: 11px; color: var(--muted); margin-top: 4px; }
.remove-file { background: transparent; border: 0; padding: 6px; cursor: pointer; color: var(--muted); margin-left: auto; flex-shrink: 0; }
.upload-error { color: var(--danger); background: var(--danger-soft); margin-top: 18px; padding: 12px 16px; border-radius: 5px; font-size: 13px; }
.upload-error i { margin-right: 8px; }
.intake-footer { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 20px 32px; border-top: 1px solid var(--border); }
.confirmation-summary { background: var(--page); padding: 20px; border-radius: 6px; }
.review-table { margin-top: 24px; border: 1px solid var(--border); border-radius: 6px; }
.review-filename { max-width: 280px; white-space: normal !important; overflow-wrap: anywhere; }
.confirmation-note { display: flex; gap: 10px; align-items: baseline; background: var(--blue-soft); padding: 14px 18px; color: var(--blue); font-size: 13px; margin-top: 20px; border-radius: 6px; }
@media (max-width: 767px) {
  .intake-content { padding: 20px 18px; }
  .intake-steps { padding: 20px 10px; }
  .intake-steps /deep/ .el-step__title { font-size: 12px; line-height: 1.5; margin-top: 8px; }
  .eye-upload-panel { padding: 16px; }
  .upload-bottom { flex-wrap: wrap; }
  .intake-footer { padding: 18px; flex-wrap: wrap; }
}
</style>
