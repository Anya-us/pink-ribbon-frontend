<template>
  <div class="score-gauge">
    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'ScoreGauge',
  props: {
    value: { type: Number, default: 72 }
  },
  data() {
    return { chart: null }
  },
  mounted() {
    // 延迟确保容器渲染完成
    this.$nextTick(() => {
      setTimeout(this.initChart, 100)
    })
    window.addEventListener('resize', this.resizeChart)
  },
  beforeDestroy() {
    if (this.chart) this.chart.dispose()
    window.removeEventListener('resize', this.resizeChart)
  },
  methods: {
    initChart() {
      if (!this.$refs.chartRef) return
      this.chart = echarts.init(this.$refs.chartRef)

      const option = {
        series: [
          {
            type: 'gauge',
            startAngle: 180,
            endAngle: 0,
            min: 0,
            max: 100,
            radius: '95%',

            // 底灰环
            axisLine: {
              lineStyle: {
                width: 20,
                color: [[1, '#E8EBF0']]
              }
            },

            // 前景彩色渐变环
            progress: {
              show: true,
              width: 20,
              roundCap: true,
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                  { offset: 0, color: '#F76C6C' },   // 红
                  { offset: 0.5, color: '#FFD166' }, // 黄
                  { offset: 1, color: '#4FC3B8' }    // 青绿
                ])
              }
            },

            pointer: { show: false },
            axisTick: { show: false },
            splitLine: { show: false },
            axisLabel: { show: false },

            detail: {
              valueAnimation: true,
              formatter: '{value}',
              fontSize: 54,
              fontWeight: 'bold',
              color: '#2C3E50',
              offsetCenter: [0, '-5%']
            },

            data: [{ value: this.value }]
          }
        ]
      }

      this.chart.setOption(option)
    },
    resizeChart() {
      if (this.chart) this.chart.resize()
    }
  }
}
</script>

<style scoped>
.score-gauge {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chart {
  width: 100%;
  height: 320px;
  background: #f9fafc; /* 让颜色更显眼 */
  border-radius: 20px;
}
</style>
