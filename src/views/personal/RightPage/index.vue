<template>
  <div class="right-page">
    <!-- 顶部头像区 -->
    <div class="header">
      <div class="avatar">
        <img :src="defaultAvatar" class="avatar" />
      </div>
      <span class="username">***</span>
    </div>
    <!-- 历史就诊记录 -->
    <div class="title">
      <h3>历史检查报告</h3>
    </div>
    <div class="card">
      <div class="filters1">
        <el-select v-model="filters.item" placeholder="筛选项目" clearable
          size="small" style="width: 200px">
          <el-option v-for="opt in uniqueItems" :key="opt" :label="opt" :value="opt" />
        </el-select>
        <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至"
          start-placeholder="开始日期" end-placeholder="结束日期" clearable
          size="small" style="width: 260px" value-format="yyyy-MM-dd" />
        <el-button type="primary" size="small" @click="applyHistoryFilter">筛选</el-button>
        <el-button size="small" @click="resetHistoryFilter">重置</el-button>
      </div>
      
      <el-table :data="filteredHistoryData" border style ="width:100%; margin-top:12px;">
        <el-table-column prop="item" label="项目" width="250" />
        <el-table-column prop="department" label="科室" width="" />
        <el-table-column prop="doctor" label="医生" width="120" />
        <el-table-column prop="result" label="结果" width="" />
        <el-table-column prop="date" label="日期" width="150" />
      </el-table>
    </div>
    <!-- 检查结果趋势 -->
    <div class="title">
      <h3>检查结果趋势</h3>
    </div>
    <div class="card">
      <div class="filters2">
        <el-select v-model="filters.category" placeholder="检查类别" size="small">
          <el-option label="影像学检查" value="1" />
          <el-option label="血液检查" value="2" />
          <el-option label="临床检验" value="3" />
        </el-select>

        <el-select v-model="filters.item" placeholder="检查项目" size="small">
          <el-option label="BRCA1/2基因检测" value="1" />
          <el-option label="IHC检测" value="2" />
          <el-option label="21基因检测" value="3" />
          <el-option label="核磁共振" value="4" />
        </el-select>

        <el-select v-model="filters.range" placeholder="时间范围" size="small">
          <el-option label="近一月" value="1"/>
          <el-option label="近半年" value="2" />
          <el-option label="近一年" value="3" />
          <el-option label="近三年" value="4" />
        </el-select>

        <el-button type="primary" size="small" @click="applyFilters">选择</el-button>
        
      </div>
      
      <transition name="fade" mode="out-in">
        <line-chart v-if="showChart" :chart-data="lineChartData" :key="chartKey" style="width:100%; height:80%;" />
      </transition>
    </div>
  </div>
</template>

<script>
import LineChart from './components/LineChart'

const lineChartData = {
  annualRate: {
    nationalData: [89, 82, 91]
  }
}
export default {
  name: 'RightPage',
  components: { LineChart },
  data() {
    return {
      defaultAvatar: require('@/assets/profileavatar.jpg'),
      filters: { 
        category: '', 
        item: '', 
        range: '',
        item: '',
        dateRange: [] 
      },
      showChart: false,
      chartKey: 0,
      lineChartData: lineChartData.annualRate,
      historyData:[
        { item: 'BRCA1/2基因检测', department: '遗传咨询科', doctor: '王医生', result: 'BRCA突变阳性', date: '2023-03-06' },
        { item: '21基因检测', department: '肿瘤科', doctor: '林医生', result: '复发风险低', date: '2025-02-04' },
        { item: 'IHC检测', department: '病理科', doctor: '*医生', result: 'ER阳性', date: '2024-02-04' },
        { item: 'IHC检测', department: '病理科', doctor: '*医生', result: 'PR阳性', date: '2024-11-13' },
        { item: 'IHC检测', department: '病理科', doctor: '*医生', result: 'HER2阴性', date: '2025-06-03' }
      ],
      filteredHistoryData:[]
    }
  },
  computed: {
    uniqueItems() {
      const items = this.historyData.map(h => h.item)
      return [...new Set(items)]
    }
  },
  created() {
    this.filteredHistoryData = this.historyData
  },
  methods: {
    applyHistoryFilter() {
      const [start, end] = this.filters.dateRange || []
      this.filteredHistoryData = this.historyData.filter(record => {
        const matchItem = this.filters.item ? record.item === this.filters.item : true
        const matchDate =
          start && end
            ? new Date(record.date) >= new Date(start) && new Date(record.date) <= new Date(end)
            : true
        return matchItem && matchDate
      })
    },
    resetHistoryFilter() {
      this.filters.item = ''
      this.filters.dateRange = []
      this.filteredHistoryData = this.historyData
    },
    applyFilters() {
      // 点击时不改数据，只刷新 key 触发 transition
      this.showChart = true
      this.chartKey += 1
    }
  }
}
</script>

<style scoped>
.right-page {
  width: 90%;
  padding: 20px;
}
.header {
  display: flex;
  height: 90px;
  align-items: center;
  background: #fff;
  padding: 12px 20px;
  border-radius: 8px;
  margin-top: 0px;
  margin-bottom: 10px;
}
.header:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.title h3 {
  display: flex;
  justify-content: space-around;
}
.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 12px;
}
.username {
  font-size: 18px;
  font-weight: bold;
}
.card {
  height: 350px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}
.card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.box {
  display: flex;
}
.filters1 {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  margin-bottom: 20px;
}
.filters2 {
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: 12px;
  margin-bottom: 20px;
}
.el-table th {
  background-color: #f5f7fa;
  color: #333;
  font-weight: bold;
}
.el-table td {
  color: #555;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>