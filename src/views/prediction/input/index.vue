<template>
  <div class="form-wrapper">
    <div class="form-container">
      
      <div class="header">
        <i class="el-icon-edit" />
        <span class="header-text">多模态数据采集</span>
      </div>
      <p class="form-description">请填写您的个人信息并上传相关多模态数据，系统将对您的健康状况进行全面评估</p>

      <el-steps :active="activeStep" finish-status="success" class="steps-container">
        <el-step title="基本信息"></el-step>
        <el-step title="健康状况"></el-step>
        <el-step title="数据上传"></el-step>
      </el-steps>

      <div class="steps-content">
        <!-- 步骤1：基本信息-->
        <div v-show="activeStep === 0" class="step-pane">
          <el-form class="custom-form" :model="formData" label-width="120px" @submit.prevent="submitData">
            <el-form-item label="姓名" class="form-item-spacing">
              <el-input v-model="formData.name" placeholder="请输入真实姓名" prefix-icon="el-icon-user" />
            </el-form-item>

            <el-form-item label="年龄" class="form-item-spacing">
              <el-input-number v-model="formData.age" :min="0" :max="120" />
            </el-form-item>

            <el-form-item label="性别" class="form-item-spacing">
              <el-radio-group v-model="formData.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="联系方式" class="form-item-spacing">
              <el-input v-model="formData.phoneNumber" placeholder="电话号码" prefix-icon="el-icon-phone" />
            </el-form-item>
            <el-form-item class="form-item-spacing">
              <el-input v-model="formData.email" placeholder="电子邮箱" prefix-icon="el-icon-message" class="mt-10" />
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤2：健康状况-->
        <div v-show="activeStep === 1" class="step-pane">
          <el-form class="custom-form" :model="formData" label-width="120px" @submit.prevent="submitData">
            <el-form-item label="家族病史">
              <el-switch v-model="formData.hasDisease" active-text="有" inactive-text="无" active-color="#25ed17" />
            </el-form-item>

            <el-form-item v-if="formData.hasDisease" label="具体疾病名称">
              <el-input v-model="formData.diseaseName" placeholder="请输入疾病名称" />
            </el-form-item>

            <el-form-item v-if="formData.hasDisease" label="患病亲属关系">
              <el-select v-model="formData.relativeWithDisease" placeholder="请选择">
                <el-option label="父母" value="父母" />
                <el-option label="祖父" value="祖父" />
                <el-option label="兄弟姐妹" value="兄弟姐妹" />
                <el-option label="其他亲属" value="其他亲属" />
              </el-select>
            </el-form-item>

            <el-form-item label="症状描述">
              <el-input v-model="formData.symptomDescription" type="textarea" rows="4" placeholder="请描述您的症状" />
            </el-form-item>

            <el-form-item label="症状开始时间">
              <el-date-picker v-model="formData.illnessDate" type="date" placeholder="选择日期" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="既往病史">
              <el-input v-model="formData.pastIllnesses" placeholder="请输入既往病史，多个病史请用逗号分隔" />
            </el-form-item>

            <el-form-item label="正在服用的药物">
              <el-input v-model="formData.currentMedications" placeholder="请输入当前正在服用的药物，多个药物请用逗号分隔" />
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤3：数据上传-->
        <div v-show="activeStep === 2" class="step-pane">
          <div class="upload-section">
            <p class="upload-title">多模态数据上传<span class="required-hint">*</span></p>
            <p class="upload-description">请上传以下相关医疗检查数据，这将帮助我们进行更精确的诊断与数字孪生模型构建</p>

            <div class="upload-grid">
              <div class="upload-card" :class="{ 'has-file': hasFile('MRI') }">
                <div class="upload-card-inner" @click="triggerUpload('MRI')">
                  <div v-if="!hasFile('MRI')" class="upload-icon">
                    <i class="el-icon-upload" />
                  </div>
                  <div v-else class="file-preview">
                    <i class="el-icon-document" />
                    <span class="file-name">{{ getFileName('MRI') }}</span>
                  </div>
                  <div class="upload-text">
                    <span class="upload-title">MRI影像</span>
                    <span class="upload-desc">支持 DICOM、JPG、PNG 格式</span>
                  </div>
                </div>
                <el-button v-if="hasFile('MRI')" type="danger" size="mini" class="remove-file" icon="el-icon-delete" circle @click.stop="removeFile('MRI')"></el-button>
              </div>

              <div class="upload-card" :class="{ 'has-file': hasFile('PET') }">
                <div class="upload-card-inner" @click="triggerUpload('PET')">
                  <div v-if="!hasFile('PET')" class="upload-icon">
                    <i class="el-icon-upload" />
                  </div>
                  <div v-else class="file-preview">
                    <i class="el-icon-document" />
                    <span class="file-name">{{ getFileName('PET') }}</span>
                  </div>
                  <div class="upload-text">
                    <span class="upload-title">PET影像</span>
                    <span class="upload-desc">支持 DICOM、JPG、PNG 格式</span>
                  </div>
                </div>
                <el-button v-if="hasFile('PET')" type="danger" size="mini" class="remove-file" icon="el-icon-delete" circle @click.stop="removeFile('PET')"></el-button>
              </div>

              <div class="upload-card" :class="{ 'has-file': hasFile('clinicalData') }">
                <div class="upload-card-inner" @click="triggerUpload('clinicalData')">
                  <div v-if="!hasFile('clinicalData')" class="upload-icon">
                    <i class="el-icon-upload" />
                  </div>
                  <div v-else class="file-preview">
                    <i class="el-icon-document" />
                    <span class="file-name">{{ getFileName('clinicalData') }}</span>
                  </div>
                  <div class="upload-text">
                    <span class="upload-title">临床数据</span>
                    <span class="upload-desc">支持 PDF、DOC、XLS 格式</span>
                  </div>
                </div>
                <el-button v-if="hasFile('clinicalData')" type="danger" size="mini" class="remove-file" icon="el-icon-delete" circle @click.stop="removeFile('clinicalData')"></el-button>
              </div>

              <div class="upload-card" :class="{ 'has-file': hasFile('other') }">
                <div class="upload-card-inner" @click="triggerUpload('other')">
                  <div v-if="!hasFile('other')" class="upload-icon">
                    <i class="el-icon-upload" />
                  </div>
                  <div v-else class="file-preview">
                    <i class="el-icon-document" />
                    <span class="file-name">{{ getFileName('other') }}</span>
                  </div>
                  <div class="upload-text">
                    <span class="upload-title">其他数据</span>
                    <span class="upload-desc">其他相关医疗数据</span>
                  </div>
                </div>
                <el-button v-if="hasFile('other')" type="danger" size="mini" class="remove-file" icon="el-icon-delete" circle @click.stop="removeFile('other')"></el-button>
              </div>
            </div>

            <div class="upload-note">
              <el-input v-model="formData.note" type="textarea" placeholder="备注：请补充说明上传文件的相关信息" rows="3" />
            </div>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <el-button v-if="activeStep > 0" @click="previousStep">上一步</el-button>
        <el-button v-if="activeStep < 2" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-if="activeStep === 2" type="success" @click="submitData" icon="el-icon-upload2" :loading="isSubmitting">{{ isSubmitting ? '提交中...' : '提交数据' }}</el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeStep: 0,
      formData: {
        name: '',
        age: null,
        gender: '',
        phoneNumber: '',
        email: '',
        hasDisease: false,
        diseaseName: '',
        relativeWithDisease: '',
        note: '',
        symptomDescription: '',
        illnessDate: null,
        pastIllnesses: '',
        currentMedications: '',
        uploadedFiles: {
          MRI: null,
          PET: null,
          clinicalData: null,
          other: null
        }
      },
      isSubmitting: false
    }
  },
  methods: {
    nextStep() {
      if (this.activeStep < 2) {
        this.activeStep++
      }
    },
    previousStep() {
      if (this.activeStep > 0) {
        this.activeStep--
      }
    },
    hasFile(type) {
      return this.formData.uploadedFiles[type] !== null
    },
    getFileName(type) {
      if (this.formData.uploadedFiles[type]) {
        return this.formData.uploadedFiles[type].name
      }
      return ''
    },
    triggerUpload(type) {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = type === 'clinicalData' ? '.pdf,.doc,.docx,.xls,.xlsx' : '.dcm,.jpg,.jpeg,.png'
      input.onchange = (e) => this.handleFileUpload(e, type)
      input.click()
    },
    handleFileUpload(event, type) {
      const file = event.target.files[0]
      if (file) {
        this.formData.uploadedFiles[type] = file
        this.$message({
          message: `成功上传${file.name}`,
          type: 'success'
        })
      }
    },
    removeFile(type) {
      this.formData.uploadedFiles[type] = null
      this.$message({
        message: '文件已移除',
        type: 'info'
      })
    },
    submitData() {
      // 验证表单数据
      if (!this.formData.name) {
        this.$message.error('请输入姓名')
        this.activeStep = 0
        return
      }

      if (!this.formData.age) {
        this.$message.error('请输入年龄')
        this.activeStep = 0
        return
      }

      if (!this.formData.gender) {
        this.$message.error('请选择性别')
        this.activeStep = 0
        return
      }

      // 检查是否上传了至少一个文件
      const hasAnyFile = Object.values(this.formData.uploadedFiles).some(file => file !== null)
      if (!hasAnyFile) {
        this.$message.error('请至少上传一个多模态数据文件')
        this.activeStep = 2
        return
      }

      // 设置提交状态
      this.isSubmitting = true

      // 显示加载中通知
      const loading = this.$loading({
        lock: true,
        text: '数据提交中，请稍候...',
        spinner: 'el-icon-loading',
        background: 'rgba(255, 255, 255, 0.7)'
      })

      // 这里可以添加实际的数据提交逻辑，例如API调用
      // 模拟提交过程
      setTimeout(() => {
        // 关闭加载提示
        loading.close()
        
        // 重置提交状态
        this.isSubmitting = false
        
        // 显示成功消息
        this.$message({
          message: '您的数据已成功提交，正在前往诊断结果页面',
          type: 'success',
          duration: 3000,
          onClose: () => {
            // 成功回调中跳转，确保消息被用户看到后再跳转
            this.$router.push({ name: 'Assess'})
          }
        })
        
        // 保存表单数据到本地存储，以便在诊断页面使用
        try {
          // 我们只存储基本信息，不存储文件数据
          const storageData = {
            patientInfo: {
              name: this.formData.name,
              age: this.formData.age,
              gender: this.formData.gender,
              hasDisease: this.formData.hasDisease,
              symptomDescription: this.formData.symptomDescription
            },
            uploadTime: new Date().toISOString()
          }
          localStorage.setItem('patientData', JSON.stringify(storageData))
        } catch (e) {
          console.error('保存数据到本地存储时出错:', e)
        }
        
        // 备份通过路由跳转
        setTimeout(() => {
          this.$router.push( {name: 'Assess'} )
        }, 3500)
      }, 2000) // 模拟2秒的提交时间
    }
  }
}
</script>

<style scoped>
.form-wrapper {
  margin: 50px;
  background-color: #ffffff;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.form-container {
  max-width: 900px;
  margin: 0 auto;
  font-family: 'Arial', sans-serif;
  padding: 25px;
}

.header {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 40px;
  margin-bottom: 10px;
}

.header i {
  margin-top: 20px;
  font-size: 32px;
  color: #666;
  margin-right: 10px;
}

.header-text {
  margin-top: 20px;
  font-size: 24px;
  color: #333;
  font-weight: 600;
}

.form-description {
  text-align: center;
  color: #666;
  margin-bottom: 25px;
  font-size: 16px;
  line-height: 1.6;
}

.steps-container {
  margin-bottom: 30px;
}

.step-pane {
  animation: fadeIn 0.5s ease-in-out;
  min-height: 400px;
}

.custom-form .el-form-item {
  margin-bottom: 20px;
}

.form-item-spacing {
  margin-bottom: 25px;
}

.custom-form .el-input,
.custom-form .el-select,
.custom-form .el-input-number {
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.mt-10 {
  margin-top: 10px;
}

/* 上传区域样式 */
.upload-section {
  padding: 10px 0;
}

.upload-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.upload-description {
  color: #666;
  margin-bottom: 20px;
  font-size: 14px;
  line-height: 1.5;
}

.upload-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.upload-card {
  height: 180px;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  position: relative;
}

.upload-card:hover {
  border-color: #409EFF;
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.upload-card.has-file {
  border: 2px solid #67c23a;
  background-color: rgba(103, 194, 58, 0.05);
}

.upload-card-inner {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 15px;
  cursor: pointer;
}

.upload-icon {
  font-size: 36px;
  color: #909399;
  margin-bottom: 15px;
}

.upload-text {
  text-align: center;
}

.upload-text .upload-title {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.upload-text .upload-desc {
  display: block;
  font-size: 12px;
  color: #909399;
}

.file-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 10px;
}

.file-preview i {
  font-size: 32px;
  color: #67c23a;
  margin-bottom: 5px;
}

.file-name {
  font-size: 12px;
  color: #333;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-file {
  position: absolute;
  top: 5px;
  right: 5px;
  opacity: 0.7;
}

.remove-file:hover {
  opacity: 1;
}

.upload-note {
  margin-top: 15px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.required-hint {
  color: #F56C6C;
  margin-left: 5px;
}
</style>



