<template>
  <div class="consult-container">
    <!-- 左侧图片区 -->
    <div class="consult-left">
      <div class="doctor-area">
        <img class="doctor-image" src="@/assets/professor.png" alt="智能问诊" />

        <!-- 动态气泡 -->
        <div class="speech-bubble">
          {{ bubbleText }}
        </div>

        <div class="mood-options" v-if="showOPtions">
          <el-button size="mini" @click="handleMood('good')">很好</el-button>
          <el-button size="mini" @click="handleMood('normal')">一般</el-button>
          <el-button size="mini" @click="handleMood('bad')">不太好</el-button>
        </div>
      </div>
    </div>

    <!-- 右侧对话区 -->
    <div class="consult-right">
      <div class="chat-header">
        <h2>粉红丝带关爱中心</h2>
        <span class="subtitle">您的专业智能健康顾问</span>
      </div>

      <div class="chat-box" ref="chatBox">
        <transition-group name="fade-slide" tag="div">
          <div v-for="(msg, index) in messages" :key="index" class="chat-line" :class="msg.role">
            <img v-if="msg.role === 'ai'" src="@/assets/assistant_avatar.png" class="avatar" alt="AI"/>
            <div class="bubble">
              <span v-if="msg.loading" class="loading-dots">
                <span>.</span><span>.</span><span>.</span>
              </span>
              <span v-else v-html="msg.text"></span>
            </div>
            <img v-if="msg.role === 'user'" src="@/assets/profileavatar.jpg" class="avatar" alt="User"/>
          </div>
        </transition-group>
      </div>
      <div class="function-buttons">
        <el-button class="fun1-btn" size="small" @click="handleConsultation">专家会诊</el-button>
      </div>

      <div class="input-bar">
        <input v-model="userInput" placeholder="请输入您的症状或问题..."
          @keyup.enter="sendMessage" class="chat-input"/>
        <el-button class="chat-sendbtn" @click="sendMessage">发送</el-button>
      </div>
    </div>

    <el-dialog title="专家列表" :visible.sync="showDoctorDialog" width="40%" class="doctor-dialog">
      <div class="doctor-list">
        <div v-for="doctor in doctorList" :key="doctor.id" class="doctor-card">
          <div class="doctor-info">
            <div class="avatar"></div>
            <div class="info">
              <span>{{ doctor.name }} {{ doctor.title }}</span>
              <span>所在医院：{{ doctor.hospital }}</span>
              <span>专业擅长：{{ doctor.specialty }}</span>
            </div>
            <el-button class="select-btn" size="mini" @click="selectDoctor(doctor)">选择</el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: "SmartConsult",
  data() {
    return {
      userInput: "",
      messages: [],
      bubbleText: "您好，今天您感觉如何？",
      loading: false,
      showOPtions: true,
      showDoctorDialog: false,
      // 固定问答
      fixedReplies: [
        { q: /你.*谁|who are you/i, a: "我是粉红丝带关爱中心的AI健康顾问，专注乳腺健康管理与风险分析。" },
        { q: /再见|bye|拜/i, a: "再见，祝您健康平安～" },
        { q: /帮我分析|分析一下/i, a: "请稍等，我来为您分析一下您的状况..." },
        { q: /乳腺|疼|痛/i, a: "若有乳腺不适，请定期体检并保持良好作息，必要时咨询医生哦～" },
        { q: /谢谢|感恩/i, a: "不客气，这是我应该做的！" },
        { q:/给出的两个治疗方案的优势是什么呀？可以推荐一个更适合我的吗？/i,
          a: `先给你说两个方案的核心好处，再告诉你推荐哪个：<br>
          方案一（保乳手术 + 内分泌治疗 + 中药/针灸）的优势：<br>
          ①创伤小，不用全切乳房，只切肿瘤和周围一点点正常组织，术后伤口恢复快，住院 3-5 天就能出院；<br>
          ②不用做化疗，副作用特别小，不会掉头发、恶心呕吐，对身体伤害小；<br>
          ③能保留乳房外形，后续生活质量更高，还能通过中药、针灸缓解潮热、失眠这些不舒服的症状。<br>
          方案二（全切手术 + 化疗 + 靶向治疗）的优势：<br>
          ①切除范围广，能把整个乳房和腋窝淋巴结都清理干净，从治疗角度看 “更彻底”，局部控制肿瘤的概率稍高；<br>
          ②有靶向药辅助，能针对性对付可能残留的微小肿瘤细胞，降低复发风险。<br>
          综合下来，更推荐你选方案一！因为你是早期 Luminal A 型乳腺癌，肿瘤比较 “温和”，对内分泌治疗特别敏感，不用化疗也能达到很好的效果。方案一的适用性评分更高（4.5/5），而且创伤小、恢复快，还能保留乳房，既不影响治疗效果，又能让你后续生活更舒心 —— 这是结合你的年龄、肿瘤亚型、激素敏感性专门选的，对你来说是 “效果好 + 少受罪” 的最优解。`,
        },
        { q:/按照推荐方案治疗结束后，复发的概率高吗？我该怎么预防复发？/i,
          a:`先给你吃颗定心丸：按方案一治疗，复发概率很低！根据你的病情，治疗后 5 年不复发的概率能达到 85% 以上，局部控制肿瘤的概率更是 95% 以上，大部分和你情况一样的患者都能长期健康生活。<br>
          预防复发的关键特别简单，跟着做就行：<br>
          ①按时吃内分泌药（他莫昔芬），坚持吃 5 年 —— 这是最核心的 “防复发药”，能从根源上抑制肿瘤再长，千万别随便停；<br>
          ②严格按医生说的复查：术后 1-2 年每 3 个月查一次，3-5 年每 6 个月查一次，5 年后每年查一次，早发现早处理，心里更踏实；<br>
          ③跟着方案里的饮食、生活建议来：多吃山药、莲子、大枣这些养身体的食物，少吃辛辣、生冷的；术后 1 个月开始慢慢散步，每天走 30 分钟，别偷懒；<br>
          ④保持好心态，别瞎琢磨 —— 焦虑也会影响身体，平时多和家人朋友聊聊，不舒服就找医生或心理咨询，心情好也是 “抗癌神器”。<br>坚持做到这些，复发的概率会降到最低，你会越来越健康的！`
        }
      ],
      doctorList: [
        { id:'01', name: "张医生", title:'主任医师', hospital: "北京协和医院", specialty: "乳腺疾病，肿瘤诊断" },
        { id:'02', name: "李医生", title:'副主任医师', hospital: "上海瑞金医院", specialty:"乳腺癌术后康复" },
        { id:'03', name: "王医生", title:'主治医师', hospital: "广州中山大学附属肿瘤医院", specialty:"影像分析与AI辅助诊断"},
      ],
    };
  },
  mounted() {
    this.messages.push({
      role: "ai",
      text: "你好呀～我是粉红丝带关爱中心的智能健康顾问。\n很高兴为您服务！",
    });
  },
  methods: {
    handleMood(mood) {
      this.showOPtions = false;
      if (mood === 'good') {
        this.bubbleText = "真棒！保持积极的心态对恢复很有帮助哦！";
      } else if (mood === 'normal') {
        this.bubbleText = "那今天您记得要多休息，避免劳累！";
      } else if (mood === 'bad') {
        this.bubbleText = "辛苦啦，要不要我帮您分析一下可能的原因？";
      }
    },

    async sendMessage() {
      const query = this.userInput.trim();
      if (!query || this.loading) return;

      this.messages.push({ role: "user", text: query });
      this.userInput = "";

      const loadingMsg = { role: "ai", text: "", loading: true };
      this.messages.push(loadingMsg);
      this.scrollToBottom();
      this.loading = true;

      // 模拟思考
      await new Promise(r => setTimeout(r, 500));

      // 固定问答逻辑
      const match = this.fixedReplies.find(r => r.q.test(query));
      const reply = match
        ? match.a
        : "抱歉，我还在学习中，暂时无法回答这个问题～";

      loadingMsg.loading = false;
      loadingMsg.text = reply;
      this.loading = false;

      this.$nextTick(() => this.scrollToBottom());
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.chatBox;
        if (el) el.scrollTop = el.scrollHeight;
      });
    },
    handleConsultation() {
      this.messages.push({
        role:'user',
        text:'我想申请专家会诊，请帮我推荐合适的专家。'
      })
      setTimeout(() => {
      }, 2500);
      this.messages.push({
        role:'ai',
        text:'正在为您匹配最合适的专家，请稍后......'
      })
      this.loading = true;
      setTimeout(() => {
        this.loading = false;
        this.showDoctorDialog = true
      }, 1500)
    },
    selectDoctor(doctor) {
      this.showDoctorDialog = false;
      this.messages.push({
        role:'user',
        text:`我选择了${doctor.name}，请帮我安排会诊。`
      })
      this.messages.push({
        role:'ai',
        text:`匹配成功！已将您的信息发送至${doctor.name}，请您耐心等待结果。祝您早日康复！`
      })
    }
  },
};
</script>

<style>
.consult-container {
  display: flex;
  height: 88vh;
  width: 100%;
  margin: 0 auto;
  background: #f8fbfd;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.06);
}

/* 左侧区域 */
.consult-left {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.doctor-area {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.doctor-image {
  max-height: 80%;
  width: auto;
  object-fit: contain;
  border-radius: 0;
  box-shadow: none;
  z-index: 2;
}

/* 动态气泡 */
.speech-bubble {
  position: absolute;
  top: 95px;
  left: 24px;
  background: #ffffff;
  color: #333;
  font-size: 14px;
  padding: 10px 20px;
  border-radius: 18px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  animation: floatIn 1s ease-out, pulse 3s ease-in-out infinite;
  white-space: nowrap;
}
.speech-bubble::after {
  content: "";
  position: absolute;
  left: 130px;
  bottom: -6px;
  width: 0;
  height: 0;
  border-top: 6px solid #ffffff;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
}

.mood-options {
  position: absolute;
  top: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
}
.mood-options .el-button {
  background: #ffffff;
  color: #333;
  border: 1px solid #d0e5f7;
  border-radius: 20px;
  transition: all 0.2s ease;
}
.mood-options .el-button:hover {
  background: #d8f1ff;
  color: #1b3a57;
}

.consult-right {
  flex: 2.2;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.chat-header {
  padding: 16px 30px 10px;
  background: linear-gradient(to right, #faf0f0, #fce3e3);
  border-bottom: 1px solid #e2eef4;
}
.chat-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1b3a57;
}
.subtitle {
  font-size: 13px;
  color: #6d7b87;
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 25px 35px;
  background: #fdfdfd;
}
.chat-line {
  display: flex;
  width: 100%;
  margin: 12px 0;
}

.chat-line.ai {
  justify-content: flex-start;
}
.chat-line.user {
  justify-content: flex-end;
}

.chat-line .bubble {
  display: inline-block;
  padding: 12px 16px;
  border-radius: 18px;
  max-width: 70%;
  line-height: 1.6;
  word-break: break-word;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}
.chat-line.ai .bubble {
  align-self: flex-start;
  background: #fff;
}
.chat-line.user .bubble {
  align-self: flex-end;
  background: #faf0f0;
}
.chat-line .avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin: 0 8px;
  flex-shrink: 0;
  border: 2px solid #fce3e3;
}
.input-bar {
  display: flex;
  padding: 15px 25px;
  border-top: 1px solid #e0e6eb;
  background: #fff;
}
.chat-input {
  flex: 1;
  margin-right: 10px;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s ease;
}
.chat-input:focus {
  border-color: #f5b1b6;
  outline: none;
  box-shadow: 0 0 0 2px rgba(255, 143, 163, 0.2);
}
.chat-sendbtn {
  background-color: #faf0f0;
  border-color: #fff;
  color: #333;
  border-radius: 6px;
  transition: 0.2s;
}
.chat-sendbtn:hover {
  background-color: #fce3e3;
}

.function-buttons {
  display: flex;
  margin-top: 10px;
}

.fun1-btn {
  margin-left: 25px;
  margin-bottom: 10px;
  gap: 10px;
  background-color: #f5adb8 !important;
  color: #fff !important;
  border: none !important;
}

.fun1-btn:hover {
  background-color: #f08999 !important;
  color: #fff !important;
  border: none !important;
}
.fun1-btn:active {
  background-color: #f08999 !important;
  color: #fff !important;
  border: none !important;
}

/* 弹窗样式 */
.doctor-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fffafc;
  border: 1px solid #f7dce3;
  border-radius: 12px;
  padding: 14px 18px;
  margin-bottom: 14px;
  transition: box-shadow 0.3s ease;
}

.doctor-info:hover {
  box-shadow: 0 2px 8px rgba(245, 173, 184, 0.3);
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #ffeef2;
  color: #f28ca0;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.info span:first-child {
  font-weight: 600;
  color: #c65b7d;
}

.select-btn {
  background-color: #f5adb8;
  color: #fff;
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.select-btn:hover {
  background-color: #f08999;
  color: #fff;
}

@keyframes floatIn {
  0% {
    opacity: 0;
    transform: translateY(-15px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
@keyframes pulse {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}
</style>

