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
        <div class="form-section-title"><h2>确认患者与基础信息</h2><p>先确认本次检查对象；带 * 的项目为必填，其余资料可后续补全。</p></div>
        <div class="patient-confirm-box">
          <div><span>当前演示患者</span><strong>{{ patient.name }} · {{ patient.id }}</strong><small>{{ patient.institutionId === 'ORG-002' ? '眼科门诊（演示）' : '城南社区筛查点（演示）' }}</small></div>
          <el-select v-model="selectedPatientId" size="small" aria-label="选择演示患者" @change="changePatient"><el-option v-for="item in patients" :key="item.id" :label="item.name + ' · ' + item.id" :value="item.id" /></el-select>
          <el-button size="small" type="primary" :plain="patientConfirmed" @click="confirmPatient">{{ patientConfirmed ? '患者已确认' : '确认患者' }}</el-button>
        </div>
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
        <div class="form-section-title"><h2>确认眼别与采集资料</h2><p>先选择本次采集的眼别，再登记时间与设备；未纳入采集的眼别保持“未提供 / 未评估”。</p></div>
        <div class="capture-registration">
          <el-form label-position="top" class="form-grid">
            <el-form-item label="本次采集眼别" required class="field-wide"><el-checkbox-group v-model="capture.eyes"><el-checkbox label="OD">右眼 OD</el-checkbox><el-checkbox label="OS">左眼 OS</el-checkbox></el-checkbox-group></el-form-item>
            <el-form-item label="采集时间" required><el-date-picker v-model="capture.capturedAt" type="datetime" value-format="yyyy-MM-ddTHH:mm:ss" placeholder="选择采集时间" style="width:100%" /></el-form-item>
            <el-form-item label="采集来源"><el-radio-group v-model="capture.source"><el-radio label="现场采集">现场采集</el-radio><el-radio label="导入影像">导入影像</el-radio></el-radio-group></el-form-item>
            <el-form-item label="采集设备" required><el-select v-model="capture.deviceId" placeholder="请选择；未知时选未登记" style="width:100%"><el-option label="眼底相机 A（演示）" value="DEV-CFP-001" /><el-option label="未登记 / 设备未知" value="" /></el-select></el-form-item>
          </el-form>
          <p class="registration-note"><i class="el-icon-info" />设备未知会在质控结果中明确标为“设备未知”，并阻止进入签发流程。</p>
        </div>
        <div class="equal-columns">
          <section v-for="eye in selectedEyes" :key="eye.key" class="eye-upload-panel">
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
        <div class="form-section-title"><h2>确认本次采集资料</h2><p>提交后会调用本机研究模型进行五级 DR 分级，再进入资料检查页面。</p></div>
        <dl class="detail-grid confirmation-summary">
          <div><dt>患者</dt><dd>{{ form.name }} · {{ form.sex }} · {{ form.age }} 岁</dd></div>
          <div><dt>糖尿病病程</dt><dd>{{ form.duration == null ? '未提供' : form.duration + ' 年' }}</dd></div>
          <div><dt>确认眼别</dt><dd>{{ capture.eyes.join('、') || '未确认' }}</dd></div>
          <div><dt>采集时间</dt><dd>{{ capture.capturedAt || '未登记' }}</dd></div>
          <div><dt>采集设备</dt><dd>{{ capture.deviceId ? '眼底相机 A（演示）' : '未登记 / 设备未知' }}</dd></div>
          <div><dt>已选择影像</dt><dd>{{ fileCount }} 份</dd></div>
        </dl>
        <div class="table-scroll review-table">
          <table class="clinical-table">
            <thead><tr><th scope="col">眼别 / 模态</th><th scope="col">文件</th><th scope="col">资料状态</th></tr></thead>
            <tbody><template v-for="eye in eyes"><tr v-for="slot in eye.slots" :key="slot.key"><td>{{ eye.label }} · {{ slot.label }}</td><td class="review-filename">{{ files[slot.key] ? files[slot.key].name : '—' }}</td><td><span class="status-pill" :class="files[slot.key] ? 'info' : ''">{{ files[slot.key] ? '已选择 · 未上传' : '未提供 · 未评估' }}</span></td></tr></template></tbody>
          </table>
        </div>
        <div class="confirmation-note"><i class="el-icon-info" /><span>将调用“算法创新7”本机接口，返回研究用途的 DR 五级概率、基础技术检查和人工复核提示；DME 与病灶定位不在本次模型能力范围内。</span></div>
        <el-form label-position="top" class="quality-demo-form"><el-form-item label="人工采集质控标记（可选）"><el-select v-model="capture.qualityScenario" style="width:100%"><el-option label="不预设，由模型技术检查决定" value="" /><el-option label="需要重拍（人工标记）" value="retake" /><el-option label="严重不可判读（人工标记）" value="ungradable" /></el-select><p>只有人工明确标记时才覆盖模型技术检查；“设备未知”仍由设备登记状态决定并阻止签发。</p></el-form-item></el-form>
      </div>
      <footer class="intake-footer">
        <span class="muted small-text">步骤 {{ step + 1 }} / 3</span>
        <div class="inline-actions"><el-button v-if="step > 0" :disabled="submitting" @click="step--">上一步</el-button><el-button v-if="step < 2" type="primary" :disabled="submitting" @click="next">下一步 <i class="el-icon-right" /></el-button><el-button v-else type="primary" :loading="submitting" @click="submit">确认资料并运行推理</el-button></div>
      </footer>
    </section>
  </main>
</template>
<script>
import ClinicalHeader from '@/components/ClinicalHeader'
import DemoNotice from '@/components/DemoNotice'
import PatientStrip from '@/components/PatientStrip'
import { demoState, patients, selectPatient, setFile, saveIntake, attachInference } from '@/data/retina-demo'
import { predictFundusEyes } from '@/services/dr/inference'

const slot = (key, label, oct = false) => ({ key, label, oct, accept: oct ? '.jpg,.jpeg,.png,.dcm' : '.jpg,.jpeg,.png', hint: oct ? 'JPG / PNG / DICOM · ≤ 50 MB' : 'JPG / PNG · ≤ 20 MB' })
export default {
  name: 'Input',
  components: { ClinicalHeader, DemoNotice, PatientStrip },
  data() {
    return {
      step: 0,
      form: {},
      selectedPatientId: demoState.patient.id,
      patientConfirmed: false,
      capture: { eyes: [], capturedAt: this.localTimestamp(), source: '现场采集', deviceId: 'DEV-CFP-001', qualityScenario: '' },
      submitting: false,
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
    fileCount() { return Object.keys(this.files).length },
    selectedEyes() { return this.eyes.filter(eye => this.capture.eyes.includes(eye.abbr)) }
  },
  watch: {
    patient() { this.step = 0; this.patientConfirmed = false; this.capture.eyes = []; this.uploadError = ''; this.previewErrors = {}; this.loadForm() }
  },
  created() { this.loadForm() },
  activated() { this.loadForm() },
  methods: {
    loadForm() {
      const p = demoState.patient
      this.selectedPatientId = p.id
      this.form = { name: p.name, age: p.age, sex: p.sex, duration: p.duration, hba1c: p.hba1c, bp: p.bp, notes: demoState.profileNote }
    },
    changePatient(patientId) {
      const patient = patients.find(item => item.id === patientId)
      if (patient) selectPatient(patient)
    },
    confirmPatient() {
      this.patientConfirmed = true
      this.$message.success('本次检查患者已确认。')
    },
    localTimestamp() {
      const now = new Date()
      const fill = value => String(value).padStart(2, '0')
      return now.getFullYear() + '-' + fill(now.getMonth() + 1) + '-' + fill(now.getDate()) + 'T' + fill(now.getHours()) + ':' + fill(now.getMinutes()) + ':' + fill(now.getSeconds())
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
        if (!this.patientConfirmed) { this.$message.error('请先确认本次检查患者。'); return }
        this.$refs.intakeForm.validate(valid => { if (valid) this.step++ })
      } else {
        if (!this.capture.eyes.length) { this.uploadError = '请先确认本次采集的左眼或右眼。'; return }
        if (!this.capture.capturedAt) { this.uploadError = '请登记采集时间。'; return }
        const missingCfp = this.capture.eyes.some(eye => !this.files[eye === 'OD' ? 'rightCfp' : 'leftCfp'])
        if (missingCfp) { this.uploadError = '每个已确认眼别都需要选择一份眼底彩照。'; return }
        this.uploadError = ''
        this.step++
      }
      window.scrollTo({ top: 0, behavior: 'auto' })
    },
    async submit() {
      if (!this.patientConfirmed || !this.capture.eyes.length) { this.$message.error('请先确认患者和检查眼别。'); return }
      saveIntake(this.form, this.capture)
      demoState.profileNote = this.form.notes
      const files = {}
      this.capture.eyes.forEach(eye => {
        const key = eye === 'OD' ? 'rightCfp' : 'leftCfp'
        if (demoState.files[key]) files[eye] = demoState.files[key]
      })
      this.submitting = true
      try {
        attachInference(await predictFundusEyes(files))
        this.$message.success('本机模型已完成研究推理，正在进入质控与共识草稿。')
      } catch (error) {
        this.$message.warning('采集资料已保存，但未得到模型结果：' + (error.message || '请检查本机后端。'))
      } finally {
        this.submitting = false
        this.$router.push('/screening/consensus')
      }
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
.patient-confirm-box { display: grid; grid-template-columns: minmax(180px, 1fr) minmax(190px, 250px) auto; gap: 14px; align-items: center; padding: 16px 18px; margin-bottom: 22px; background: var(--primary-soft); border: 1px solid #CFE4E6; border-radius: 8px; }
.patient-confirm-box span, .patient-confirm-box small { display: block; color: var(--muted); font-size: 12px; }
.patient-confirm-box strong { display: block; margin: 4px 0; color: var(--heading); font-size: 15px; }
.capture-registration { padding: 18px 20px 10px; margin-bottom: 20px; background: var(--page); border: 1px solid var(--border); border-radius: 8px; }
.capture-registration /deep/ .el-form-item { margin-bottom: 16px; }
.registration-note { margin: 2px 0 8px; color: var(--muted); font-size: 12px; }
.registration-note i { color: var(--blue); margin-right: 5px; }
.quality-demo-form { max-width: 470px; margin-top: 22px; padding: 16px 18px 2px; background: var(--page); border: 1px solid var(--border); border-radius: 6px; }
.quality-demo-form p { margin: 8px 0 0; color: var(--muted); font-size: 12px; line-height: 1.7; }
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
  .patient-confirm-box { grid-template-columns: 1fr; }
  .upload-bottom { flex-wrap: wrap; }
  .intake-footer { padding: 18px; flex-wrap: wrap; }
}
</style>
