<template>
  <div class="dashboard-editor-container">
    <HomeCarousel /> <!-- 顶部轮播图 -->

    <!-- 欢迎语与用户信息 -->
    <div class="welcome-section">
      <h2>欢迎回来，{{ user.name }}！</h2>
      <p>上次AI分析时间：{{ lastCheck }}</p>
    </div>

    <div class="top-header">系统相关数据概览</div>
    <el-divider />

    <!-- 风险卡片 + 趋势图 -->
    <el-row class="main-row">
      <el-col :lg="12" :sm="24">
        <div class="header">全球&全国乳腺癌占癌症比例趋势图</div>
        <line-chart :chart-data="lineChartData" style="width:100%;" />
      </el-col>

      <el-col :lg="12" :sm="24" class="stat-cards">
        <div v-for="(card, index) in stats" class="stat-card" :key="index">
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- 群体对比与功能卡 -->
    <el-row class="main-row">
      <el-col :lg="12" :sm="24">
        <div class="header">人群风险分布对比</div>
        <BarChart class="chart-box" />
      </el-col>

      <el-col :lg="12" :sm="24">
        <div v-for="(item,index) in featureList" class="feature-card"  :key="index">
          <div class="card-content">
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 健康知识区 -->
    <div class="top-header">健康知识与使用指南</div>
      <el-divider />
    <div class="homepage-guide">
      <el-row>
        <el-col :span="24">
          <VideoPlayer />
        </el-col>
      </el-row>
    </div>

    <!-- 回到顶部 -->
    <BackToTop />
  </div>
</template>

<script>
import HomeCarousel from './components/HomeCarousel'
import LineChart from './components/LineChart'
import VideoPlayer from './components/VideoPlayer'
import BackToTop from '@/components/BackToTop'
import BarChart from './components/BarChart'
import * as echarts from 'echarts'

// 模拟趋势数据
const lineChartData = {
  annualRate: {
    globalData: [85, 78, 70, 72, 90],
    nationalData: [90, 88, 80, 82, 87]
  }
}

export default {
  name: 'UserDashboard',
  components: { HomeCarousel, LineChart, VideoPlayer, BarChart, BackToTop },
  data() {
    return {
      user: { name: '女女士' },
      lastCheck: '2025-09-21',
      lineChartData: lineChartData.annualRate,
      stats: [
        { label: '访问人数', value: '1,204' },
        { label: '就诊人数', value: '678' },
        { label: '就诊正确率', value: '94.8%' },
        { label: '痊愈率', value: '88.6%' }
      ],
      featureList: [
        { title: '个性化诊疗', desc: 'AI为您定制专属治疗建议' },
        { title: '专家咨询', desc: '与权威医生实时沟通分析结果' },
        { title: '隐私安全', desc: '您的检测数据经过严格加密保护' }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-editor-container {
  padding: 32px;
  background-color: #f8f9fb;
  position: relative;

  .top-header {
    font-weight: 700;
    font-size: 18px;
    color: #2c3e50;
    margin: 32px 0 12px;
  }

  .welcome-section {
    text-align: center;
    margin: 24px 0 16px;
    h2 { font-size: 22px; font-weight: 600; color: #2c3e50; }
    p { font-size: 14px; color: #6b7280; }
    color:#5e5e5e
  }

  .main-row {
    background: #fff;
    gap: 50px;
    padding: 16px;
    margin-bottom: 32px;
    border-radius: 16px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.04);
    .header {
      margin-left: 50px;
      margin-top: 15px;
      margin-bottom: 15px;
    }
  }

  /* —— 右上四个卡片 —— */
  .stat-cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-content: space-between;
    height: 360px; /* 和linechart一致 */
    padding: 8px;

  .stat-card {
    flex: 0 0 48%; /* 每行2个 */
    height: 48%; /* 每列2个 */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    background: linear-gradient(145deg, #f6f7fb, #ebecf0);
    border-radius: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    cursor: pointer;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }

    .stat-value {
      font-size: 30px;
      font-weight: 700;
      margin-bottom: 8px;
    }

    .stat-label {
      font-size: 14px;
      color: #6b7280;
      letter-spacing: 0.3px;
    }
  }
}


  /* —— 功能卡 —— */
  .feature-card {
    background: linear-gradient(145deg, #f6f7fb, #ebecf0);
    border-radius: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    padding: 20px;
    margin-bottom: 16px;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }

    .card-content {
      h3 {
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 6px;
      }
      p {
        font-size: 13px;
        color: #6b7280;
        line-height: 1.5;
      }
    }
  }

  .chart-box {
    width: 100%;
    height: 300px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 30px;
  }

  .homepage-guide {
      background: #ffffff;
      border-radius: 16px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.05);
      padding: 16px;
  }
  
  .stat-card:nth-child(1) .stat-value {
    color: #f4a4b0; 
  }
  .stat-card:nth-child(2) .stat-value {
    color: #fcb998; 
  }
  .stat-card:nth-child(3) .stat-value {
    color: #a0d9bc; 
  }
  .stat-card:nth-child(4) .stat-value {
    color: #abd8dc; 
  }

  .feature-card:nth-child(1) .card-content h3 {
    color: #f4a4b0;
  }
  .feature-card:nth-child(2) .card-content h3 {
    color: #fcb998;
  }
  .feature-card:nth-child(3) .card-content h3 {
    color: #a0d9bc;
  }

}
</style>
