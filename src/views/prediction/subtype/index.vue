<template>
  <div class="subtype-analysis">
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">亚型预测
          <el-tag type="success" size="small" class="page-tag">最新更新</el-tag>
        </h2>
        <p class="page-subtitle">基于患者检测数据进行的亚型分析</p >
      </div>
    </div>

    <!-- 基本信息 -->
    <div class="content-container module-spacing">
      <div class="header">
        <el-card shadow="hover" class="info-card">
          <div class="info-row">
            <span class="label">患者</span>
            <span class="value">女女士</span>
          </div>
          <div class="info-row">
            <span class="label">性别</span>
            <span class="value">女</span>
          </div>
          <div class="info-row">
            <span class="label">年龄</span>
            <span class="value">48</span>
          </div>
          <div class="info-row">
            <span class="label">分析日期</span>
            <span class="value">2025-09-20</span>
          </div>
          <div class="info-row">
            <span class="label">多组学检测完成情况</span>
            <el-tag type="success">已完成</el-tag>
          </div>
        </el-card>

        <!-- 分析结果 -->
        <el-card shadow="hover" class="result-card">
          <h3>亚型分析结果</h3>
          <p>系统分析表明，患者属于 
            <el-tag :type="subtypeTag">{{ subtypeText }}</el-tag>
          </p >
        </el-card>
      </div>
    </div>
    
    <!-- 特征展例 -->
    <div class="content-container module-spacing">
      <div class="features-row">
        <!-- 基因组学卡片 -->
        <el-card shadow="always" class="feature-card" @click.native="showReport('gene')">
          <div class="card-header gene">基因组学特征</div>
          <ul>
            <li><span class="dot gene"></span> 突变基因: TP53, BRCA1</li>
            <li><span class="dot gene"></span> 高表达: HER2</li>
          </ul>
        </el-card>

        <!-- 蛋白质组学卡片 -->
        <el-card shadow="always" class="feature-card" @click.native="showReport('protein')">
          <div class="card-header protein">蛋白质组学特征</div>
          <ul>
            <li><span class="dot protein"></span> 过表达: EGFR</li>
            <li><span class="dot protein"></span> 信号通路异常: PI3K/AKT</li>
          </ul>
        </el-card>

        <!-- 转录组学卡片 -->
        <el-card shadow="always" class="feature-card" @click.native="showReport('transcript')">
          <div class="card-header transcript">转录组学特征</div>
          <ul>
            <li><span class="dot transcript"></span> 高表达: ESR1</li>
            <li><span class="dot transcript"></span> 抑制: GATA3</li>
          </ul>
        </el-card>
      </div>
    </div>

    <!-- 弹窗：显例具体报告 -->
    <el-dialog :title="reportTitle" :visible.sync="reportVisible" width="50%" append-to-body>
      <div v-html="reportContent"></div>
      <span slot="footer">
        <el-button @click="reportVisible = false">关闭</el-button> 
      </span>
    </el-dialog>
    
    <!-- 亚型详细介绍 -->
    <div class="content-container module-spacing">
      <el-card shadow="hover" class="subtype-card">
        <h3>亚型详细介绍</h3>
        <div class="subtype-intro-row">
          <div v-for="item in subtypes" :key="item.name" class="subtype-item" @click="toggleSubtype(item.name)">
            <h3>{{ item.name }}</h3>
            <p>{{ item.brief }}</p >
            <!-- 展开区域 -->
            <transition name="fade">
              <div v-if="activeSubtype === item.name" class="subtype-content">
                <p v-for="line in item.detail" :key="line">{{ line }}</p >
              </div>
            </transition>
          </div>
        </div> 
      </el-card>
    </div>
    
    <!-- 综合结论 -->
    <div class="content-container module-spacing">
      <el-card shadow="hover" class="conclusion-card">
        <h3>综合判断结论</h3>
        <p>
          结合多组学特征，提例患者为 <el-tag :type="subtypeTag">{{ subtypeText }}</el-tag>，该亚型预后较差，
          推荐进一步检测 HER2 靶向治疗相关指标。
        </p >
        <el-button class="plan-button" @click="gotoDetail">{{ isProcessing ? '方案生成中...' : '个性化治疗方案生成' }}</el-button>
      </el-card>
    </div>
  
  </div>
</template>

<script>
export default {
  name: "SubtypeAnalysis",
  data() {
    return {
      activeSubtype: '',
      subtypes: [
        {
          name: 'Luminal A 型',
          brief: 'ER、PR 阳性，HER2 阴性，Ki-67 低',
          detail: [
            '生长慢，复发风险低',
            '预后最好',
            '对内分泌治疗反应良好'
          ]
        },
        {
          name: 'Luminal B 型',
          brief: 'ER、PR 阳性，可伴 HER2 阳性，Ki-67 高',
          detail: [
            '比 Luminal A 生长更快',
            '复发风险更高',
            '部分患者需化疗或 HER2 靶向治疗'
          ]
        },
        {
          name: 'HER2 阳性型',
          brief: 'HER2 过表达，ER、PR 阴性',
          detail: [
            '侵袭性强',
            '对 HER2 靶向药物敏感'
          ]
        },
        {
          name: '三阴性乳腺癌',
          brief: 'ER、PR、HER2 均阴性',
          detail: [
            '进展快，复发风险高',
            '目前主要依赖化疗',
            '部分可尝试免疫治疗'
          ]
        }
      ],
      consistencyText: "已完成",
      subtypeText: "Luminal A",
      reportVisible: false,
      reportTitle: '',
      reportContent: '',
      isProcessing: false
    };
  },
  computed: {
    consistencyTag() {
      return this.consistencyText === "已完成" ? "success" : "warning";
    },
    subtypeTag() {
      switch (this.subtypeText) {
        case 'Luminal A': return 'success'
        case 'Luminal B': return 'primary'
        case '三阴性乳腺癌': return 'danger'
        case 'HER2 阳性': return 'warning'
      }
    }
  },
  methods: {
    gotoDetail() {
      try{
        this.isProcessing = true
        this.$message({
          message:'正在分析数据中...',
          type:'info',
          duration: 3000
        })
        setTimeout(() => {
          this.isProcessing = false
          this.$message({
            message:'诊断完成',
            type:'success',
            duration:3000
          })
          this.$router.push('/advice/index')
        },2500)
      }catch(error){
        this.isProcessing = false
        console.error('执行诊断失败:', error)
        this.$message.error('执行诊断过程中出现错误，请稍后重试')
      }
    },
    showReport(type) {
      this.reportVisible = true;
      if (type === 'gene') {
        this.reportTitle = '基因组学报告';
        this.reportContent = `
          <p>检测到 TP53 和 BRCA1 基因突变，提例 DNA 修复机制受损，可能增加乳腺癌风险。</p >
          <p>HER2 基因高表达，提例可能对 HER2 靶向治疗有反应。</p >
        `;
      } else if (type === 'protein') {
        this.reportTitle = '蛋白质组学报告';
        this.reportContent = `
          <p>EGFR 蛋白过表达，提例细胞增殖信号增强，可能促进肿瘤生长。</p >
          <p>PI3K/AKT 信号通路异常，提例细胞存活和代谢调控受影响，可能与肿瘤进展相关。</p >
        `;
      } else if (type === 'transcript') {
        this.reportTitle = '转录组学报告';
        this.reportContent = `
          <p>ESR1 基因高表达，提例激素受体阳性，可能对内分泌治疗有反应。</p >
          <p>GATA3 基因抑制，提例细胞分化受影响，可能与肿瘤侵袭性相关。</p >
        `;
      }
    },
    toggleSubtype(name) {
      this.activeSubtype = this.activeSubtype === name ? '' : name
    }
  }
}
</script>

<style scoped>
/* 统一字体大小，整体调整为16px */
* {
  font-size: 15px;
  font-family: "Microsoft YaHei", sans-serif;
}

.subtype-analysis {
  height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 40px;
  position: relative;
  overflow-y: auto;
}

/* 统一内容容器样式 - 关键修改点 */
.content-container {
  max-width: 1200px; /* 限制最大宽度 */
  margin: 0 auto; /* 居中显例 */
}

/* 增大模块间距 */
.module-spacing {
  margin-bottom: 40px;
  padding-left: 20px;
  padding-right: 20px;
}

.page-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #fff;
  padding: 20px 40px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 22px;
  color: #1f2d3d;
  margin: 0 0 5px 0;
  font-weight: 600;
  display: flex;
  align-items: center;
  padding: 10px;
}
.page-tag {
  margin-left: 10px;
  font-size: 12px;
  padding: 2px,6px;
}
.page-subtitle {
  font-size: 14px;
  color: #8392a5;
  margin: 0;
}
.header {
  gap: 20px;
  display: flex;
  flex-direction: row;
}
.header-content {
  display: flex;
  flex-direction: column;
}

.subtype-intro-row {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  font-size: 15px;
}

/* 修改子类卡片样式名避免冲突 */
.subtype-item {
  flex: 1;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
}

.subtype-item h3 {
  font-size: 16px;
  margin-bottom: 20px;
  margin: 0 0 8px;
}

.subtype-item:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-4px);
}

.subtype-item p {
  margin: 0;
  color: #606266;
  font-size: 13px;
}

.subtype-content {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #dcdfe6;
  color: #303133;
}

.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-leave-to {
  opacity: 0;
}

/* 控制整个 info-card 的内边距 */
.info-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 20px;
  border-radius: 20px;
}

.result-card {
  flex: 1;
  border-radius: 20px;
  padding: 20px;
}

.info-row {
  display: flex;
  align-items: center; 
  gap: 20px;           
  min-height: 36px;
}

.label {
  min-width: 160px;
  text-align: left;
  font-weight: 600;
  color: #303133;
}

.value {
  flex: 1;
  color: #606266;
}

/* 特征卡片部分 */
.features-row {
  display: flex;
  gap: 25px;
}

.feature-card {
  flex: 1;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  font-size: 18px;
  font-weight: bold;
  padding: 15px;
  color: #fff;
}

.card-header.gene {
  background: linear-gradient(135deg, #f5adb8, #f8d4d9);
}

.card-header.protein {
  background: linear-gradient(135deg, #facbb3, #fde5d9);
}

.card-header.transcript {
  background: linear-gradient(135deg, #bbddc2, #d8e2da);
}

.feature-card ul {
  list-style: none;
  padding: 15px;
}

.feature-card li {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  color: #303133;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 10px;
}

.dot.gene {
  background-color: #F5ADB8;
}

.dot.protein {
  background-color: #facbb3;
}

.dot.transcript {
  background-color: #bbddc2;
}

.conclusion-card {
  margin-bottom: 50px;
  padding: 20px;
}

.plan-button {
  background: linear-gradient(135deg, #f5adb8, #ffccd3, #fde5d9, #d8e2da, #e9f4f4);
  color: #808080;
  border: none;
  border-radius: 26px;
  padding: 12px 32px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
}
</style>