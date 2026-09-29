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
    setOptions({ nationalData } = {}) {
      this.chart.setOption({
        grid: {
          left: 30,
          right: 80,
          bottom: 0,
          top: 30,
          containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' },
          padding: [5, 10]
        },
        xAxis: {
          data: ['第一次', '第二次', '第三次'],
          boundaryGap: false,
          axisTick: { show: false },
          axisLine: { lineStyle: { color: '#D9DDE3' } },
          axisLabel: { color: '#7B7B7B' },
          name: '检测次数',
          nameLocation: 'end',
          nameGap: 15,
          nameTextStyle: {
            color: '#666',
            fontSize: 13,
            padding: [0, 0, 0, 10]
          }
        },
        yAxis: {
          axisTick: { show: false },
          axisLine: { lineStyle: { color: '#D9DDE3' } },
          axisLabel: { color: '#7B7B7B' },
          splitLine: { lineStyle: { color: '#ECEEF1' } },
          name: '阳性率(%)',
          nameLocation: 'middle',
          nameGap: 25,
          nameTextStyle: {
            color: '#666',
            fontSize: 13,
            align: 'left',
            padding: [0, 0, 5, 0]
          }
        },
        legend: {
          textStyle: { color: '#5E5E5E' }
        },
        series: [
          {
            type: 'line',
            smooth: true,
            data: nationalData,
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: {
              normal: {
                color: '#ffccd3', // 浅柔紫
                lineStyle: {
                  color: '#ffccd3',
                  width: 3
                },
                areaStyle: {
                  color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(255, 204, 211, 0.5)' },  // 顶部颜色：粉+半透明
                    { offset: 1, color: 'rgba(255, 204, 211, 0.05)' }  // 底部颜色：淡粉、几乎透明
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

