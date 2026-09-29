<template>
  <div class="left-page">
    <!-- 顶部头像区 -->
    <div class="header">
      <div class="avatar">
        <el-upload v-if="isEditing" class="avatar-uploader" action="" :show-file-list="false"
        :before-upload="beforeAvatarUpload" :on-change="handleAvatarChange" :auto-upload="false">
          <img v-if="formData.avatar" :src="formData.avatar" class="avatar" />
          <i v-else class="el-icon-plus avatar-uploader-icon"></i>
        </el-upload>
        <img v-else :src="formData.avatar || defaultAvatar" class="avatar" />
      </div>
      <span class="username">{{ formData.name }}</span>

      <el-button v-if="!isEditing" type="primary" size="mini" @click="enterEdit">编辑</el-button>
      <template v-else>
        <el-button type="warning" size="mini" @click="cancelConfirm">退出编辑</el-button>
        <el-button type="success" size="mini" @click="save">保存</el-button>
      </template>
    </div>

    <!-- 信息分块 -->
    <div class="title1">
      <h3>基本信息</h3>
      <h3>联系信息</h3>
    </div>
    <div class="info-grid">
      <div class="card1">
        <div class="field">
            <label>姓名</label>
            <span v-if="!isEditing">{{ formData.name }}</span>
            <el-input v-else v-model="formData.name" size="small" />
        </div>
        <div class="field">
            <label>性别</label>
            <span v-if="!isEditing">{{ formData.gender }}</span>
            <el-input v-else v-model="formData.gender" size="small" />
        </div>
        <div class="field">
            <label>年龄</label>
            <span v-if="!isEditing">{{ formData.age }}</span>
            <el-input v-else v-model="formData.age" size="small" type="number" />
        </div>
        <div class="field">
            <label>血型</label>
            <span v-if="!isEditing">{{ formData.bloodType }}</span>
            <el-input v-else v-model="formData.bloodType" size="small" />
        </div>
        <div class="field">
            <label>身高</label>
            <span v-if="!isEditing">{{ formData.height }} cm</span>
            <el-input v-else v-model="formData.height" size="small" type="number" />
        </div>
        <div class="field">
            <label>体重</label>
            <span v-if="!isEditing">{{ formData.weight }} kg</span>
            <el-input v-else v-model="formData.weight" size="small" type="number" />
        </div>
      </div>
      <div class="card1">
        <div class="field">
            <label>电话</label>
            <span v-if="!isEditing">{{ formData.phone }}</span>
            <el-input v-else v-model="formData.phone" size="small" type="tel" />
        </div>
        <div class="field">
            <label>邮箱</label>
            <span v-if="!isEditing">{{ formData.email }}</span>
            <el-input v-else v-model="formData.email" size="small" type="email" />
        </div>
        <div class="field">
            <label>紧急联系人</label>
            <span v-if="!isEditing">{{ formData.emergencyContact }}</span>
            <el-input v-else v-model="formData.emergencyContact" size="small" />
        </div>
        <div class="field">
            <label>紧急电话</label>
            <span v-if="!isEditing">{{ formData.emergencyPhone }}</span>
            <el-input v-else v-model="formData.emergencyPhone" size="small" type="tel" />
        </div>
        <div class="field">
            <label>住址</label>
            <span v-if="!isEditing">{{ formData.address }}</span>
            <el-input v-else v-model="formData.address" size="small" />
        </div>
      </div>
    </div>
    
    <!-- 过敏史和家族病史 -->
    <div class="medical-history-section">
      <div class="history-title">
        <h3>过敏史</h3>
        <el-button 
          v-if="isEditing" 
          type="text" 
          size="mini" 
          @click="addAllergy"
          class="add-btn"
        >
          <i class="el-icon-plus"></i> 添加
        </el-button>
      </div>
      
      <!-- 过敏史列表 -->
      <el-card class="history-card">
        <div v-if="allergies.length === 0" class="empty-state">
          <i class="el-icon-circle-check-outline"></i>
          <p>无过敏史记录</p >
        </div>
        <div v-else class="history-list">
          <div class="history-item" v-for="(item, index) in allergies" :key="index">
            <div class="history-content">
              <!-- 编辑模式：下拉选择框+输入框 -->
              <div v-if="isEditing" class="edit-input-group">
                <!-- 过敏类型下拉选择 -->
                <el-select 
                  v-model="item.type" 
                  size="mini" 
                  placeholder="选择过敏类型" 
                  class="edit-input type-input"
                >
                  <el-option label="药物过敏" value="药物过敏"></el-option>
                  <el-option label="食物过敏" value="食物过敏"></el-option>
                  <el-option label="花粉过敏" value="花粉过敏"></el-option>
                  <el-option label="尘螨过敏" value="尘螨过敏"></el-option>
                  <el-option label="其他过敏" value="其他过敏"></el-option>
                </el-select>
                <!-- 具体过敏原输入框 -->
                <el-input 
                  v-model="item.detail" 
                  size="mini" 
                  placeholder="具体过敏原（如：青霉素/海鲜）" 
                  class="edit-input detail-input"
                />
                <!-- 发现日期选择器 -->
                <el-date-picker 
                  v-model="item.date" 
                  size="mini" 
                  type="month" 
                  placeholder="选择发现日期" 
                  class="edit-input date-input"
                  value-format="yyyy-MM"
                />
              </div>
              <!-- 非编辑模式：显示文本 -->
              <div v-else>
                <el-tag type="danger" size="mini">{{ item.type }}</el-tag>
                <span class="history-detail">{{ item.detail }}</span>
                <span class="history-date">{{ item.date }}</span>
              </div>
            </div>
            <el-button 
              v-if="isEditing" 
              type="text" 
              size="mini" 
              @click="removeItem(allergies, index)"
              class="delete-btn"
            >
              <i class="el-icon-delete"></i>
            </el-button>
          </div>
        </div>
      </el-card>

      <div class="history-title">
        <h3>家族病史</h3>
        <el-button 
          v-if="isEditing" 
          type="text" 
          size="mini" 
          @click="addFamilyDisease"
          class="add-btn"
        >
          <i class="el-icon-plus"></i> 添加
        </el-button>
      </div>
      
      <!-- 家族病史列表 -->
      <el-card class="history-card">
        <div v-if="familyDiseases.length === 0" class="empty-state">
          <i class="el-icon-circle-check-outline"></i>
          <p>无家族病史记录</p >
        </div>
        <div v-else class="history-list">
          <div class="history-item" v-for="(item, index) in familyDiseases" :key="index">
            <div class="history-content">
              <!-- 编辑模式：下拉选择框+输入框 -->
              <div v-if="isEditing" class="edit-input-group">
                <!-- 亲属关系下拉选择 -->
                <el-select 
                  v-model="item.relation" 
                  size="mini" 
                  placeholder="选择亲属关系" 
                  class="edit-input type-input"
                >
                  <el-option label="父亲" value="父亲"></el-option>
                  <el-option label="母亲" value="母亲"></el-option>
                  <el-option label="祖父" value="祖父"></el-option>
                  <el-option label="祖母" value="祖母"></el-option>
                  <el-option label="兄弟姐妹" value="兄弟姐妹"></el-option>
                  <el-option label="其他亲属" value="其他亲属"></el-option>
                </el-select>
                <!-- 疾病名称输入框 -->
                <el-input 
                  v-model="item.disease" 
                  size="mini" 
                  placeholder="疾病名称（如：高血压/糖尿病）" 
                  class="edit-input detail-input"
                />
                <!-- 确诊日期选择器 -->
                <el-date-picker 
                  v-model="item.diagnoseDate" 
                  size="mini" 
                  type="month" 
                  placeholder="选择确诊日期" 
                  class="edit-input date-input"
                  value-format="yyyy-MM"
                />
              </div>
              <!-- 非编辑模式：显示文本 -->
              <div v-else>
                <el-tag type="warning" size="mini">{{ item.relation }}</el-tag>
                <span class="history-detail">{{ item.disease }}</span>
                <span class="history-date">{{ item.diagnoseDate }}</span>
              </div>
            </div>
            <el-button 
              v-if="isEditing" 
              type="text" 
              size="mini" 
              @click="removeItem(familyDiseases, index)"
              class="delete-btn"
            >
              <i class="el-icon-delete"></i>
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LeftPage',
  data() {
    return {
      isEditing: false,
      defaultAvatar: require('@/assets/profileavatar.jpg'),
      formData: {
        avatar: '',
        name: '示例患者',
        gender: '女',
        age: 48,
        bloodType: 'A',
        height: 160,
        weight: 60,
        phone: '示例电话',
        email: 'demo@example.invalid',
        emergencyContact: '示例联系人',
        emergencyPhone: '示例联系电话',
        address: '示例地址'
      },
      // 过敏史数据
      allergies: [],
      // 家族病史数据
      familyDiseases: [
        {
          relation: '示例亲属',
          disease: '示例病史',
          diagnoseDate: '示例日期'
        }
      ],
      backupData: null,
      backupAllergies: [],
      backupFamilyDiseases: []
    }
  },
  methods: {
    // 进入编辑模式 - 备份数据
    enterEdit() {
      this.backupData = { ...this.formData }
      this.backupAllergies = JSON.parse(JSON.stringify(this.allergies))
      this.backupFamilyDiseases = JSON.parse(JSON.stringify(this.familyDiseases))
      this.isEditing = true
    },
    // 保存修改
    save() {
      // 实际应用中可添加接口请求，提交数据到后端
      this.isEditing = false
      this.$message.success('保存成功!')
    },
    // 取消编辑确认
    cancelConfirm() {
      this.$confirm('确定要退出编辑吗？未保存的修改将丢失。', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.cancel()
      }).catch(() => { })
    },
    // 取消编辑（恢复备份）
    cancel() {
      this.isEditing = false
      if (this.backupData) {
        this.formData = { ...this.backupData }
        this.allergies = JSON.parse(JSON.stringify(this.backupAllergies))
        this.familyDiseases = JSON.parse(JSON.stringify(this.backupFamilyDiseases))
      }
      this.$message.info('已退出编辑，修改未保存')
    },
    // 添加过敏史
    addAllergy() {
      this.allergies.push({
        type: '',
        detail: '',
        date: ''
      })
    },
    // 添加家族病史
    addFamilyDisease() {
      this.familyDiseases.push({
        relation: '',
        disease: '',
        diagnoseDate: ''
      })
    },
    // 删除条目
    removeItem(list, index) {
      list.splice(index, 1)
    },
    // 头像上传前校验
    beforeAvatarUpload(file) {
      const isImage = file.type === 'image/jpeg' || file.type === 'image/png'
      const isLt2M = file.size / 1024 / 1024 < 2
      if (!isImage) this.$message.error('上传头像图片只能是JPG/PNG格式！')
      if (!isLt2M) this.$message.error('上传头像图片大小不可超过2MB！')
      return isImage && isLt2M
    },
    // 处理头像预览
    handleAvatarChange(file) {
      const rawFile = file.raw || file
      if (!rawFile) return

      const reader = new FileReader()
      reader.onload = e => {
        this.formData.avatar = e.target.result
      }
      reader.readAsDataURL(rawFile)
    }
  }
}
</script>

<style scoped>
.left-page {
  width: 90%;
  padding: 20px;
}
.header {
  display: flex;
  height: 90px;
  align-items: center;
  background-color: #fff;
  padding: 12px 20px;
  border-radius: 8px;
  margin-top: 0px;
  margin-bottom: 10px;
}
.title1 {
  display: flex;
  justify-content: space-around;
  margin: 22px 0;
}
.title1 h3 {
  margin: 0;
  color: #333;
}
.avatar {
  width: 50px;
  height: 50px;
  background: #409eff;
  border-radius: 50%;
  margin-right: 12px;
  object-fit: cover;
}
.avatar-uploader {
  border: 1px solid #409eff;
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.avatar-uploader-icon {
  font-size: 25px;
  color: #409eff;
}
.username {
  font-size: 18px;
  font-weight: bold;
  margin-right: auto;
}
.field {
  display: flex;
  margin-bottom: 12px;
  align-items: center;
}
.field label {
  width: 100px;
  margin-right: 16px;
  font-weight: bold;
  white-space: nowrap;
  color: #333;
}
.field span {
  flex: 1;
  line-height: 32px;
  min-height: 32px;
  color: #555;
}
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.card1 {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  min-height: 260px;
  box-sizing: border-box;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.card1:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.header:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
/* 病史部分样式 */
.medical-history-section {
  margin-top: 20px;
}
.history-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 15px 0 10px;
  padding: 0 10px;
}
.history-title h3 {
  color: #333;
  margin:10px 0;
}
.add-btn {
  color: #409eff;
  padding: 0;
}
/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 30px 0;
  color: #8c8c8c;
}
.empty-state i {
  font-size: 36px;
  margin-bottom: 10px;
  color: #c9e2ff;
}
/* 列表样式 */
.history-card {
  margin-bottom: 20px;
  border-radius: 8px;
}
.history-list {
  padding: 5px 0;
}
.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px dashed #f0f0f0;
}
.history-item:last-child {
  border-bottom: none;
}
.history-content {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}
.history-detail {
  flex: 1;
  color: #333;
  margin-right: 8px;
}
.history-date {
  color: #8c8c8c;
  font-size: 12px;
  white-space: nowrap;
}
.delete-btn {
  color: #f56c6c;
  padding: 0;
  visibility: hidden;
}
.history-item:hover .delete-btn {
  visibility: visible;
}
/* 编辑模式输入框样式 */
.edit-input-group {
  display: flex;
  gap: 10px;
  width: 100%;
  align-items: center;
}
.edit-input {
  height: 32px;
}
.type-input {
  width: 120px;
}
.detail-input {
  flex: 1;
}
.date-input {
  width: 120px;
}
/* 调整标签与文字的间距 */
.el-tag {
  margin-right: 8px;
}
</style>