<template>
  <div class="treatment-page">
    <!-- 顶部标题标题栏 -->
    <div class="page-header">
      <div class="header-content">
        <h2 class="page-title">诊疗建议
          <el-tag type="success" size="small" class="page-tag">最新更新</el-tag>
        </h2>
        <p class="page-subtitle">基于患者病情分析的个性化治疗方案</p>
      </div>
      
      <div class="header-actions">
        <el-button class="download-btn" icon="el-icon-download" @click="printPatientInfo">打印报告</el-button>
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="content-container">
      <!-- 患者基本信息卡片 -->
      <el-card shadow="hover" class="info-card">
        <el-row :gutter="20" type="flex" align="top" class="row-container">
          <el-col :span="8" class="info-item">
            <div class="info-label">患者信息</div>
            <div class="info-row">
              <span class="label">患者</span>
              <span class="value">{{ patientName }}</span>
            </div>
            <div class="info-row">
              <span class="label">性别</span>
              <span class="value">女</span>
            </div>
            <div class="info-row">
              <span class="label">年龄</span>
              <span class="value">48</span>
            </div>
          </el-col>
          
          <div class="vertical-divider"></div>
          <el-col :span="8" class="info-item">      
            <div class="info-label">风险评估</div>      
            <div class="risk-assessment">        
              <span class="risk-value" :style="{ color: scoreColor(currentPercentage) }">
                {{ currentPercentage }}分</span>        
              <el-progress :percentage="currentPercentage" stroke-width="6" 
                :color="riskColor" :show-text="false" class="risk-progress"  />      
            </div>    
          </el-col>
          
          <div class="vertical-divider"></div>
          <el-col :span="8" class="info-item">
            <div class="info-label">亚型分析</div>
            <div class="info-value">Luminal A 型早期乳腺癌</div>
            <el-tag type="success" size="mini" class="subtype-tag">激素敏感性</el-tag>
          </el-col>
        </el-row>
      </el-card>

      <!-- 治疗方案区域 -->
      <div class="plan-section">
        <div class="section-header">
          <i class="el-icon-stethoscope section-icon"></i>
          <h3 class="section-title">诊疗方案</h3>
          <el-divider direction="vertical" class="header-divider"></el-divider>
          <el-text type="secondary">共2个方案可供选择</el-text>
        </div>
        
        <el-tabs v-model="activePlan" class="plan-tabs" tab-position="top">
          <!-- 方案一详细内容 -->
          <el-tab-pane label="方案一" name="plan1">
            <el-card shadow="hover" class="plan-card">
              <!-- 方案一内容保持不变 -->
              <div class="plan-header">
                <div class="plan-meta">
                  <el-rate v-model="plan1Rating" disabled allow-half class="plan-rating"></el-rate>
                  <el-text size="small" type="info">适用性评分：4.5/5</el-text>
                </div>
                
                <div class="plan-tags">
                  <el-tag type="primary" size="mini">优先推荐</el-tag>
                  <el-tag type="success" size="mini">创伤小</el-tag>
                  <el-tag type="info" size="mini">恢复快</el-tag>
                </div>
              </div>
              
              <el-divider class="plan-divider"></el-divider>
              
              <!-- 治疗目标、步骤等内容保持不变 -->
              <div class="plan-section-title">
                <i class="el-icon-target"></i> 治疗目标
              </div>
              <div class="plan-section-content">
                <p>完整切除肿瘤组织，保留乳房外形与功能，通过内分泌治疗预防复发，结合中医药调理提高生活质量，降低治疗相关不良反应。</p>
              </div>
              
              <div class="plan-section-title">
                <i class="el-icon-list"></i> 详细治疗步骤
              </div>
              <ul class="plan-items">
                <li class="plan-item">
                  <div class="step-number">1</div>
                  <div class="step-content">
                    <div class="step-title">乳腺癌保乳手术</div>
                    <div class="step-details">
                      <p>行肿瘤扩大切除术（切除肿瘤及周围1-2cm正常组织）+前哨淋巴结活检</p>
                      <p><strong>手术时间</strong>：约90分钟</p>
                      <p><strong>麻醉方式</strong>：全身麻醉</p>
                      <p><strong>术后观察</strong>：住院3-5天，观察伤口愈合情况</p>
                    </div>
                  </div>
                </li>
                
                <li class="plan-item">
                  <div class="step-number">2</div>
                  <div class="step-content">
                    <div class="step-title">术后辅助内分泌治疗</div>
                    <div class="step-details">
                      <p>他莫昔芬 20mg/日，连续服用5年</p>
                      <p><strong>用药监测</strong>：每3个月复查妇科超声、肝功能</p>
                      <p><strong>常见反应</strong>：可能出现潮热、盗汗、关节疼痛等症状</p>
                    </div>
                  </div>
                </li>
                
                <li class="plan-item">
                  <div class="step-number">3</div>
                  <div class="step-content">
                    <div class="step-title">中药辅助治疗</div>
                    <div class="step-details">
                      <p>香砂六君子汤加减：党参15g，白术12g，茯苓15g，甘草6g，陈皮9g，半夏9g，木香6g，砂仁6g</p>
                      <p><strong>用法</strong>：每日1剂，水煎400ml，分早晚两次温服，连续服用3个月为一疗程</p>
                      <p><strong>功效</strong>：健脾益气，减轻内分泌治疗引起的胃肠道反应</p>
                    </div>
                  </div>
                </li>
                
                <li class="plan-item">
                  <div class="step-number">4</div>
                  <div class="step-content">
                    <div class="step-title">针灸调理</div>
                    <div class="step-details">
                      <p>针对更年期症状（潮热、失眠）进行治疗</p>
                      <p><strong>取穴</strong>：三阴交、太溪、关元、肾俞、百会</p>
                      <p><strong>频率</strong>：每周2次，每次30分钟，10次为一疗程</p>
                    </div>
                  </div>
                </li>
                
                <li class="plan-item">
                  <div class="step-number">5</div>
                  <div class="step-content">
                    <div class="step-title">饮食与生活指导</div>
                    <div class="step-details">
                      <p><strong>饮食原则</strong>：辨证施膳，宜食健脾益气食物（如山药、莲子、大枣），避免辛辣刺激、生冷油腻食物</p>
                      <p><strong>运动建议</strong>：术后1个月可开始轻度运动（如散步），逐渐增加至每日30分钟</p>
                      <p><strong>心理调节</strong>：保持良好心态，必要时进行心理咨询</p>
                    </div>
                  </div>
                </li>
              </ul>
              
              <div class="plan-section-title">
                <i class="el-icon-pie-chart"></i> 预期效果与随访计划
              </div>
              <div class="plan-section-content">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="expected-title">预期效果</div>
                    <ul class="expected-list">
                      <li>局部控制率：95%以上</li>
                      <li>5年无病生存率：85%以上</li>
                      <li>乳房外形保留满意度：90%以上</li>
                      <li>生活质量评分：≥80分</li>
                    </ul>
                  </el-col>
                  <el-col :span="12">
                    <div class="expected-title">随访计划</div>
                    <ul class="expected-list">
                      <li>术后1-2年：每3个月复查一次</li>
                      <li>术后3-5年：每6个月复查一次</li>
                      <li>5年以上：每年复查一次</li>
                      <li>复查项目：乳腺超声、钼靶、肿瘤标志物、血常规等</li>
                    </ul>
                  </el-col>
                </el-row>
              </div>
              
              <div class="plan-actions">
                <el-button type="primary" size="small" icon="el-icon-question" @click="showPrognosisDetail(1)">预后详情</el-button>
              </div>
            </el-card>
          </el-tab-pane>

          <!-- 方案二详细内容 -->
          <el-tab-pane label="方案二" name="plan2">
            <el-card shadow="hover" class="plan-card">
              <!-- 方案二内容保持不变 -->
              <div class="plan-header">
                <div class="plan-meta">
                  <el-rate v-model="plan2Rating" disabled allow-half class="plan-rating"></el-rate>
                  <el-text size="small" type="info">适用性评分：3.5/5</el-text>
                </div>
                
                <div class="plan-tags">
                  <el-tag type="warning" size="mini">备选方案</el-tag>
                  <el-tag type="info" size="mini">综合治疗</el-tag>
                  <el-tag type="danger" size="mini">副作用可能较大</el-tag>
                </div>
              </div>
              
              <el-divider class="plan-divider"></el-divider>
              
              <!-- 治疗目标、步骤等内容保持不变 -->
              <div class="plan-section-title">
                <i class="el-icon-target"></i> 治疗目标
              </div>
              <div class="plan-section-content">
                <p>通过综合治疗手段最大限度清除体内肿瘤细胞，降低复发转移风险，中医药辅助治疗减轻化疗不良反应，提高患者耐受性和生活质量。</p>
              </div>
              
              <div class="plan-section-title">
                <i class="el-icon-list"></i> 详细治疗步骤
              </div>
              <ul class="plan-items">
                <li class="plan-item">
                  <div class="step-number">1</div>
                  <div class="step-content">
                    <div class="step-title">乳腺癌改良根治术</div>
                    <div class="step-details">
                      <p>行全乳切除+腋窝淋巴结清扫术</p>
                      <p><strong>手术时间</strong>：约120分钟</p>
                      <p><strong>麻醉方式</strong>：全身麻醉</p>
                      <p><strong>术后观察</strong>：住院7-10天，注意皮瓣愈合情况</p>
                    </div>
                  </div>
                </li>
                
                <li class="plan-item">
                  <div class="step-number">2</div>
                  <div class="step-content">
                    <div class="step-title">术后辅助化疗</div>
                    <div class="step-details">
                      <p>AC方案：多柔比星（A）+环磷酰胺（C），每21天为一周期，共4周期</p>
                      <p><strong>用药监测</strong>：化疗期间每周复查血常规、肝肾功能</p>
                      <p><strong>常见反应</strong>：恶心呕吐、脱发、骨髓抑制、乏力</p>
                    </div>
                  </div>
                </li>
                
                <li class="plan-item">
                  <div class="step-number">3</div>
                  <div class="step-content">
                    <div class="step-title">靶向药物治疗</div>
                    <div class="step-details">
                      <p>基于BRCA基因突变检测结果，给予奥拉帕利 300mg/次，每日2次</p>
                      <p><strong>用药周期</strong>：连续服用1年</p>
                      <p><strong>监测项目</strong>：每2个月复查血常规、肝肾功能、肿瘤标志物</p>
                    </div>
                  </div>
                </li>
                
                <li class="plan-item">
                  <div class="step-number">4</div>
                  <div class="step-content">
                    <div class="step-title">中医辅助治疗</div>
                    <div class="step-details">
                      <p>参芪扶正汤加减：黄芪30g，党参15g，白术12g，茯苓15g，当归12g，白芍15g，川芎9g，甘草6g</p>
                      <p><strong>用法</strong>：化疗期间及化疗后3个月内服用，每日1剂，水煎服</p>
                      <p><strong>功效</strong>：益气养血，减轻化疗所致骨髓抑制和消化道反应</p>
                    </div>
                  </div>
                </li>
                
                <li class="plan-item">
                  <div class="step-number">5</div>
                  <div class="step-content">
                    <div class="step-title">康复治疗</div>
                    <div class="step-details">
                      <p><strong>上肢功能锻炼</strong>：术后1周开始进行循序渐进的患侧上肢功能锻炼，预防肩关节活动受限</p>
                      <p><strong>中医外治法</strong>：穴位贴敷（内关、足三里）缓解化疗所致恶心呕吐</p>
                      <p><strong>运动指导</strong>：化疗结束后可进行适度运动，如八段锦、太极拳等，每次20-30分钟</p>
                    </div>
                  </div>
                </li>
              </ul>
              
              <div class="plan-section-title">
                <i class="el-icon-pie-chart"></i> 预期效果与随访计划
              </div>
              <div class="plan-section-content">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="expected-title">预期效果</div>
                    <ul class="expected-list">
                      <li>局部控制率：98%以上</li>
                      <li>5年无病生存率：88%以上</li>
                      <li>上肢功能恢复率：90%以上</li>
                      <li>生活质量评分：≥75分</li>
                    </ul>
                  </el-col>
                  <el-col :span="12">
                    <div class="expected-title">随访计划</div>
                    <ul class="expected-list">
                      <li>术后1年：每3个月复查一次</li>
                      <li>术后2-3年：每6个月复查一次</li>
                      <li>3年以上：每年复查一次</li>
                      <li>复查项目：胸部CT、乳腺超声、肿瘤标志物、血常规等</li>
                    </ul>
                  </el-col>
                </el-row>
              </div>
              
              <div class="plan-actions">
                <el-button type="primary" size="small" icon="el-icon-question" @click="showPrognosisDetail(2)">预后详情</el-button>
              </div>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 数字生命悬浮球 -->
    <div class="digital-life-ball" @click="gotoDigitalLifePage">
      <div class="ball-content">
        <i class="el-icon-user-solid ball-icon"></i>
        <div class="ball-text">AI小助手</div>
      </div>
    </div>

    <!-- 预后详情弹窗 -->
    <el-dialog :visible.sync="prognosisVisible" :title="`方案${currentPlan}预后详情`" width="80%"
      :before-close="handleClose" :max-width="['768px', '90%']" custom-class="prognosis-dialog">
      <div class="prognosis-content">
        <!-- 方案一预后详情 -->
        <div v-if="currentPlan === 1">
          <el-card shadow="none" class="prognosis-card">
            <div slot="header" class="prognosis-header">
              <h4>保乳手术+内分泌治疗预后分析</h4>
            </div>
            
            <!-- 优化后的预后统计数据 - 使用环形进度条 -->
            <el-row :gutter="20" class="prognosis-stats">
              <el-col :span="6" :xs="12" class="stat-item">
                <div class="stat-card">
                  <div class="stat-chart">
                    <el-progress  type="circle" :percentage="85" :stroke-width="8" 
                    :width="80" class="circle-progress">
                      <div class="progress-inner">
                        <span class="progress-value">85%</span>
                        <span class="progress-label">5年生存率</span>
                      </div>
                    </el-progress>
                  </div>
                  <div class="stat-note">高于平均水平12%</div>
                </div>
              </el-col>
              
              <el-col :span="6" :xs="12" class="stat-item">
                <div class="stat-card">
                  <div class="stat-chart">
                    <el-progress type="circle" :percentage="15" :stroke-width="8" :width="80"
                      stroke="#e6a23c" class="circle-progress">
                      <div class="progress-inner">
                        <span class="progress-value">15%</span>
                        <span class="progress-label">复发风险</span>
                      </div>
                    </el-progress>
                  </div>
                  <div class="stat-note">主要集中在术后3年内</div>
                </div>
              </el-col>
              
              <el-col :span="6" :xs="12" class="stat-item">
                <div class="stat-card">
                  <div class="stat-chart">
                    <el-progress type="circle" :percentage="85" :stroke-width="8" :width="80"
                      stroke="#409eff" class="circle-progress">
                      <div class="progress-inner">
                        <span class="progress-value">85分</span>
                        <span class="progress-label">生活质量</span>
                      </div>
                    </el-progress>
                  </div>
                  <div class="stat-note">满分100分，含心理评估</div>
                </div>
              </el-col>
              
              <el-col :span="6" :xs="12" class="stat-item">
                <div class="stat-card">
                  <div class="stat-chart">
                    <el-progress type="circle" :percentage="75" 
                      :stroke-width="8" 
                      :width="80"
                      stroke="#67c23a"
                      class="circle-progress"
                    >
                      <div class="progress-inner">
                        <span class="progress-value">3个月</span>
                        <span class="progress-label">恢复周期</span>
                      </div>
                    </el-progress>
                  </div>
                  <div class="stat-note">至正常生活状态</div>
                </div>
              </el-col>
            </el-row>
        
            <!-- 预后注意事项 -->
            <div class="prognosis-section">
              <h5 class="section-title"><i class="el-icon-exclamation-circle"></i> 预后注意事项</h5>
              
              <el-collapse v-model="activeCollapse1" class="prognosis-collapse">
                <el-collapse-item title="药物治疗注意事项" name="item1">
                  <ul class="note-list">
                    <li><i class="el-icon-check-circle"></i> 他莫昔芬需每日固定时间服用，不可随意停药或更改剂量</li>
                    <li><i class="el-icon-check-circle"></i> 如出现严重潮热、盗汗，可在医生指导下调整用药方案</li>
                    <li><i class="el-icon-check-circle"></i> 每3个月进行一次妇科超声检查，监测子宫内膜变化</li>
                    <li><i class="el-icon-check-circle"></i> 定期检查肝功能，如出现黄疸、乏力等症状应立即就医</li>
                    <li><i class="el-icon-check-circle"></i> 避免同时服用影响他莫昔芬代谢的药物（如抗抑郁药、某些抗生素）</li>
                  </ul>
                </el-collapse-item>
                
                <el-collapse-item title="日常生活管理" name="item2">
                  <ul class="note-list">
                    <li><i class="el-icon-check-circle"></i> 保持规律作息，避免熬夜，保证每日7-8小时睡眠</li>
                    <li><i class="el-icon-check-circle"></i> 坚持适度运动，术后1个月可开始散步（每次15-20分钟），逐渐增加至每日30分钟</li>
                    <li><i class="el-icon-check-circle"></i> 饮食宜清淡富营养，多食新鲜蔬果、全谷物和优质蛋白</li>
                    <li><i class="el-icon-check-circle"></i> 避免摄入含激素类食物（如蜂王浆、雪蛤等）</li>
                    <li><i class="el-icon-check-circle"></i> 保持良好情绪状态，避免长期精神紧张和焦虑</li>
                  </ul>
                </el-collapse-item>
                
                <el-collapse-item title="复查与监测计划" name="item3">
                  <ul class="note-list">
                    <li><i class="el-icon-check-circle"></i> 术后1-2年：每3个月进行一次乳腺超声、肿瘤标志物（CEA、CA153）检查</li>
                    <li><i class="el-icon-check-circle"></i> 每6个月进行一次乳腺钼靶检查</li>
                    <li><i class="el-icon-check-circle"></i> 术后3-5年：每6个月复查一次，检查项目同前</li>
                    <li><i class="el-icon-check-circle"></i> 5年以上：每年复查一次，终身随访</li>
                    <li><i class="el-icon-check-circle"></i> 出现乳房肿块、疼痛、异常分泌物等症状应立即就诊</li>
                  </ul>
                </el-collapse-item>
                
                <el-collapse-item title="可能出现的并发症及应对" name="item4">
                  <ul class="note-list">
                    <li><i class="el-icon-check-circle"></i> 伤口感染：表现为红肿热痛，需及时就医抗感染治疗</li>
                    <li><i class="el-icon-check-circle"></i> 上肢淋巴水肿：避免患侧上肢提重物、测血压和静脉穿刺</li>
                    <li><i class="el-icon-check-circle"></i> 内分泌治疗相关骨质疏松：适当补充钙剂和维生素D，定期骨密度检测</li>
                    <li><i class="el-icon-check-circle"></i> 更年期症状加重：可在医生指导下采用中药或非激素类药物缓解</li>
                  </ul>
                </el-collapse-item>
              </el-collapse>
            </div>
            <el-divider></el-divider>
          </el-card>
        </div>
        
        <!-- 方案二预后详情 -->
        <div v-if="currentPlan === 2">
          <el-card shadow="none" class="prognosis-card">
            <div slot="header" class="prognosis-header">
              <h4>根治术+综合治疗预后分析</h4>
            </div>
            <!-- 优化后的预后统计数据 - 使用环形进度条 -->
            <el-row :gutter="20" class="prognosis-stats">
              <el-col :span="6" :xs="12" class="stat-item">
                <div class="stat-card">
                  <div class="stat-chart">
                    <el-progress 
                      type="circle" 
                      :percentage="88" 
                      :stroke-width="8" 
                      :width="80"
                      class="circle-progress"
                    >
                      <div class="progress-inner">
                        <span class="progress-value">88%</span>
                        <span class="progress-label">5年生存率</span>
                      </div>
                    </el-progress>
                  </div>
                  <div class="stat-note">高于平均水平15%</div>
                </div>
              </el-col>
              
              <el-col :span="6" :xs="12" class="stat-item">
                <div class="stat-card">
                  <div class="stat-chart">
                    <el-progress 
                      type="circle" 
                      :percentage="8" 
                      :stroke-width="8" 
                      :width="80"
                      stroke="#e6a23c"
                      class="circle-progress"
                    >
                      <div class="progress-inner">
                        <span class="progress-value">8%</span>
                        <span class="progress-label">复发风险</span>
                      </div>
                    </el-progress>
                  </div>
                  <div class="stat-note">各时期风险较均衡</div>
                </div>
              </el-col>
              
              <el-col :span="6" :xs="12" class="stat-item">
                <div class="stat-card">
                  <div class="stat-chart">
                    <el-progress 
                      type="circle" 
                      :percentage="75" 
                      :stroke-width="8" 
                      :width="80"
                      stroke="#409eff"
                      class="circle-progress"
                    >
                      <div class="progress-inner">
                        <span class="progress-value">75分</span>
                        <span class="progress-label">生活质量</span>
                      </div>
                    </el-progress>
                  </div>
                  <div class="stat-note">满分100分，含心理评估</div>
                </div>
              </el-col>
              
              <el-col :span="6" :xs="12" class="stat-item">
                <div class="stat-card">
                  <div class="stat-chart">
                    <el-progress 
                      type="circle" 
                      :percentage="50" 
                      :stroke-width="8" 
                      :width="80"
                      stroke="#67c23a"
                      class="circle-progress"
                    >
                      <div class="progress-inner">
                        <span class="progress-value">6个月</span>
                        <span class="progress-label">恢复周期</span>
                      </div>
                    </el-progress>
                  </div>
                  <div class="stat-note">至正常生活状态</div>
                </div>
              </el-col>
            </el-row>
            
            <!-- 预后注意事项 -->
            <div class="prognosis-section">
              <h5 class="section-title"><i class="el-icon-exclamation-circle"></i> 预后注意事项</h5>
              
              <el-collapse v-model="activeCollapse2" class="prognosis-collapse">
                <el-collapse-item title="综合治疗注意事项" name="item1">
                  <ul class="note-list">
                    <li><i class="el-icon-check-circle"></i> 化疗期间每周检查血常规，如白细胞过低需及时处理</li>
                    <li><i class="el-icon-check-circle"></i> 奥拉帕利需每日两次服用，整片吞服，不可咀嚼或压碎</li>
                    <li><i class="el-icon-check-circle"></i> 靶向治疗期间避免同时使用强效CYP3A抑制剂（如酮康唑）</li>
                    <li><i class="el-icon-check-circle"></i> 化疗和靶向治疗期间需严格避孕（至少治疗结束后6个月）</li>
                    <li><i class="el-icon-check-circle"></i> 如出现严重腹泻、皮疹或呼吸困难，应立即就医</li>
                  </ul>
                </el-collapse-item>
                
                <el-collapse-item title="术后康复训练" name="item2">
                  <ul class="note-list">
                    <li><i class="el-icon-check-circle"></i> 术后1-7天：进行握拳、伸指、腕部活动，每日3-4次，每次10-15分钟</li>
                    <li><i class="el-icon-check-circle"></i> 术后2周：开始进行肘关节活动，逐渐增加活动范围</li>
                    <li><i class="el-icon-check-circle"></i> 术后1个月：可进行肩关节活动，如梳头、爬墙等动作</li>
                    <li><i class="el-icon-check-circle"></i> 康复训练需循序渐进，避免过度疲劳和剧烈运动</li>
                    <li><i class="el-icon-check-circle"></i> 坚持长期锻炼，预防肩关节粘连和上肢功能障碍</li>
                  </ul>
                </el-collapse-item>
                
                <el-collapse-item title="复查与监测计划" name="item3">
                  <ul class="note-list">
                    <li><i class="el-icon-check-circle"></i> 术后1年：每3个月进行一次胸部CT、肿瘤标志物、血常规检查</li>
                    <li><i class="el-icon-check-circle"></i> 每6个月进行一次乳腺超声和腹部超声检查</li>
                    <li><i class="el-icon-check-circle"></i> 术后2-3年：每6个月复查一次，检查项目同前</li>
                    <li><i class="el-icon-check-circle"></i> 3年以上：每年复查一次，终身随访</li>
                    <li><i class="el-icon-check-circle"></i> 靶向治疗期间每2个月检查一次肝肾功能</li>
                  </ul>
                </el-collapse-item>
                
                <el-collapse-item title="长期健康管理" name="item4">
                  <ul class="note-list">
                    <li><i class="el-icon-check-circle"></i> 保持健康体重，避免肥胖（BMI建议维持在18.5-24）</li>
                    <li><i class="el-icon-check-circle"></i> 戒烟限酒，避免接触二手烟和其他致癌物质</li>
                    <li><i class="el-icon-check-circle"></i> 定期进行心脏功能检查（多柔比星可能影响心脏功能）</li>
                    <li><i class="el-icon-check-circle"></i> 关注心理健康，必要时寻求专业心理咨询</li>
                    <li><i class="el-icon-check-circle"></i> 可考虑加入乳腺癌康复互助小组，获取更多支持</li>
                  </ul>
                </el-collapse-item>
              </el-collapse>
            </div>
            
            <el-divider></el-divider>
          </el-card>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="prognosisVisible = false">关闭</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>

export default {
  name: "TreatmentAdvice",
  data() {
    return {
      patientName: '***',
      activePlan: "plan1",
      plan1Rating: 4.5,
      plan2Rating: 3.5,
      prognosisVisible: false,  // 预后详情弹窗控制
      currentPlan: 1,
      targetPercentage: 72, 
      currentPercentage: 0, 
      progressTimer: null,
      // 折叠面板状态管理
      activeCollapse1: ['item1'],  // 方案一折叠面板默认展开项
      activeCollapse2: ['item1']   // 方案二折叠面板默认展开项
    };
  },
  computed: {
    riskColor() {
      if (this.currentPercentage >= 80) {
        return '#f56c6c';
      } else if (this.currentPercentage >= 60) {
        return '#fed65f'; 
      } else {
        return '#67c23a'; 
      }
    }
  },
  mounted() {
    this.startProgressAnimation();
  },
  beforeDestroy() {
    if (this.progressTimer) {
      clearInterval(this.progressTimer);
    }
  },
  methods: {
    gotoDigitalLifePage() {
      this.$router.push('/chat/index');
    },
    scoreColor(val) {
    if (val <= 60) return '#67C23A' // 绿色
    if (val <= 80) return '#fed65f' // 黄色
    return '#F56C6C'                // 红色
    },
    // 显例预后详情
    showPrognosisDetail(planNum) {
      this.currentPlan = planNum;
      this.prognosisVisible = true;
    },
    handleClose() {
      this.prognosisVisible = false;
    },
    //打印报告
     printPatientInfo() {
      try {
        this.$message({
          message: '正在准备打印信息...',
          type: 'info'
        })
        window.print()
      } catch (error) {
        console.error('打印患者信息失败:', error)
        this.$message.error('打印功能出现错误，请稍后重试')
      }
    },

    //导出报告
    generatePDF() {
      // 这里使用一个链接模拟PDF下载
      // 在实际项目中，这里应该连接到后端API
      const link = document.createElement('a')
      link.href = `data:application/pdf;base64,JVBERi0xLjcKJeLjz9MKNCAwIG9iago8PC9UeXBlL1hPYmplY3QvU3VidHlwZS9JbWFnZS9XaWR0aCA0MDAvSGVpZ2h0IDQwMC9CaXRzUGVyQ29tcG9uZW50IDgvQ29sb3JTcGFjZS9EZXZpY2VSR0IvRmlsdGVyL0RDVERlY29kZS9MZW5ndGggMzYzMz4+CnN0cmVhbQrHcPHZSOIRDxJKx1P9Tg+lEW1WNMRK1uHalyJGkLSj9AQ+YQVj+uX6s7Gg9TDG+9zcLJCyY39j50R6TxnzShxOh2pRBLFg4+1Q4YlGCe+T8PqLiGkKGJPCcTLHFQjxCkBQcqTqP9mWw3o4H2zy2ePuFV5o4jcwIUnMJb2WOw2aq7CvnOhQR6sPIvBsZZOc7F3Oej6fTDSJ8TpqbBM9QGLMPfJKA2viJmCdCJt1VtDdQvC/JccYMqNh+nEyY4hB8zkDfHLqtM6XJTKUFqJkgwL67Y40gHwJ5EZIB+BUv9gGJEUzGzrU`
      link.download = `${this.patientName}_乳腺癌诊疗建议报告.pdf`
      link.click()
    },

    startProgressAnimation() {
      if (this.progressTimer) {
        clearInterval(this.progressTimer);
      }
      
      this.progressTimer = setInterval(() => {
        this.currentPercentage += 1;
        if (this.currentPercentage >= this.targetPercentage) {
          this.currentPercentage = this.targetPercentage;
          clearInterval(this.progressTimer);
        }
      }, 30);
    },
  }
};
</script>

<style scoped>
.treatment-page {
  height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 40px;
  position: relative;
  overflow-y: auto;
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
.header-content {
  display: flex;
  flex-direction: column;
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
}
.page-subtitle {
  font-size: 14px;
  color: #8392a5;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 10px;
  .download-btn {
    background: linear-gradient(135deg, #f5adb8, #ffccd3, #fde5d9, #d8e2da, #e9f4f4);
    color: #808080;
    border: none;
    border-radius: 26px;
    padding: 12px 32px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s;
  }
}
.content-container {
  width: 95%;
  max-width: 1200px;
  margin: 0 auto;
}
.row-container {
  min-height: 160px;
}
.info-card {
  margin-bottom: 30px;
  border-radius: 8px;
  border: none;
  transition: all 0.3s ease;
}
.info-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.vertical-divider {
  width: 1px;
  background-color: #e0e0e0;  /* 灰色 */
  margin: 0 20px;
  align-self: stretch;
}
.info-label {
  min-height: 30px;
  line-height: 30px;
  font-weight: bold;
  font-size: 15px;
  color: #8392a5;
  margin-bottom: 15px;
}
.info-row {
  display: flex;
  align-items: center;            
  min-height: 32px;
}
.label {
  min-width: 160px;
  text-align: left;
  font-weight: 600;
  color: #303133;
}
.value {
  flex: 1;
  text-align: left;
}
.info-value {
  font-size: 16px;
  color: #1f2d3d;
  font-weight: 500;
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}
.info-item {
  display: flex;
  flex-direction: column;
}
.subtype-tag {
  margin-top: 5px;
  width: fit-content;
}

/* 风险评估样式 */
.risk-assessment {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.risk-value {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 5px;
  display: inline-block;
}

.risk-progress {
  width: 80%;
}

.risk-text {
  font-size: 14px;
  color: #f56c6c;
  margin-top: 5px;
}

/* 方案区域样式 */
.plan-section {
  background-color: #fff;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f2f5;
}

.header-divider {
  margin: 0 10px;
  height: 20px;
}

.section-icon {
  color: #f5adb8;
  font-size: 20px;
  margin-right: 10px;
}

.section-title {
  font-size: 18px;
  color: #1f2d3d;
  margin: 0;
  font-weight: 600;
}
/* 选项卡样式 */
.plan-tabs {
  --el-tabs-active-color: #f5adb8;
}
/* 方案卡片样式 */
.plan-card {
  margin-top: 15px;
  border-radius: 6px;
  border: 1px solid #f0f2f5;
  transition: all 0.3s ease;
  overflow: hidden;
}
.plan-card:hover {
  border-color: #e6f7ff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}
.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px dashed #f0f2f5;
}
.plan-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}
.plan-tags {
  display: flex;
  gap: 5px;
}
.plan-divider {
  margin: 10px 0;
}

.plan-section-title {
  font-size: 15px;
  color: #1f2d3d;
  font-weight: 600;
  margin: 20px 0 10px 0;
  display: flex;
  align-items: center;
}

.plan-section-title i {
  color: #f5adb8;
  margin-right: 8px;
  font-size: 16px;
}

/* 方案章节内容 */
.plan-section-content {
  padding: 0 15px;
  color: #4e5969;
  line-height: 1.7;
}

/* 方案列表样式 */
.plan-items {
  padding: 10px 0;
  margin: 0;
}

.plan-item {
  list-style: none;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 6px;
  transition: all 0.2s ease;
  display: flex;
  background-color: #fafafa;
}

.plan-item:hover {
  background-color: #f5f9ff;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #f5adb8;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  margin-right: 15px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 600;
  color: #1f2d3d;
  margin-bottom: 8px;
  font-size: 15px;
}

.step-details {
  color: #4e5969;
  font-size: 14px;
  line-height: 1.6;
}

.step-details p {
  margin: 5px 0;
}

.step-details strong {
  color: #1f2d3d;
}

/* 预期效果样式 */
.expected-title {
  font-weight: 600;
  color: #1f2d3d;
  margin-bottom: 10px;
  font-size: 14px;
}

.expected-list {
  padding-left: 20px;
  color: #4e5969;
  line-height: 1.7;
}

.expected-list li {
  margin-bottom: 5px;
}

/* 方案操作区 */
.plan-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px;
  border-top: 1px dashed #f0f2f5;
  background-color: #fafafa;
  margin-top: 15px;
}

/* 数字生命悬浮球样式 */
.digital-life-ball {
  position: fixed;
  right: 30px;
  bottom: 30px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f5adb8, #f6d6db);
  color: white;
  box-shadow: 0 4px 12px rgba(238, 169, 201, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1000;
}

.digital-life-ball:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(237, 181, 238, 0.4);
}

.ball-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ball-icon {
  font-size: 22px;
  margin-bottom: 3px;
}

.ball-text {
  font-size: 12px;
  line-height: 1;
}

/* 预后详情弹窗样式 */
.prognosis-dialog {
  border-radius: 8px;
}

.prognosis-content {
  font-size: 14px;
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 10px;
}

.prognosis-card {
  border: none;
}

.prognosis-header {
  padding: 0 0 15px 0;
  border-bottom: 1px solid #f0f2f5;
}

.prognosis-header h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #1f2d3d;
  font-weight: 600;
}

.header-desc {
  margin: 0;
  font-size: 13px;
  color: #8392a5;
}

/* 优化后的统计数据样式 - 环形进度条 */
.prognosis-stats {
  margin: 25px 0;
}

.stat-item {
  padding: 10px;
}

.stat-card {
  background-color: #fafafa;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.stat-chart {
  position: relative;
  margin-bottom: 10px;
}

::v-deep .circle-progress {
  position: relative;
}

.progress-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  width: 100%;
}

.progress-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2d3d;
  display: block;
  line-height: 1;
}

.progress-label {
  font-size: 12px;
  color: #8392a5;
  display: block;
  margin-top: 5px;
}

.stat-note {
  font-size: 12px;
  color: #8392a5;
  text-align: center;
  margin-top: 5px;
  line-height: 1.4;
}

.prognosis-section {
  margin-bottom: 20px;
}

.prognosis-section:last-child {
  margin-bottom: 0;
}

.prognosis-section .section-title {
  font-size: 15px;
  color: #1f2d3d;
  font-weight: 600;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.prognosis-section .section-title i {
  color: #f5adb8;
  margin-right: 8px;
}

.prognosis-collapse {
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}

::v-deep .el-collapse-item__header {
  font-weight: 500;
  padding: 12px 15px;
  background-color: #f7f8fa;
}

::v-deep .el-collapse-item__content {
  padding: 15px;
  border-top: 1px solid #e8e8e8;
}

.note-list {
  padding-left: 20px;
  margin: 0;
}

.note-list li {
  margin-bottom: 8px;
  line-height: 1.6;
  color: #4e5969;
}

.note-list li i {
  color: #67c23a;
  margin-right: 5px;
}

::v-deep .el-descriptions {
  margin-bottom: 15px;
}

::v-deep .el-descriptions__label {
  font-weight: 500;
}

::v-deep .el-alert {
  margin-bottom: 10px;
}

::v-deep .el-dialog__footer {
  padding: 15px 20px;
  border-top: 1px solid #f0f2f5;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .el-row {
    flex-direction: column;
  }
  
  .el-col {
    width: 100% !important;
    margin-bottom: 15px;
  }
  
  .page-header {
    padding: 20px 25px;
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .content-container {
    width: 90%;
  }
  
  .plan-section {
    padding: 15px;
  }
  
  .plan-item {
    flex-direction: column;
  }
  
  .step-number {
    margin-right: 0;
    margin-bottom: 10px;
    align-self: flex-start;
  }
  
  .prognosis-stats {
    margin: 15px 0;
  }
  
  .stat-item {
    margin-bottom: 15px;
  }
  
  .progress-value {
    font-size: 14px;
  }
  
  .progress-label {
    font-size: 11px;
  }
}
</style>  