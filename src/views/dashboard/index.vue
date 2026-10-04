<template>
  <main class="clinical-page dashboard-page">
    <clinical-header title="诊疗工作台" description="糖尿病视网膜病变多模态筛查与管理">
      <span class="dashboard-date"><i class="el-icon-date" aria-hidden="true" />{{ today }}</span>
    </clinical-header>

    <section class="welcome-panel" aria-label="筛查工作入口">
      <div class="welcome-grid" aria-hidden="true" />
      <div class="welcome-copy">
        <h2>您好，{{ name }}</h2>
        <p>今天的筛查与复核，从这里开始。</p>
        <span class="welcome-modalities">眼底彩照 · OCT · 临床病史</span>
        <el-button class="welcome-button" icon="el-icon-plus" @click="$router.push('/screening/intake')">开始筛查</el-button>
      </div>
      <div class="welcome-orbit" aria-hidden="true" />
      <img :src="doctorImage" class="welcome-doctor" alt="" aria-hidden="true" width="1024" height="1536">
    </section>
    <demo-notice class="dashboard-demo-note" :text="'当前 ' + patients.length + ' 例为演示病例，图表由示例记录汇总；尚未连接真实诊疗服务。'" />

    <section class="metric-grid" aria-label="演示队列概况">
      <button v-for="metric in metrics" :key="metric.label" type="button" class="metric-card" :class="[metric.tone, { 'is-selected': status && status === metric.filter }]" :aria-pressed="String(status === metric.filter)" @click="showQueue(metric.filter)">
        <div class="metric-top"><span>{{ metric.label }}</span><span class="metric-share">{{ metric.share }}</span></div>
        <div class="metric-main"><div class="metric-value number">{{ metric.value }}<span>例</span></div><span class="metric-symbol"><i :class="metric.icon" aria-hidden="true" /></span></div>
        <div class="metric-hint">{{ metric.hint }}<i class="el-icon-right" aria-hidden="true" /></div>
      </button>
    </section>

    <div class="overview-grid section-gap">
      <section class="panel chart-panel">
        <div class="panel-heading"><div><h2>病例入队记录</h2><p>按采集日期累计，了解资料准备情况。</p></div><span class="status-pill">示例记录</span></div>
        <div class="chart-legend"><span><i class="legend-dot primary-dot" />入队病例</span><span><i class="legend-dot blue-dot" />已提供彩照</span></div>
        <div class="trend-chart-body"><case-intake-chart :records="intakeRecords" /></div>
        <p class="chart-caption">已提供眼底彩照 {{ imageCount }} 例，缺失资料仍需补全。</p>
      </section>
      <section class="panel chart-panel distribution-panel">
        <div class="panel-heading"><div><h2>流程分布</h2><p>当前病例所在的工作环节</p></div></div>
        <screening-chart :entries="distribution" />
        <div class="distribution-legend"><div v-for="entry in distribution" :key="entry.name"><span><i class="legend-dot" :style="{ background: entry.color }" />{{ entry.name }}</span><strong class="number">{{ entry.value }}<small> 例</small></strong></div></div>
      </section>
    </div>

    <div class="two-column section-gap">
      <section id="screening-queue" ref="queuePanel" class="panel queue-panel">
        <div class="panel-heading"><div><h2>筛查病例队列</h2><p>查找病例，进入对应的筛查与复核环节。</p></div><span class="status-pill">示例数据</span></div>
        <div class="queue-filters">
          <label for="queue-status" class="sr-only">筛选病例状态</label>
          <el-input v-model="search" label="搜索病例" placeholder="搜索姓名或病例编号" prefix-icon="el-icon-search" clearable aria-label="搜索病例" />
          <el-select id="queue-status" v-model="status" aria-label="筛选病例状态">
            <el-option label="全部状态" value="" />
            <el-option v-for="item in statuses" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </div>
        <div class="table-scroll">
          <table class="clinical-table">
            <thead><tr><th scope="col">患者 / 病例编号</th><th scope="col">影像资料</th><th scope="col">流程状态</th><th scope="col">操作</th></tr></thead>
            <tbody>
              <tr v-for="patient in filteredPatients" :key="patient.id">
                <td class="name-cell"><div class="queue-patient"><span class="queue-monogram" aria-hidden="true">{{ patient.name.slice(0, 1) }}</span><div>{{ patient.name }} <span class="muted small-text">{{ patient.sex }} · {{ patient.age }} 岁</span><small>{{ patient.id }}</small></div></div></td>
                <td><div class="image-tags"><span :class="{ available: patient.cfp }">CFP</span><span :class="{ available: patient.oct }">OCT</span></div></td>
                <td><span class="status-pill" :class="patient.tone">{{ patient.status }}</span></td>
                <td><el-button type="text" @click="openCase(patient)">{{ patient.cfp ? '查看病例' : '补全采集' }} <i class="el-icon-arrow-right" /></el-button></td>
              </tr>
              <tr v-if="!filteredPatients.length"><td colspan="4" class="empty-queue">没有符合条件的病例，请调整搜索或筛选。</td></tr>
            </tbody>
          </table>
        </div>
        <div class="queue-footer">共 {{ filteredPatients.length }} 例<span>CFP：眼底彩照 · 灰色表示资料缺失</span></div>
      </section>
      <section class="panel tasks-panel">
        <div class="panel-heading"><div><h2>下一步工作</h2><p>衔接采集、复核与随访</p></div><i class="el-icon-finished muted" aria-hidden="true" /></div>
        <div class="next-task-list">
          <button type="button" @click="openPriority"><span class="task-symbol danger"><i class="el-icon-view" /></span><span><strong>优先复核影像证据</strong><small>{{ priorityCount }} 例需优先关注 · 演示</small></span><i class="el-icon-arrow-right" /></button>
          <button type="button" @click="$router.push('/screening/intake')"><span class="task-symbol info"><i class="el-icon-upload2" /></span><span><strong>补全多模态资料</strong><small>左右眼独立采集与核对</small></span><i class="el-icon-arrow-right" /></button>
          <button type="button" @click="$router.push('/followup/index')"><span class="task-symbol primary"><i class="el-icon-date" /></span><span><strong>查看处置与随访任务</strong><small>由医生确认后进入执行</small></span><i class="el-icon-arrow-right" /></button>
        </div>
        <div class="workspace-note"><i class="el-icon-connection" aria-hidden="true" /><span>多智能体共识辅助评估<br>最终结论由医生复核确认</span></div>
      </section>
    </div>
    <p class="dashboard-footer">多模态采集<span>·</span>共识评估<span>·</span>医生复核<span>·</span>处置随访</p>
  </main>
</template>
<script>
import { mapGetters } from 'vuex'
import ClinicalHeader from '@/components/ClinicalHeader'
import DemoNotice from '@/components/DemoNotice'
import ScreeningChart from '@/components/ScreeningChart'
import CaseIntakeChart from '@/components/CaseIntakeChart'
import { patients, selectPatient } from '@/data/retina-demo'
export default {
  name: 'Dashboard',
  components: { ClinicalHeader, DemoNotice, ScreeningChart, CaseIntakeChart },
  data() {
    return {
      patients, search: '', status: '',
      doctorImage: process.env.BASE_URL + 'images/clinic-doctor.png',
      today: new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }),
      statuses: [{ label: '待采集', value: '待采集' }, { label: '待复核（含优先）', value: 'review' }, { label: '优先复核', value: '优先复核' }, { label: '随访准备', value: '随访准备' }]
    }
  },
  computed: {
    ...mapGetters(['name']),
    imageCount() { return this.patients.filter(item => item.cfp).length },
    priorityCount() { return this.patients.filter(item => item.tone === 'danger').length },
    filteredPatients() {
      const query = this.search.trim().toLowerCase()
      return this.patients.filter(item => (!this.status || (this.status === 'review' ? item.status.includes('复核') : item.status === this.status)) && (!query || (item.name + item.id).toLowerCase().includes(query)))
    },
    metrics() {
      const count = this.patients.length
      const share = value => count ? Math.round(value / count * 100) + '%' : '0%'
      const review = this.patients.filter(item => item.status.includes('复核')).length
      const collection = this.patients.filter(item => !item.cfp).length
      const followup = this.patients.filter(item => item.status === '随访准备').length
      return [
        { label: '病例总数', value: count, share: '演示', hint: '查看当前全部病例', icon: 'el-icon-folder-opened', tone: 'teal', filter: '' },
        { label: '待医生复核', value: review, share: share(review), hint: '含优先复核 ' + this.priorityCount + ' 例', icon: 'el-icon-view', tone: 'rose', filter: 'review' },
        { label: '待补全采集', value: collection, share: share(collection), hint: '补全所需影像资料', icon: 'el-icon-upload2', tone: 'amber', filter: '待采集' },
        { label: '随访准备', value: followup, share: share(followup), hint: '待医生确认安排', icon: 'el-icon-date', tone: 'blue', filter: '随访准备' }
      ]
    },
    distribution() {
      return [
        { name: '待采集', value: this.metrics[2].value, color: '#D4A840' },
        { name: '待复核', value: this.metrics[1].value, color: '#568CAE' },
        { name: '随访准备', value: this.metrics[3].value, color: '#2D8075' }
      ]
    },
    intakeRecords() {
      const dates = [...new Set(this.patients.map(item => item.date))].sort()
      return dates.map(date => {
        const cohort = this.patients.filter(item => item.date <= date)
        return { label: Number(date.slice(5, 7)) + '月' + Number(date.slice(8, 10)) + '日', total: cohort.length, images: cohort.filter(item => item.cfp).length }
      })
    }
  },
  methods: {
    showQueue(status) {
      this.status = status
      this.search = ''
      this.$nextTick(() => this.$refs.queuePanel.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' }))
    },
    openCase(patient) {
      selectPatient(patient)
      this.$router.push(patient.cfp ? '/patients/index' : '/screening/intake')
    },
    openPriority() {
      selectPatient(patients.find(item => item.tone === 'danger'))
      this.$router.push('/screening/consensus')
    }
  }
}
</script>
<style scoped>
.dashboard-date { color: var(--muted); font-size: 13px; white-space: nowrap; }
.dashboard-date i { margin-right: 7px; }
.welcome-panel { position: relative; isolation: isolate; background: var(--primary); border-radius: 20px; padding: 34px 38px; min-height: 248px; margin-top: 24px; }
.welcome-grid { position: absolute; inset: 0; border-radius: inherit; overflow: hidden; z-index: -1; background-image: linear-gradient(rgba(254,254,254,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(254,254,254,.035) 1px, transparent 1px); background-size: 28px 28px; mask-image: linear-gradient(90deg, transparent, #263238); }
.welcome-copy { position: relative; width: calc(100% - 280px); z-index: 2; }
.welcome-copy h2 { color: #FEFEFE; font-size: 30px; font-weight: 600; margin: 0 0 10px; }
.welcome-copy p { color: #FEFEFE; font-size: 16px; margin: 0 0 5px; }
.welcome-modalities { display: block; font-size: 13px; color: #FEFEFE; }
.welcome-button { margin-top: 24px; color: var(--primary-hover); border: 1px solid #FEFEFE; background: #FEFEFE; padding: 12px 20px; border-radius: 8px; font-weight: 500; }
.welcome-button:hover, .welcome-button:focus { color: var(--primary-hover); background: #E9F4F1; border-color: #E9F4F1; }
.welcome-doctor { position: absolute; height: 292px; width: 280px; object-fit: cover; object-position: center top; right: 32px; bottom: 0; z-index: 1; pointer-events: none; }
.welcome-orbit { position: absolute; right: 35px; bottom: 0; width: 264px; height: 238px; border-radius: 130px 130px 0 0; background: rgba(254,254,254,.045); z-index: -1; }
.dashboard-demo-note { background: transparent; border: 0; padding: 0 2px; margin: 15px 0 18px; font-size: 12px; }
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
.metric-card { --metric-color: var(--primary); --metric-soft: var(--primary-soft); display: block; text-align: left; background: var(--panel); border: 1px solid var(--border); border-bottom: 3px solid var(--metric-color); border-radius: 12px; padding: 18px 20px 16px; cursor: pointer; min-width: 0; color: var(--text); transition: box-shadow .18s, border-color .18s; }
.metric-card.rose { --metric-color: var(--rose); --metric-soft: var(--rose-soft); }
.metric-card.amber { --metric-color: var(--amber); --metric-soft: var(--amber-soft); }
.metric-card.blue { --metric-color: var(--blue); --metric-soft: var(--blue-soft); }
.metric-card:hover, .metric-card.is-selected { border-color: var(--metric-color); box-shadow: 0 4px 16px rgba(38,50,56,.05); }
.metric-top { display: flex; justify-content: space-between; align-items: center; gap: 5px; font-size: 14px; color: var(--heading); }
.metric-share { background: var(--metric-soft); color: var(--text); font-size: 10px; padding: 2px 6px; border-radius: 12px; white-space: nowrap; }
.metric-main { display: flex; align-items: center; justify-content: space-between; margin: 14px 0 10px; }
.metric-value { font-size: 32px; font-weight: 650; color: var(--metric-color); line-height: 1.2; }
.metric-value span { font-size: 12px; margin-left: 7px; font-weight: 400; color: var(--muted); }
.metric-symbol { width: 38px; height: 38px; border-radius: 8px; display: grid; place-items: center; background: var(--metric-soft); color: var(--metric-color); font-size: 20px; }
.metric-hint { font-size: 11px; color: var(--muted); display: flex; align-items: center; justify-content: space-between; gap: 4px; }
.overview-grid { display: grid; grid-template-columns: minmax(0, 1.8fr) minmax(280px, 1fr); gap: 20px; }
.chart-panel .panel-heading { border-bottom: 0; padding: 20px 24px 8px; }
.chart-panel .panel-heading p { font-size: 12px; }
.chart-legend { display: flex; gap: 22px; font-size: 12px; color: var(--muted); padding: 8px 24px 0; }
.chart-legend span, .distribution-legend span { display: flex; align-items: center; gap: 7px; }
.legend-dot { width: 8px; height: 8px; border-radius: 3px; display: inline-block; flex-shrink: 0; }
.primary-dot { background: var(--primary); }
.blue-dot { background: var(--blue); }
.trend-chart-body { padding: 0 20px; }
.chart-caption { padding: 0 24px 18px; margin: 0; color: var(--muted); font-size: 12px; }
.distribution-legend { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); padding: 12px 20px 20px; gap: 8px; font-size: 11px; color: var(--muted); }
.distribution-legend > div { display: flex; flex-direction: column; gap: 7px; align-items: center; }
.distribution-legend strong { font-size: 18px; color: var(--heading); font-weight: 600; }
.distribution-legend small { font-size: 11px; color: var(--muted); font-weight: 400; }
.queue-filters { padding: 16px 20px; display: flex; gap: 12px; }
.queue-filters .el-input { width: 100%; max-width: 280px; }
.queue-filters .el-select { width: 180px; flex-shrink: 0; }
.queue-patient { display: flex; align-items: center; gap: 10px; }
.queue-monogram { width: 32px; height: 32px; border-radius: 50%; color: var(--primary); background: var(--primary-soft); display: grid; place-items: center; font-size: 12px; flex-shrink: 0; font-weight: 500; }
.image-tags { display: flex; gap: 5px; }
.image-tags span { color: var(--muted); background: #EDF1F0; font-size: 11px; padding: 2px 6px; border-radius: 4px; }
.image-tags .available { color: var(--primary-hover); background: var(--primary-soft); }
.queue-panel .clinical-table th, .queue-panel .clinical-table td { padding: 13px 20px; }
.queue-footer { display: flex; justify-content: space-between; gap: 12px; border-top: 1px solid var(--border); padding: 13px 20px; font-size: 12px; color: var(--muted); }
.empty-queue { text-align: center; color: var(--muted); white-space: normal !important; }
.next-task-list { padding: 4px 20px; }
.next-task-list button { width: 100%; border: 0; border-bottom: 1px solid var(--border); background: transparent; text-align: left; padding: 19px 0; display: flex; align-items: center; gap: 12px; cursor: pointer; color: var(--text); }
.next-task-list button:last-child { border-bottom: 0; }
.next-task-list button:hover strong { color: var(--primary); }
.next-task-list strong { font-weight: 500; font-size: 14px; display: block; }
.next-task-list small { font-size: 12px; color: var(--muted); display: block; margin-top: 3px; }
.next-task-list button > .el-icon-arrow-right { margin-left: auto; color: var(--muted); }
.task-symbol { width: 36px; height: 36px; border-radius: 10px; display: grid; place-items: center; flex-shrink: 0; font-size: 18px; }
.task-symbol.danger { background: var(--danger-soft); color: var(--danger); }
.task-symbol.info { background: var(--blue-soft); color: var(--blue); }
.task-symbol.primary { background: var(--primary-soft); color: var(--primary); }
.workspace-note { margin: 4px 20px 20px; padding: 15px; border-radius: 10px; display: flex; gap: 12px; align-items: center; background: var(--primary-soft); color: var(--primary-hover); font-size: 12px; line-height: 1.8; }
.workspace-note i { font-size: 23px; }
.dashboard-footer { text-align: center; font-size: 12px; margin: 25px 0 0; color: var(--muted); }
.dashboard-footer span { margin: 0 13px; color: var(--input-border); }
@media (max-width: 1250px) { .metric-card { padding: 17px 15px; } .metric-top { font-size: 13px; } .metric-grid { gap: 14px; } .dashboard-page .two-column { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 1050px) { .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .overview-grid { grid-template-columns: minmax(0, 1fr); } .welcome-copy h2 { font-size: 26px; } .welcome-panel { padding: 30px; } .welcome-doctor { right: 12px; width: 245px; } .welcome-copy { width: calc(100% - 230px); } }
@media (max-width: 767px) {
  .welcome-panel { padding: 24px 20px; min-height: 218px; border-radius: 16px; margin-top: 18px; }
  .welcome-copy { width: calc(100% - 88px); }
  .welcome-copy h2 { font-size: 20px; margin-bottom: 10px; }
  .welcome-copy p { font-size: 13px; max-width: 160px; margin-bottom: 9px; }
  .welcome-modalities { font-size: 11px; line-height: 1.8; max-width: 150px; }
  .welcome-button { padding: 11px 16px; font-size: 12px; margin-top: 17px; }
  .welcome-doctor { width: 124px; height: 192px; right: 0; }
  .welcome-orbit { width: 134px; height: 176px; right: 0; }
  .dashboard-demo-note { font-size: 11px; margin: 13px 0 16px; }
  .metric-grid { gap: 12px; }
  .metric-card { padding: 15px 14px 13px; }
  .metric-top { font-size: 12px; flex-wrap: wrap; gap: 5px; }
  .metric-share { font-size: 9px; }
  .metric-value { font-size: 29px; }
  .metric-symbol { width: 32px; height: 32px; font-size: 18px; }
  .metric-hint { font-size: 10px; }
  .chart-panel .panel-heading { padding: 18px 18px 8px; }
  .chart-legend { padding-left: 18px; padding-right: 18px; gap: 18px; }
  .trend-chart-body { padding: 0 12px; }
  .chart-caption { padding-left: 18px; padding-right: 18px; font-size: 11px; }
  .queue-filters { padding: 14px 16px; flex-direction: column; }
  .queue-filters .el-input, .queue-filters .el-select { width: 100%; max-width: none; }
  .queue-footer { flex-direction: column; gap: 4px; }
  .dashboard-footer { line-height: 2; }
}
</style>
