<template>
  <div class="two-column">
    <section class="panel">
      <div class="panel-heading"><h2>基础信息与糖尿病史</h2><el-button v-if="!editing" type="text" icon="el-icon-edit" @click="startEdit">编辑演示档案</el-button><span v-else class="status-pill info">编辑中</span></div>
      <div class="panel-body">
        <el-form v-if="editing" ref="form" :model="draft" :rules="rules" label-position="top">
          <div class="form-grid">
            <el-form-item label="姓名 / 脱敏称呼" prop="name"><el-input v-model.trim="draft.name" label="姓名或脱敏称呼" maxlength="24" /></el-form-item>
            <el-form-item label="年龄" prop="age"><el-input-number v-model="draft.age" label="年龄" :min="1" :max="120" :precision="0" /></el-form-item>
            <el-form-item label="性别" for="profile-sex"><el-select id="profile-sex" v-model="draft.sex"><el-option label="男" value="男" /><el-option label="女" value="女" /><el-option label="未填写" value="未填写" /></el-select></el-form-item>
            <el-form-item label="糖尿病病程（年）"><el-input-number v-model="draft.duration" label="糖尿病病程（年）" :min="0" :max="100" :precision="0" /></el-form-item>
            <el-form-item label="HbA1c（%）"><el-input v-model.trim="draft.hba1c" label="HbA1c（%）" placeholder="未提供可留空" /></el-form-item>
            <el-form-item label="血压（mmHg）"><el-input v-model.trim="draft.bp" label="血压（mmHg）" placeholder="例如 132 / 82" /></el-form-item>
            <el-form-item label="病史备注" class="field-wide"><el-input v-model="note" label="病史备注" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="记录眼科既往史、用药或待核对的信息" /></el-form-item>
          </div>
          <div class="inline-actions"><el-button type="primary" @click="save">保存本次编辑</el-button><el-button @click="editing = false">取消</el-button></div>
        </el-form>
        <div v-else>
          <dl class="detail-grid">
            <div><dt>病例编号</dt><dd>{{ patient.id }}</dd></div>
            <div><dt>姓名</dt><dd>{{ patient.name }}</dd></div>
            <div><dt>性别 / 年龄</dt><dd>{{ patient.sex }} / {{ patient.age }} 岁</dd></div>
            <div><dt>糖尿病病程</dt><dd>{{ patient.duration == null ? '未填写' : patient.duration + ' 年' }}</dd></div>
            <div><dt>HbA1c</dt><dd>{{ patient.hba1c ? patient.hba1c + ' %' : '未提供' }}</dd></div>
            <div><dt>血压</dt><dd>{{ patient.bp ? patient.bp + ' mmHg' : '未提供' }}</dd></div>
          </dl>
          <div class="history-note"><h3>病史备注</h3><p>{{ savedNote || '眼科既往史、糖尿病用药与近期症状尚待核对。' }}</p></div>
          <div class="record-source"><i class="el-icon-document" aria-hidden="true" />来源：{{ custom ? '本次采集表单' : '演示档案' }} · 仅用于页面流程展示</div>
        </div>
      </div>
    </section>
    <section class="panel">
      <div class="panel-heading"><h2>资料完整性</h2><span class="status-pill info">待核对</span></div>
      <div class="completeness-list">
        <div><span><i class="el-icon-user" />基础资料</span><span class="status-pill success">已填写</span></div>
        <div><span><i class="el-icon-view" />眼底彩照</span><span class="status-pill" :class="hasCfp ? 'info' : ''">{{ hasCfp ? '已登记' : '未提供' }}</span></div>
        <div><span><i class="el-icon-data-line" />OCT</span><span class="status-pill" :class="hasOct ? 'info' : ''">{{ hasOct ? '已登记' : '未提供' }}</span></div>
        <div><span><i class="el-icon-document-checked" />医生签发报告</span><span class="status-pill" :class="signedReport ? 'success' : ''">{{ signedReport ? '合成报告已签发' : '未签发' }}</span></div>
      </div>
      <p class="completeness-note">资料完整性与诊断结果分别记录。缺少检查资料时，相关评估保持“未评估”。</p>
    </section>
  </div>
</template>
<script>
import { demoState, updatePatient, currentBundle } from '@/data/retina-demo'
export default {
  name: 'PatientDetails',
  data() {
    return {
      editing: false, draft: {}, note: '',
      rules: {
        name: [{ required: true, whitespace: true, message: '请填写姓名或脱敏称呼', trigger: 'blur' }],
        age: [{ required: true, type: 'number', message: '请填写年龄', trigger: 'blur' }]
      }
    }
  },
  computed: {
    patient() { return demoState.patient },
    custom() { return !!demoState.intake || Object.keys(demoState.files).length > 0 },
    savedNote() { return this.patient.note },
    bundle: currentBundle,
    signedReport() { return this.bundle.reports.find(item => item.status === 'signed') },
    hasCfp() { return this.bundle.images.some(image => image.modality === 'CFP') || !!(demoState.files.rightCfp || demoState.files.leftCfp) },
    hasOct() { return this.bundle.images.some(image => image.modality === 'OCT') || !!(demoState.files.rightOct || demoState.files.leftOct) }
  },
  watch: { patient() { this.editing = false } },
  methods: {
    startEdit() { this.draft = { ...this.patient }; this.note = this.savedNote; this.editing = true },
    save() {
      this.$refs.form.validate(valid => {
        if (!valid) return
        updatePatient({ ...this.draft, note: this.note })
        this.editing = false
        this.$message.success('合成档案已更新，相关页面同步显示。')
      })
    }
  }
}
</script>
<style scoped>
.history-note { margin-top: 28px; border-top: 1px solid var(--border); padding-top: 20px; }
.history-note h3 { margin: 0 0 8px; font-size: 14px; }
.history-note p { margin: 0; color: var(--muted); white-space: pre-wrap; overflow-wrap: anywhere; }
.record-source { margin-top: 28px; padding: 10px 12px; background: var(--page); border-radius: 5px; font-size: 12px; color: var(--muted); }
.record-source i { margin-right: 6px; }
.completeness-list { padding: 4px 24px; }
.completeness-list > div { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 17px 0; border-bottom: 1px solid #E7EEEB; font-size: 13px; }
.completeness-list i { margin-right: 9px; color: var(--input-border); font-size: 17px; }
.completeness-note { margin: 12px 24px 22px; color: var(--muted); font-size: 13px; }
@media (max-width: 1100px) { .detail-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
