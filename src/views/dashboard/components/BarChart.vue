<template>
  <div :class="className" :style="{ height, width }" />
</template>

<script>
import * as echarts from 'echarts'
import 'echarts/theme/macarons'
import resize from './mixins/resize'

export default {
  name: 'BarChart',
  mixins: [resize],
  props: {
    className: {
      type: String,
      default: 'chart'
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '300px'
    }
  },
  data() {
    return {
      chart: null,
      chartData: {
        categories: ['低风险', '中风险', '高风险'],
        values: [60, 30, 10]
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart()
    })
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.dispose()
      this.chart = null
    }
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$el, 'macarons')
      this.setOptions(this.chartData)
    },
    setOptions({ categories, values }) {
      if (!this.chart) return
      this.chart.setOption({
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        grid: {
          left: 40,
          right: 20,
          bottom: 30,
          top: 40,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: categories,
          axisLine: { lineStyle: { color: '#A0A7B4' } },
          axisLabel: { color: '#555' }
        },
        yAxis: {
          type: 'value',
          name: '比例(%)',
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#ECEEF3' } },
          axisLabel: { color: '#555' },
          nameTextStyle: {
            color: '#555'
          }
        },
        series: [
          {
            data: values,
            type: 'bar',
            barWidth: '40%',
            itemStyle: {
              borderRadius: [6, 6, 0, 0],
              color: (params) => ['#BBDDC2', '#FACBB3', '#F5ADB8'][params.dataIndex]
            },
            animationDuration: 1000
          }
        ]
      })
    }
  }
}
</script>

<style scoped>
.chart {
  width: 100%;
  height: 100%;
}
</style>
