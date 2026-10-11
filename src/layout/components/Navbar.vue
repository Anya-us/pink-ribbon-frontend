<template>
  <header class="navbar">
    <div class="navbar-page-title" aria-live="polite">{{ pageTitle }}</div>
    <div class="navbar-right">
      <el-tooltip content="转诊与随访" placement="bottom">
        <button class="toolbar-button followup-button" type="button" aria-label="查看转诊与随访" @click="navigate('/followup/index')"><i class="el-icon-date" aria-hidden="true" /></button>
      </el-tooltip>
      <el-popover v-model="tasksVisible" placement="bottom-end" :width="300" trigger="click">
        <div class="toolbar-popover">
          <h3>待办工作</h3>
          <p>根据当前病例记录汇总</p>
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
          <div class="help-note">当前病例及候选分级均为样本记录。影像文件仅在本地选择与预览。</div>
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
import { patients, selectPatient, contextQuery } from '@/data/retina-demo'
export default {
  data() { return { tasksVisible: false, helpVisible: false } },
  computed: {
    ...mapGetters(['device', 'name']),
    pageTitle() {
      return [...this.$route.matched].reverse().map(route => route.meta && route.meta.title).find(Boolean) || '糖网诊疗'
    },
    reviewCount() { return patients.filter(item => item.status.includes('复核')).length },
    collectionCount() { return patients.filter(item => !item.cfp).length },
    followupCount() { return patients.filter(item => item.status === '随访准备').length }
  },
  methods: {
    navigate(path) {
      const target = { path, query: path === '/dashboard' ? {} : contextQuery() }
      if (this.$route.path !== path || this.$route.query.patientId !== target.query.patientId || this.$route.query.examinationId !== target.query.examinationId) this.$router.push(target)
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
.navbar-page-title { min-width: 0; color: var(--heading); font-size: 20px; font-weight: 650; letter-spacing: .04em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.navbar-right { display: flex; align-items: center; gap: 12px; margin-left: auto; flex-shrink: 0; }
.toolbar-button { width: 40px; height: 40px; display: grid; place-items: center; position: relative; border: 0; border-radius: 50%; background: var(--page); color: var(--muted); font-size: 19px; cursor: pointer; }
.toolbar-button:hover, .toolbar-button[aria-expanded="true"] { color: var(--primary); background: var(--primary-soft); }
.notification-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--rose); position: absolute; top: 1px; right: 2px; box-shadow: 0 0 0 2px var(--panel); }
.toolbar-popover h3 { margin: 0; color: var(--heading); font-size: 16px; }
.toolbar-popover p { color: var(--muted); font-size: 14px; margin: 5px 0 12px; line-height: 1.7; }
.toolbar-popover button { display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 13px 0; border: 0; border-top: 1px solid var(--border); background: transparent; color: var(--text); cursor: pointer; font-size: 15px; }
.toolbar-popover button:hover { color: var(--primary); }
.toolbar-popover strong { font-weight: 500; color: var(--primary); }
.toolbar-popover strong i { margin-left: 8px; }
.help-note { border-radius: 8px; background: var(--page); padding: 12px; font-size: 14px; line-height: 1.8; color: var(--muted); margin-bottom: 12px; }
.workspace-help .text-link { font-size: 14px; }
.account-button { border: none; background: transparent; display: flex; align-items: center; gap: 10px; font-size: 15px; color: var(--text); padding: 4px; cursor: pointer; border-radius: 24px; margin-left: 6px; }
.account-button:hover { background: var(--primary-soft); }
.account-mark { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 50%; background: var(--primary-soft); color: var(--primary); font-size: 21px; }
.account-button .el-icon-arrow-down { font-size: 11px; }
@media (max-width: 1050px) { .account-name { display: none; } .navbar { gap: 14px; } .navbar-right { gap: 8px; } }
@media (max-width: 767px) {
  .navbar { padding: 0 16px; gap: 10px; }
  .navbar-page-title { flex: 1; font-size: 15px; }
  .navbar-right { gap: 6px; }
  .followup-button, .help-button, .account-button .el-icon-arrow-down { display: none; }
  .toolbar-button { width: 34px; height: 34px; font-size: 18px; }
  .account-button { padding: 0; margin: 0; }
  .account-mark { width: 34px; height: 34px; font-size: 18px; }
}
</style>
