<template>
  <main class="clinical-page">
    <patient-strip><template slot="tools"><el-button type="primary" icon="el-icon-upload2" @click="$router.push('/screening/intake')">补全采集资料</el-button></template></patient-strip>
    <demo-notice text="档案为合成病例，编辑同步到各业务页面，并在当前浏览器保留。" />
    <el-tabs v-model="activeTab" class="record-tabs">
      <el-tab-pane label="基础信息与糖尿病史" name="basic"><left-page /></el-tab-pane>
      <el-tab-pane label="双眼筛查记录" name="history"><right-page /></el-tab-pane>
    </el-tabs>
  </main>
</template>
<script>
import DemoNotice from '@/components/DemoNotice'
import PatientStrip from '@/components/PatientStrip'
import LeftPage from './LeftPage'
import RightPage from './RightPage'
export default {
  name: 'Personal',
  components: { DemoNotice, PatientStrip, LeftPage, RightPage },
  data() { return { activeTab: 'basic' } }
}
</script>
<style scoped>
.record-tabs /deep/ .el-tabs__header { margin-bottom: 20px; }
</style>
