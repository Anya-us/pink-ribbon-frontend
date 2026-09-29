<template>
  <div class="dashboard-editor-container">
    <HomeCarousel /> <!-- 轮播图组件 -->

    <div class="top-header">数据与趋势分析</div>
    <el-divider />
    <div class="dashboard-data-analysis">
      <!-- 第1行：女性乳腺癌占全球新增癌症病例百分比（独占一行） -->
      <div class="analysis-section">
        <!-- 标题与分隔线 -->
        <div class="section-header">
          <div class="header">女性乳腺癌占全球新增癌症病例百分比</div>
          <el-divider class="section-divider" />
        </div>
        <!-- 折线图内容（独占一行宽度） -->
        <div class="section-content">
          <line-chart :chart-data="lineChartData" style="width: 100%;" />
        </div>
      

      <!-- 第2行：系统数据分析（独占一行，在乳腺癌模块下方） -->
      
        <!-- 标题与分隔线 -->
        <div class="section-header">
          <div class="header">系统数据分析</div>
          <el-divider class="section-divider" />
        </div>
        <!-- 系统数据内容（内部保持原卡片布局） -->
        <div class="section-content system-data-content">
          <!-- 系统使用人数（独占一行） -->
          <div class="system-card-row" style="margin-bottom: 16px;">
            <div class="feature-card feature-card-small">
              <div class="card-content">
                <h3>系统使用人数</h3>
                <p>当前系统活跃用户规模</p>
                <el-progress 
                  :percentage="75" 
                  status="success" 
                  stroke-width="6" 
                  show-text 
                  style="margin-top: 8px;"
                />
                <p style="font-size: 12px; color: #666; margin-top: 4px;">当前：13,568 人 | 目标：18,000 人</p>
              </div>
            </div>
          </div>

          <!-- 预测准确率 + 用户满意度（同行分布，保持对齐） -->
          <div class="system-card-row" :gutter="16">
            <!-- 预测准确率 -->
            <div class="system-card-col">
              <div class="feature-card feature-card-equal">
                <div class="card-content card-content-center">
                  <div class="card-header">
                    <h3>预测准确率</h3>
                    <p>AI乳腺癌预测模型精度</p>
                  </div>
                  <div class="card-body">
                    <el-progress 
                      type="circle" 
                      :percentage="92" 
                      :width="125" 
                      stroke-width="8"
                    />
                  </div>
                  <div class="card-footer">
                    <p class="data-card__desc">精度：92%</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 用户满意度 -->
            <div class="system-card-col">
              <div class="feature-card feature-card-equal">
                <div class="card-content">
                  <div class="card-header">
                    <h3>用户满意度</h3>
                    <p>基于320条用户反馈统计</p>
                  </div>
                  <div class="card-body">
                    <div class="chart-wrapper">
                      <pie-chart />
                    </div>
                  </div>
                  <div class="card-footer">
                    <p class="data-card__desc">&nbsp;</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="homepage-guide" style="margin-top: 32px;">
      <div class="top-header">使用指南</div>
      <el-divider />
      <div style="background: #fff; padding: 16px 16px 24px; margin-bottom: 32px;">
        <VideoPlayer />
      </div>  
    </div>
  </div>
</template>

<script>
import HomeCarousel from './components/HomeCarousel'
import Progress from './components/Progress'
import LineChart from './components/LineChart'
import VideoPlayer from './components/VideoPlayer'
import PieChart from './components/PieChart'

// 发病率数据（补充年份标签，折线图更清晰）
const lineChartData = {
  annualRate: {
    globalData: [100, 120,143, 161,160],
    nationalData: [120, 70,82, 91,95],
    labels: ['2020', '2022', '2024']
  }
}

export default {
  name: 'DashboardAdmin',
  components: {
    HomeCarousel,
    Progress,
    VideoPlayer,
    LineChart,
    PieChart,
  },
  data() {
    return {
      lineChartData: lineChartData.annualRate
    }
  },
  methods: {
    handleSetLineChartData(type) {
      this.lineChartData = lineChartData[type]
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-editor-container {
  padding: 32px;
  background-color: rgb(240, 242, 245);
  position: relative;

  .top-header {
    font-size: 18px;
    font-weight: 600;
    color: #1f2329;
    margin-bottom: 12px;
  }

  // 每个分析模块（乳腺癌/系统数据）的统一容器样式
  .analysis-section {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    padding: 20px;
  }

  // 模块标题区样式
  .section-header {
    margin-bottom: 16px;
  }

  .header {
    font-size: 16px;
    color: rgba(0, 0, 0, 0.7);
    margin-bottom: 8px;
  }

  .section-divider {
    margin: 0;
    width: 100%;
  }

  // 模块内容区基础样式
  .section-content {
    padding: 35px 0;
  }

  // 系统数据分析模块的内容区特殊样式（内部卡片布局）
  .system-data-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  // 系统数据的卡片行容器（替代原el-row）
  .system-card-row {
    display: flex;
    width: 100%;
    gap: 16px; // 卡片之间的间距
  }

  // 系统数据的卡片列容器（预测准确率/用户满意度各占一半）
  .system-card-col {
    flex: 1; // 两列均分宽度
  }

  // 系统使用人数模块（缩小，独占一行）
  .feature-card-small {
    min-height: 140px;
    display: flex;
    align-items: center;
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    padding: 16px;
    transition: all 0.3s ease;
    cursor: pointer;
    width: 100%;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    .card-content {
      flex: 1;
    }

    h3 {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 6px;
      color: #333;
    }

    p {
      font-size: 13px;
      color: #666;
      margin: 0;
      line-height: 1.4;
    }
  }

  // 预测准确率+用户满意度：统一模块样式（强制对齐）
  .feature-card-equal {
    width: 100%;
    height: 300px; // 固定高度，确保两模块大小一致
    display: flex;
    flex-direction: column;
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    padding: 18px;
    transition: all 0.3s ease;
    cursor: pointer;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    .card-content {
      flex: 1;
      display: flex;
      flex-direction: column;
    }

    // 1. 标题区：固定高度，两模块对齐
    .card-header {
      height: 50px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    // 2. 内容区：自适应填充，高度一致
    .card-body {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 8px 0;
    }

    // 3. 底部描述区：固定高度，底部对齐
    .card-footer {
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    h3 {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 4px;
      color: #333;
      text-align: center;
    }

    p {
      font-size: 13px;
      color: #666;
      margin: 0;
      text-align: center;
    }
  }

  // 预测准确率模块：内容居中
  .card-content-center {
    text-align: center;
  }

  // 饼图容器：确保完整显示且与圆形进度条匹配
  .chart-wrapper {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  // 描述文本样式统一
  .data-card__desc {
    font-size: 16px;
    color: #666;
    margin: 0;
  }

  // 使用指南区域
  .homepage-guide {
    .top-header {
      margin-bottom: 12px;
    }
  }
}

// 响应式适配：小屏幕下系统数据的两卡片上下堆叠
@media (max-width: 1024px) {
  .system-card-row {
    flex-direction: column;
  }

  .feature-card-equal {
    height: 220px;
  }

  .chart-wrapper {
    height: 120px;
  }

  .dashboard-editor-container {
    padding: 16px;
  }
}
</style>