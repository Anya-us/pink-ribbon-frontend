<template>
  <div class="distribution-chart" role="img" :aria-label="'演示病例流程分布：' + summary">
    <div ref="chart" class="screening-chart" />
    <div class="distribution-total"><strong class="number">{{ total }}</strong><span>病例总数</span></div>
  </div>
</template>
<script>
import echarts from 'echarts/lib/echarts'
import 'echarts/lib/chart/pie'
import 'echarts/lib/component/tooltip'
export default {
  name: 'ScreeningChart',
  props: { entries: { type: Array, required: true }},
  data() { return { chart: null, observer: null } },
  computed: {
    total() { return this.entries.reduce((sum, item) => sum + item.value, 0) },
    summary() { return this.entries.map(item => item.name + item.value + '例').join('，') }
  },
  watch: { entries: { deep: true, handler() { this.renderChart() } }},
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
        tooltip: { trigger: 'item', backgroundColor: '#FEFEFE', borderColor: '#E6EBEE', borderWidth: 1, textStyle: { color: '#263238', fontFamily }, formatter: '{b}：{c} 例（{d}%）' },
        series: [{ type: 'pie', radius: ['66%', '88%'], center: ['50%', '50%'], startAngle: 90, avoidLabelOverlap: true, label: { show: false }, labelLine: { show: false }, hoverOffset: 3, data: this.entries.map(item => ({ name: item.name, value: item.value, itemStyle: { color: item.color, borderColor: '#FEFEFE', borderWidth: 4 }})) }]
      }, true)
    }
  }
}
</script>
<style scoped>
.distribution-chart { position: relative; width: 100%; height: 196px; }
.screening-chart { height: 100%; width: 100%; }
.distribution-total { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; pointer-events: none; }
.distribution-total strong { font-size: 34px; line-height: 1.3; font-weight: 650; color: var(--heading); }
.distribution-total span { font-size: 12px; color: var(--muted); margin-top: 4px; }
</style>
