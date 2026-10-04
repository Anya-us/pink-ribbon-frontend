<template>
  <header class="navbar">
    <hamburger :is-active="sidebar.opened" @toggleClick="toggleSideBar" />
    <el-autocomplete
      v-model="query"
      class="patient-search"
      :fetch-suggestions="searchPatients"
      :trigger-on-focus="false"
      :highlight-first-item="true"
      :debounce="80"
      placeholder="搜索患者姓名或病例编号"
      prefix-icon="el-icon-search"
      aria-label="搜索患者姓名或病例编号"
      clearable
      @select="openPatient"
    >
      <template slot-scope="{ item }">
        <span class="search-patient-name">{{ item.patient.name }}<span>{{ item.patient.sex }} · {{ item.patient.age }} 岁</span></span>
        <span class="search-patient-id">{{ item.patient.id }}</span>
      </template>
    </el-autocomplete>
    <div class="navbar-right">
      <el-tooltip content="转诊与随访" placement="bottom">
        <button class="toolbar-button followup-button" type="button" aria-label="查看转诊与随访" @click="navigate('/followup/index')"><i class="el-icon-date" aria-hidden="true" /></button>
      </el-tooltip>
      <el-popover v-model="tasksVisible" placement="bottom-end" :width="300" trigger="click">
        <div class="toolbar-popover">
          <h3>待办工作</h3>
          <p>根据当前演示病例汇总</p>
          <button type="button" @click="openReview"><span>待医生复核</span><strong>{{ reviewCount }} 例<i class="el-icon-arrow-right" /></strong></button>
          <button type="button" @click="openIntake"><span>待补全影像</span><strong>{{ collectionCount }} 例<i class="el-icon-arrow-right" /></strong></button>
          <button type="button" @click="openFollowup"><span>随访准备</span><strong>{{ followupCount }} 例<i class="el-icon-arrow-right" /></strong></button>
        </div>
        <button slot="reference" class="toolbar-button" type="button" :aria-expanded="String(tasksVisible)" :aria-label="'查看待办工作，待复核 ' + reviewCount + ' 例'"><i class="el-icon-bell" aria-hidden="true" /><span v-if="reviewCount" class="notification-dot" /></button>
      </el-popover>
      <el-popover v-model="helpVisible" placement="bottom-end" :width="300" trigger="click">
        <div class="toolbar-popover workspace-help">
          <h3>筛查工作空间</h3>
          <p>依次完成资料采集、共识评估、医生复核与处置随访。</p>
          <div class="help-note">当前为演示环境，病例及候选分级均为示例。影像文件仅在本地选择与预览。</div>
          <router-link class="text-link" to="/patient/help" @click.native="helpVisible = false">查看流程说明 <i class="el-icon-right" /></router-link>
        </div>
        <button slot="reference" class="toolbar-button help-button" type="button" :aria-expanded="String(helpVisible)" aria-label="查看工作空间说明"><i class="el-icon-question" aria-hidden="true" /></button>
      </el-popover>
      <el-dropdown trigger="click" @command="handleCommand">
        <button class="account-button" type="button" aria-label="打开账户菜单">
          <span class="account-mark"><i class="el-icon-user" aria-hidden="true" /></span>
          <span v-if="device !== 'mobile'" class="account-name">{{ name }}</span>
          <i class="el-icon-arrow-down" aria-hidden="true" />
        </button>
        <el-dropdown-menu slot="dropdown">
          <el-dropdown-item command="dashboard">诊疗工作台</el-dropdown-item>
          <el-dropdown-item command="personal">当前患者档案</el-dropdown-item>
          <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </div>
  </header>
</template>
<script>
import { mapGetters } from 'vuex'
import Hamburger from '@/components/Hamburger'
import { patients, selectPatient, contextQuery } from '@/data/retina-demo'
export default {
  components: { Hamburger },
  data() { return { query: '', tasksVisible: false, helpVisible: false } },
  computed: {
    ...mapGetters(['sidebar', 'device', 'name']),
    reviewCount() { return patients.filter(item => item.status.includes('复核')).length },
    collectionCount() { return patients.filter(item => !item.cfp).length },
    followupCount() { return patients.filter(item => item.status === '随访准备').length }
  },
  methods: {
    toggleSideBar() { this.$store.dispatch('app/toggleSideBar') },
    navigate(path) {
      const target = { path, query: path === '/dashboard' ? {} : contextQuery() }
      if (this.$route.path !== path || this.$route.query.patientId !== target.query.patientId || this.$route.query.examinationId !== target.query.examinationId) this.$router.push(target)
    },
    searchPatients(query, callback) {
      const value = query.trim().toLowerCase()
      callback(value ? patients.filter(item => (item.name + item.id).toLowerCase().includes(value)).map(patient => ({ value: patient.name + ' · ' + patient.id, patient })) : [])
    },
    openPatient(item) {
      selectPatient(item.patient)
      this.query = ''
      this.navigate('/patients/index')
    },
    openReview() {
      selectPatient(patients.find(item => item.tone === 'danger') || patients.find(item => item.status.includes('复核')))
      this.tasksVisible = false
      this.navigate('/screening/consensus')
    },
    openIntake() {
      selectPatient(patients.find(item => !item.cfp))
      this.tasksVisible = false
      this.navigate('/screening/intake')
    },
    openFollowup() {
      selectPatient(patients.find(item => item.status === '随访准备'))
      this.tasksVisible = false
      this.navigate('/followup/index')
    },
    async handleCommand(command) {
      if (command === 'logout') {
        await this.$store.dispatch('user/logout')
        selectPatient(patients[0])
        this.$router.push('/login?redirect=' + encodeURIComponent(this.$route.fullPath))
      } else {
        this.navigate(command === 'personal' ? '/patients/index' : '/dashboard')
      }
    }
  }
}
</script>
<style scoped>
.navbar { height: var(--navbar-height); display: flex; align-items: center; gap: 20px; background: var(--panel); border-bottom: 1px solid var(--border); padding: 0 30px; }
.patient-search { width: 350px; max-width: 42%; }
.patient-search ::v-deep .el-input__inner { background: var(--page); border: 1px solid transparent; border-radius: 24px; height: 44px; padding-left: 40px; }
.patient-search ::v-deep .el-input__inner:focus { border-color: var(--primary); }
.patient-search ::v-deep .el-input__prefix { left: 13px; color: var(--muted); }
.search-patient-name { display: block; color: var(--heading); line-height: 1.5; padding-top: 7px; }
.search-patient-name span { color: var(--muted); margin-left: 12px; font-size: 12px; }
.search-patient-id { display: block; color: var(--muted); line-height: 1.5; padding-bottom: 7px; font-size: 12px; }
.navbar-right { display: flex; align-items: center; gap: 12px; margin-left: auto; flex-shrink: 0; }
.toolbar-button { width: 40px; height: 40px; display: grid; place-items: center; position: relative; border: 0; border-radius: 50%; background: var(--page); color: var(--muted); font-size: 19px; cursor: pointer; }
.toolbar-button:hover, .toolbar-button[aria-expanded="true"] { color: var(--primary); background: var(--primary-soft); }
.notification-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--rose); position: absolute; top: 1px; right: 2px; box-shadow: 0 0 0 2px var(--panel); }
.toolbar-popover h3 { margin: 0; color: var(--heading); font-size: 16px; }
.toolbar-popover p { color: var(--muted); font-size: 12px; margin: 5px 0 12px; line-height: 1.7; }
.toolbar-popover button { display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 13px 0; border: 0; border-top: 1px solid var(--border); background: transparent; color: var(--text); cursor: pointer; font-size: 13px; }
.toolbar-popover button:hover { color: var(--primary); }
.toolbar-popover strong { font-weight: 500; color: var(--primary); }
.toolbar-popover strong i { margin-left: 8px; }
.help-note { border-radius: 8px; background: var(--page); padding: 12px; font-size: 12px; line-height: 1.8; color: var(--muted); margin-bottom: 12px; }
.workspace-help .text-link { font-size: 13px; }
.account-button { border: none; background: transparent; display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--text); padding: 4px; cursor: pointer; border-radius: 24px; margin-left: 6px; }
.account-button:hover { background: var(--primary-soft); }
.account-mark { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 50%; background: var(--primary-soft); color: var(--primary); font-size: 21px; }
.account-button .el-icon-arrow-down { font-size: 11px; }
@media (max-width: 1050px) { .account-name { display: none; } .patient-search { max-width: none; width: 300px; } .navbar { gap: 14px; } .navbar-right { gap: 8px; } }
@media (max-width: 767px) {
  .navbar { padding: 0 16px; gap: 10px; }
  .patient-search { flex: 1; min-width: 0; width: auto; }
  .patient-search ::v-deep .el-input__inner { font-size: 12px; height: 40px; padding-left: 32px; padding-right: 26px; }
  .patient-search ::v-deep .el-input__prefix { left: 7px; }
  .navbar-right { gap: 6px; }
  .followup-button, .help-button, .account-button .el-icon-arrow-down { display: none; }
  .toolbar-button { width: 34px; height: 34px; font-size: 18px; }
  .account-button { padding: 0; margin: 0; }
  .account-mark { width: 34px; height: 34px; font-size: 18px; }
  .navbar ::v-deep .navigation-toggle { width: 34px; height: 34px; }
}
</style>
