<template><div ref="chart" class="case-intake-chart" role="img" :aria-label="summary" /></template>
<script>
import echarts from 'echarts/lib/echarts'
import 'echarts/lib/chart/line'
import 'echarts/lib/component/tooltip'
import 'echarts/lib/component/grid'
export default {
  name: 'CaseIntakeChart',
  props: { records: { type: Array, required: true }},
  data() { return { chart: null, observer: null } },
  computed: { summary() { return '示例病例累计入队记录：' + this.records.map(item => item.label + '入队' + item.total + '例，已提供彩照' + item.images + '例').join('；') } },
  watch: { records: { deep: true, handler() { this.renderChart() } }},
  mounted() {
    this.chart = echarts.init(this.$refs.chart)
    this.renderChart()
    if (window.ResizeObserver) {
      this.observer = new ResizeObserver(this.resize)
      this.observer.observe(this.$refs.chart)
    }
    window.addEventListener('resize', this.resize)
  },
  activated() { this.$nextTick(this.resize) },
  beforeDestroy() {
    if (this.observer) this.observer.disconnect()
    window.removeEventListener('resize', this.resize)
    if (this.chart) this.chart.dispose()
  },
  methods: {
    resize() { if (this.chart) this.chart.resize() },
    renderChart() {
      if (!this.chart) return
      const fontFamily = window.getComputedStyle(document.body).fontFamily
      this.chart.setOption({
        textStyle: { fontFamily },
        animation: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
        animationDuration: 220,
        grid: { left: 30, right: 24, top: 22, bottom: 32 },
        tooltip: { trigger: 'axis', backgroundColor: '#FEFEFE', borderColor: '#E6EBEE', borderWidth: 1, textStyle: { color: '#263238', fontFamily }, axisPointer: { type: 'line', lineStyle: { color: '#A9C5B8', type: 'dashed' }}},
        xAxis: { type: 'category', boundaryGap: false, data: this.records.map(item => item.label), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#68767F', fontSize: 11, margin: 14 }},
        yAxis: { type: 'value', min: 0, minInterval: 1, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#68767F', fontSize: 11 }, splitLine: { lineStyle: { color: '#EDF0F2' }}},
        series: [
          { name: '入队病例', type: 'line', symbol: 'circle', symbolSize: 9, lineStyle: { color: '#2D8075', width: 3 }, itemStyle: { color: '#2D8075', borderColor: '#FEFEFE', borderWidth: 3 }, data: this.records.map(item => item.total) },
          { name: '已提供彩照', type: 'line', symbol: 'circle', symbolSize: 7, lineStyle: { color: '#427EAC', width: 2, type: 'dashed' }, itemStyle: { color: '#427EAC', borderColor: '#FEFEFE', borderWidth: 2 }, data: this.records.map(item => item.images) }
        ]
      }, true)
    }
  }
}
</script>
<style scoped>
.case-intake-chart { height: 198px; width: 100%; }
</style>
