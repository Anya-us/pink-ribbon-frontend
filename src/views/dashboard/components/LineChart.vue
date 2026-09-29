<template>
  <div :class="className" :style="{height:height,width:width}" />
</template>

<script>
import echarts from 'echarts'
require('echarts/theme/macarons')
import resize from './mixins/resize'

export default {
  mixins: [resize],
  props: {
    className: { type: String, default: 'chart' },
    width: { type: String, default: '100%' },
    height: { type: String, default: '350px' },
    autoResize: { type: Boolean, default: true },
    chartData: { type: Object, required: true }
  },
  data() {
    return { chart: null }
  },
  watch: {
    chartData: {
      deep: true,
      handler(val) {
        this.setOptions(val)
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
    setOptions({ globalData, nationalData } = {}) {
      this.chart.setOption({
        grid: {
          left: 40,
          right: 30,
          bottom: 20,
          top: 30,
          containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' },
          padding: [5, 10]
        },
        xAxis: {
          data: ['2020', '2021', '2022', '2023', '2024'],
          boundaryGap: false,
          axisTick: { show: false },
          axisLine: { lineStyle: { color: '#D9DDE3' } },
          axisLabel: { color: '#7B7B7B' }
        },
        yAxis: {
          axisTick: { show: false },
          axisLine: { lineStyle: { color: '#D9DDE3' } },
          axisLabel: { color: '#7B7B7B' },
          splitLine: { lineStyle: { color: '#ECEEF1' } }
        },
        legend: {
          data: ['全球', '全国'],
          textStyle: { color: '#5E5E5E' }
        },
        series: [
          {
            name: '全球',
            type: 'line',
            smooth: true,
            data: globalData,
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: {
              normal: {
                color: '#BBDDC2', // 绿
                lineStyle: {
                  color: '#BBDDC2',
                  width: 3
                },
                areaStyle: {
                  color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(187, 221, 194, 0.4)' }, // 顶部浓一点
                    { offset: 1, color: 'rgba(187, 221, 194, 0.05)' } // 底部几乎透明
                  ])
                }
              }
            },
            animationDuration: 2800,
            animationEasing: 'cubicInOut'
          },
          {
            name: '全国',
            type: 'line',
            smooth: true,
            data: nationalData,
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: {
              normal: {
                color: '#F5ADB8', // 粉
                lineStyle: {
                  color: '#F5ADB8',
                  width: 3
                },
                areaStyle: {
                  color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(245, 173, 184, 0.4)' }, 
                    { offset: 1, color: 'rgba(245, 173, 184, 0.05)' } 
                  ])
                }
              }
            },
            animationDuration: 2800,
            animationEasing: 'quadraticOut'
          }
        ]
      })
    }
  }
}
</script>

