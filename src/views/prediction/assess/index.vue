<template>
  <div class="patient-panel">
    <!-- 阶段 1：评估进行中 -->
    <div v-if="loading" class="loading-box">
      <el-button class="sync-btn" @click="startEvaluation">一键同步资料</el-button>
      <div v-if="evaluating" class="progress-area">
        <el-progress :percentage="progress" :stroke-width="12" color="#fde5d9" />
        <p class="progress-text">多位医生正在评估中，请稍后...</p>
      </div>
    </div>

    <!-- 阶段 2：评估结果 -->
    <div v-else>
      <el-alert class="note" type="info" :closable="false" show-icon
        title="本结果仅作健康参考，不能替代医生诊断。如有不适，请及时就医。"/>
      <!-- 结果概览卡 -->
      <div class="summary-card" :class="uiClass(final.rule)">
        <div class="summary-left">
          <div class="score" :style="{ color: scoreColor() }">{{ riskScore }}</div>
          <div class="label">风险指数</div>
        </div>
        <div class="summary-right">
          <div class="title">{{ titleText(final.rule) }}</div>
          <div class="subtitle">{{ subtitleText(final.rule) }}</div>
          <div class="advice">
            <span>医生讨论结果：</span>
            <el-tag :type="consistencyTag">{{ consistencyText }}</el-tag>
          </div>
        </div>
        <div class="assess-again">
          <span class="question">对结果有疑问？</span>
          <el-button class="assess-btn">重新评估</el-button>
        </div>
      </div>

      <!-- 医生评分折叠 -->
      <el-card class="more">
        <el-collapse>
          <el-collapse-item>
              <template #title>
                <span class="collapse-title">查看各医生评估详情</span>
              </template>
            <div class="doctor-bars">
              <div v-for="m in modelViews" :key="m.name" class="bar-row">
                <span class="mname">{{ m.display }}</span>
                <el-progress :percentage="m.tendency" :text-inside="true" :stroke-width="20" :color="progressColor" />
                <span class="hint">{{ m.hint }}</span>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-card>

      <!-- 医生意见与说明 -->
      <div class="card-row">
        <el-card class="explain">
          <div class="section-title">这个数值代表什么？</div>
          <p class="explain-text">{{ reason }}</p>
        </el-card>
        <el-card class="reasons">
          <div class="section-title">医生这样认为</div>
          <div class="chips">
            <el-tag v-for="(r,i) in consensusReasons" :key="i" effect="plain" size="small">{{ r }}</el-tag>
          </div>
          <el-alert v-if="consistencyText==='有分歧' || final.rule==='gray'" type="warning" :closable="false"
          title="建议两周内进行线下复查。" show-icon/>
        </el-card>
      </div>

      <!-- 报告 -->
      <el-card class="report-preview">
        <div class="section-title">报告摘要</div>
        <p class="report-text">
          您的综合风险评估指数为 <b>{{ riskScore }}/100</b>，提示存在中度患病风险。
          结合临床信息、影像学特征与分子标记物，多位医生协同分析后得出。
          建议进一步影像学检查并与医生沟通后续方案。
        </p>
        <div class="report-actions">
          <el-button class="download-btn" @click="downloadPDF">下载PDF报告</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PatientSimmdPanel',
  data() {
    return {
      loading: true,
      evaluating: false,
      progress: 0,
      riskScore: 72,
      final: { rule: 'rule-in' },
      consensusReasons: ['结节形态良性','Ki67略高需随访','无家族史风险低'],
      modelViews: [
        { name: 'xgb', display: '医生A', tendency: 82, hint: '建议检查' },
        { name: 'ftt', display: '医生B', tendency: 76, hint: '倾向检查' },
        { name: 'ebm', display: '医生C', tendency: 68, hint: '建议复查' },
        { name: 'logit', display: '医生D', tendency: 60, hint: '建议随访' }
      ],
      reason: "风险指数代表基于多模态数据的总体评估，数值越高风险越大，请结合医生意见综合判断。"
    }
  },
  computed: {
    consistencyText() {
      const vals = this.modelViews.map(v => v.tendency)
      const mean = vals.reduce((a,b)=>a+b,0)/vals.length
      const std = Math.sqrt(vals.reduce((s,x)=>s+(x-mean)**2,0)/vals.length)
      if (std < 8) return '高度一致'
      if (std < 15) return '较一致'
      return '有分歧'
    },
    consistencyTag() {
      return this.consistencyText === '有分歧' ? 'warning' : 'success'
    }
  },
  methods: {
    uiClass(rule){
      return rule==='rule-in' ? 'warn'
           : rule==='rule-out' ? 'safe'
           : 'neutral'
    },
    scoreColor() {
      if (this.riskScore <= 60) return '#4CAF50'
      if (this.riskScore <= 80) return '#FED65F' /* 学术黄 */
      return '#F44336'
    },
    titleText(rule){
      return rule==='rule-in' ? '风险指数偏中' :
             rule==='rule-out' ? '风险较低' : '指数偏高'
    },
    subtitleText(rule){
      return rule==='rule-in'
        ? '建议补充检查或与医生沟通'
        : rule==='rule-out'
        ? '倾向良性，可定期复查'
        : '存在异常信号，建议就医'
    },
    startEvaluation() {
      this.evaluating = true;
      let timer = setInterval(() => {
        if (this.progress <= 92) this.progress += 8;
        else {
          clearInterval(timer);
          this.loading = false;
          this.evaluating = false;
        }
      }, 300)
    },
    progressColor(p) {
      return p < 70 ? '#d8e2da' : '#ffccd3';
    },
    downloadPDF() {
      window.print()
    }
  }
}
</script>

<style scoped>
.patient-panel {
  width: 85%;
  max-width: 960px;
  margin: 80px auto 120px;
  display: flex;
  flex-direction: column;
  gap: 48px;
  font-family: "Inter", "PingFang SC", sans-serif;
  color: #2e2e2e;
  background: none;
}

/* 加载阶段 */
.loading-box {
  text-align: center;
  margin-top: 140px;
}
.sync-btn {
  background: linear-gradient(135deg, #f5adb8, #ffccd3, #fde5d9, #d8e2da, #e9f4f4);
  border: none;
  padding: 14px 36px;
  border-radius: 28px;
  color: #808080;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}
.sync-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(254, 215, 245, 0.35);
}
.progress-area {
  margin-top: 40px;
}
.progress-text {
  margin-top: 16px;
  font-size: 15px;
  color: #666;
}

/* 结果卡 */
.summary-card {
  display: flex;
  align-items: center;
  border-radius: 18px;
  padding: 36px 48px;
  margin-top: 20px;
  background: #fff;
  border: 1px solid #eaeaea;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  justify-content: space-around;
}
.summary-left{
  flex-shrink: 0;
  text-align: center;
  margin-right: 50px;
}
.score {
  font-size: 52px;
  font-weight: 700;
  line-height: 1;
  transition: color 0.3s ease;
}
.label {
  font-size: 14px;
  color: #888;
  margin-top: 6px;
}
.summary-right {
  flex: 1;
  line-height: 1.8;
  margin-left: 20px;
}
.assess-again {
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: center;
  justify-content: left;
  .question {
    font-size: 15px;
    color: #999;
  }
}
.assess-btn {
  background: linear-gradient(135deg, #f5adb8, #ffccd3, #fde5d9, #d8e2da, #e9f4f4);
  color: #808080;
  border: none;
  border-radius: 26px;
  padding: 12px 32px;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
}
.assess-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(162, 228, 181, 0.35);
}
.title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}
.subtitle {
  font-size: 15px;
  color: #777;
  margin-top: 8px;
}
.advice {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #555;
}
.advice .el-tag {
  border: none;
  background: #f5f5f5;
  color: #6CA8F1;
  border-radius: 6px;
}

/* 折叠面板 */
.more {
  border-radius: 14px;
  background: #fff;
  padding: 20px 28px;
  margin-top: 20px;
}
.collapse-title {
  font-size: 16px;
  font-weight: 600;
  color: #2e2e2e;
}
.bar-row {
  display: grid;
  grid-template-columns: 80px 1fr 120px;
  gap: 12px;
  align-items: center;
  margin: 10px 0;
}
.mname { font-size: 14px; color: #444; }
.hint { font-size: 13px; color: #999; }

/* 医生意见与说明*/
.card-row {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  margin-top: 20px;
}
.card-row .el-card {
  flex: 1;
  border-radius: 14px;
  border: 1px solid #ececec;
  padding: 28px 32px;
}
.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #333;
  margin-bottom: 14px;
}
.explain-text {
  font-size: 14px;
  color: #555;
  line-height: 1.8;
}
.el-tag {
  border-radius: 6px;
  background: #f8fbff;
  color: #4FC3B8;
  border: none;
  font-size: 13px;
  margin: 5px;
}

/*  报告  */
.report-preview {
  background: #fff;
  border-radius: 16px;
  margin-top: 20px;
  padding: 36px 40px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}
.report-text {
  color: #444;
  line-height: 1.9;
  font-size: 15px;
  margin-bottom: 24px;
}
.download-btn {
  background: linear-gradient(135deg, #f5adb8, #ffccd3, #fde5d9, #d8e2da, #e9f4f4);
  color: #808080;
  border: none;
  border-radius: 26px;
  padding: 12px 32px;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
}
.download-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(108,168,241,0.35);
}
</style>


