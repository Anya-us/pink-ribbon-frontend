<template>
  <div :class="className" :style="{ height: height, width: width }" />
</template>

<script>
import * as echarts from 'echarts'
require('echarts/theme/macarons') // echarts 主题
import resize from './mixins/resize'

export default {
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
      default: '200px'
    }
  },
  data() {
    return {
      chart: null
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart()
    })
  },
  beforeDestroy() {
    if (!this.chart) {
      return
    }
    this.chart.dispose()
    this.chart = null
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$el, 'macarons')

      this.chart.setOption({
        tooltip: {
          trigger: 'item',
          formatter: ' {a} <br/>{b} :{d}%',
          textStyle: {
            fontSize: 10
          },
          padding: 8
        },
        legend: {
          left: 'center',
          bottom: '5',
          data: ['满意', '一般', '不满意'],
          textStyle: {
            fontSize: 11
          },
          itemWidth: 9,
          itemHeight: 9,
          itemGap: 12
        },
        series: [
          {
            name: '用户满意度',
            type: 'pie',
            roseType: 'radius',
            // 调整内外半径比例，增加扇形高度差异
            radius: [15, 70], 
            // 调整中心位置，为更高的扇形留出空间
            center: ['50%', '50%'],
            // 调整数据比例，增加"一般"和"不满意"的占比
            data: [
              { value: 300, name: '满意' },  // 降低满意的比例
              { value: 150, name: '一般' },  // 提高一般的比例
              { value: 100, name: '不满意' } // 提高不满意的比例
            ],
            // 调整扇区角度，使各部分分布更均匀
            minAngle: 20,  // 设置最小角度，确保小数据也有可见的扇形
            label: {
              show: true,
              fontSize: 10,
              formatter: '{b}:{d}%',
              padding: 2
            },
            labelLine: {
              show: true,
              length: 8,  // 稍微增加标签线长度，适应更高的扇形
              lineStyle: {
                width: 0.8
              }
            },
            animationEasing: 'cubicInOut',
            animationDuration: 2200
          }
        ]
      })
    }
  }
}
</script>

<style scoped>
.chart {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden; 
}
</style>
