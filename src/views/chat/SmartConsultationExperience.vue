<template>
  <main class="smart-page">
    <section class="smart-layout">
      <aside class="guide-panel">
        <div class="guide-top"><span class="presence-dot" /> 小晴 · 健康陪伴助手</div>
        <div class="guide-portrait">
          <span class="portrait-light light-one" />
          <span class="portrait-light light-two" />
          <img :src="fullBodyImage" alt="智能问诊助手小晴">
        </div>
        <div class="guide-copy">
          <h2>你好，今天感觉怎么样？</h2>
          <p>你可以和我聊聊眼睛的感受，也可以直接开始预约。</p>
        </div>
        <div class="guide-chips"><button v-for="item in guideQuestions" :key="item" type="button" @click="sendPreset(item)">{{ item }}</button></div>
      </aside>

      <section class="conversation-card">
        <header class="conversation-header">
          <div class="assistant-avatar"><img :src="avatarImage" alt=""></div>
          <div class="assistant-intro"><h2>和小晴聊聊</h2><p>{{ patientBrief }}</p></div>
          <el-popover v-model="casePickerVisible" placement="bottom-start" :width="330" trigger="click" popper-class="case-picker-popper">
            <div class="case-picker">
              <div class="case-picker-heading"><span>患者病例档案</span><small>选择后，小晴会结合记录与你沟通</small></div>
              <button v-for="patient in patientRecords" :key="patient.id" type="button" :class="['case-option', { selected: patient.id === activePatient.id }]" @click="selectCase(patient)">
                <span class="case-option-name"><strong>{{ patient.name }}</strong><small>{{ patient.sex }} · {{ patient.age }} 岁 · {{ patient.id }}</small></span>
                <span>{{ patient.date }} · {{ patient.status }}</span>
                <i v-if="patient.id === activePatient.id" class="el-icon-check" />
              </button>
            </div>
            <button slot="reference" type="button" class="case-trigger" :aria-expanded="String(casePickerVisible)">
              <span class="case-trigger-label">病例档案</span>
              <strong>{{ activePatient.name }}<i class="el-icon-arrow-down" /></strong>
            </button>
          </el-popover>
          <div class="conversation-actions">
            <button type="button" @click="openAppointment"><i class="el-icon-date" /> 预约</button>
            <button type="button" @click="sendPreset('复查前要准备什么？')"><i class="el-icon-notebook-2" /> 复查</button>
            <button type="button" @click="sendPreset('给我一些日常建议')"><i class="el-icon-sunny" /> 建议</button>
          </div>
        </header>
        <div ref="messages" class="conversation-messages" role="log" aria-live="polite" aria-label="智能问诊对话">
          <article v-for="message in messages" :key="message.id" class="message-row" :class="message.role">
            <img v-if="message.role === 'assistant'" :src="avatarImage" class="message-avatar" alt="">
            <span v-else class="message-avatar user-avatar"><i class="el-icon-user" /></span>
            <div class="message-content"><span class="message-author">{{ message.role === 'assistant' ? '小晴' : '我' }}</span><div class="message-bubble">{{ message.text }}</div></div>
          </article>
          <article v-if="isThinking" class="message-row">
            <img :src="avatarImage" class="message-avatar" alt="">
            <div class="message-content"><span class="message-author">小晴</span><div class="message-bubble thinking-bubble"><i /><i /><i /></div></div>
          </article>
        </div>
        <div class="conversation-compose">
          <div class="quick-question-row"><button v-for="question in quickQuestions" :key="question" type="button" @click="sendPreset(question)">{{ question }}</button></div>
          <form class="compose-form" @submit.prevent="send">
            <el-input v-model="input" type="textarea" :rows="2" resize="none" maxlength="300" placeholder="例如：最近看屏幕容易累，给我一些建议" aria-label="输入你的问题" @keydown.enter.native.exact="handleEnter" />
            <el-button type="primary" native-type="submit" :disabled="!input.trim() || isThinking"><i class="el-icon-position" /><span>发送</span></el-button>
          </form>
        </div>
      </section>

    </section>

    <el-dialog :visible.sync="appointmentVisible" custom-class="appointment-dialog" width="680px" :close-on-click-modal="false">
      <div slot="title" class="dialog-title"><span class="dialog-title-icon"><i class="el-icon-date" /></span><div><h2>预约医生</h2><p>选择你希望沟通的方向和方便的时间</p></div></div>
      <div class="booking-section"><h3>选择医生</h3><div class="doctor-list"><button v-for="doctor in doctors" :key="doctor.id" type="button" :class="['doctor-option', { selected: selectedDoctorId === doctor.id }]" @click="selectedDoctorId = doctor.id"><span class="doctor-avatar" :class="doctor.tone">{{ doctor.name.slice(0, 1) }}</span><span><strong>{{ doctor.name }}</strong><small>{{ doctor.department }}</small><em>{{ doctor.focus }}</em></span><i v-if="selectedDoctorId === doctor.id" class="el-icon-check" /></button></div></div>
      <div class="booking-section"><h3>选择时段</h3><div class="slot-list"><button v-for="slot in slots" :key="slot" type="button" :class="{ selected: selectedSlot === slot }" @click="selectedSlot = slot">{{ slot }}</button></div></div>
      <div v-if="selectedDoctor && selectedSlot" class="booking-summary"><i class="el-icon-circle-check" /><span>已选择 {{ selectedDoctor.name }} · {{ selectedSlot }}</span></div>
      <div slot="footer" class="dialog-footer"><el-button @click="appointmentVisible = false">稍后再说</el-button><el-button type="primary" :disabled="!selectedDoctor || !selectedSlot" @click="confirmAppointment">确认预约</el-button></div>
    </el-dialog>
  </main>
</template>

<script>
import fullBodyImage from '@/assets/smart-consultant-fullbody.png'
import avatarImage from '@/assets/smart-consultant.png'
import { patients, demoState, selectPatient, contextQuery } from '@/data/retina-demo'

export default {
  name: 'SmartConsultationExperience',
  data() {
    return {
      fullBodyImage,
      avatarImage,
      input: '',
      isThinking: false,
      appointmentVisible: false,
      casePickerVisible: false,
      selectedDoctorId: 'chen',
      selectedSlot: '明天 09:30',
      appointment: null,
      counter: 1,
      patientRecords: patients,
      guideQuestions: ['我想预约医生', '给我一些日常建议', '复查前要准备什么？'],
      quickQuestions: ['今天怎么照顾眼睛？', '饮食和作息怎么安排？', '检查结果出来后要关注什么？', '我想预约医生'],
      doctors: [
        { id: 'chen', name: '陈医生', department: '眼底专科', focus: '复查与影像解读', tone: 'blue' },
        { id: 'zhou', name: '周医生', department: '眼健康管理', focus: '生活管理与随访', tone: 'mint' },
        { id: 'xu', name: '许医生', department: '内分泌咨询', focus: '血糖与生活安排', tone: 'violet' }
      ],
      slots: ['今天 15:30', '明天 09:30', '明天 14:00', '周六 10:00'],
      messages: [{ id: 0, role: 'assistant', text: '你好，我是小晴。最近用眼还舒服吗？无论是日常安排、复查准备，还是想预约医生，都可以告诉我。' }]
    }
  },
  computed: {
    selectedDoctor() { return this.doctors.find(doctor => doctor.id === this.selectedDoctorId) },
    activePatient() { return demoState.patient },
    patientBrief() {
      const patient = this.activePatient
      return patient.duration ? '已关联 ' + patient.name + ' 的健康档案 · 病程 ' + patient.duration + ' 年' : '已关联 ' + patient.name + ' 的健康档案'
    }
  },
  methods: {
    handleEnter(event) { if (event.isComposing || event.keyCode === 229) return; event.preventDefault(); this.send() },
    scrollToLatest() { this.$nextTick(() => { if (this.$refs.messages) this.$refs.messages.scrollTop = this.$refs.messages.scrollHeight }) },
    append(text, role) { this.messages.push({ id: this.counter++, role, text }); this.scrollToLatest() },
    selectCase(patient) {
      if (patient.id === this.activePatient.id) { this.casePickerVisible = false; return }
      selectPatient(patient)
      this.casePickerVisible = false
      this.messages = [{ id: this.counter++, role: 'assistant', text: this.caseGreeting() }]
      this.$router.replace({ path: this.$route.path, query: contextQuery() })
      this.scrollToLatest()
    },
    caseGreeting() {
      const patient = this.activePatient
      const record = patient.cfp ? '近期已关联眼底检查记录' : '当前还没有眼底影像记录'
      const glucose = patient.hba1c ? 'HbA1c ' + patient.hba1c + '%' : '血糖记录待补充'
      return '好的，我已经打开 ' + patient.name + ' 的病例档案。这里记录了糖尿病病程约 ' + patient.duration + ' 年、' + glucose + '，' + record + '。你想先聊日常安排、复查准备，还是想预约医生？'
    },
    patientContext() {
      const patient = this.activePatient
      const glucose = patient.hba1c ? '最近 HbA1c 为 ' + patient.hba1c + '%' : '血糖记录还可以在下次就诊前补充'
      const imaging = patient.cfp ? '近期已有眼底检查资料' : '近期还没有眼底影像资料'
      return patient.name + '的档案里，糖尿病病程约 ' + patient.duration + ' 年，' + glucose + '，' + imaging + '。'
    },
    openAppointment() { this.appointmentVisible = true },
    confirmAppointment() {
      this.appointment = { doctor: this.selectedDoctor, slot: this.selectedSlot }
      this.appointmentVisible = false
      this.append('我想预约 ' + this.selectedDoctor.name + '，时间是 ' + this.selectedSlot, 'user')
      this.append('好的，已为你保留 ' + this.selectedDoctor.name + ' 的 ' + this.selectedSlot + ' 时段。就诊前可以带上近期检查记录，并写下最想确认的两三个问题，我们到时一起慢慢沟通。', 'assistant')
    },
    sendPreset(text) { if (this.isThinking) return; this.append(text, 'user'); if (/预约医生/.test(text)) { this.append('当然可以。我已经为你打开预约面板，选好医生和时段后就可以确认。', 'assistant'); this.openAppointment() } else this.reply(text) },
    send() { const text = this.input.trim(); if (!text || this.isThinking) return; this.append(text, 'user'); this.input = ''; this.reply(text) },
    reply(text) {
      this.isThinking = true
      this.scrollToLatest()
      window.setTimeout(() => { this.append(this.replyFor(text), 'assistant'); this.isThinking = false; this.scrollToLatest() }, 420)
    },
    replyFor(text) {
      if (/建议|康复|恢复|调养|日常|饮食|作息|运动|怎么做|用眼|照顾|屏幕|累/.test(text)) return this.patientContext() + '\n\n当然可以。你可以先试试这个容易坚持的日常安排：\n\n1. 早晚花一分钟记录当天的用眼感受和血糖情况，复查时带给医生参考。\n2. 连续看屏幕约 20—30 分钟后，望向远处放松一会儿，刻意多眨几次眼。\n3. 三餐尽量规律，餐盘里多留出蔬菜、优质蛋白和适量主食；饮水分次进行。\n4. 在身体舒适、医生已认可的前提下，把散步、拉伸或轻松骑行安排进一周，循序增加。\n5. 保持稳定的睡眠时间，睡前让眼睛离开手机一会儿。\n\n如果出现突然明显的视物模糊、黑影遮挡、闪光增多或眼部疼痛，可以优先联系眼科医生。你想先从饮食、作息还是用眼习惯开始调整？'
      if (/复查|检查|报告|结果|预约/.test(text)) return this.patientContext() + '\n\n复查前可以准备三样东西：近期检查记录、这段时间的血糖或生活记录，以及你最想确认的两三个问题。\n\n到检查当天，记得把左右眼感受分别说清楚，例如是否有看远看近的变化、夜间视物感受、黑影或闪光等。检查完成后，我也可以陪你一起梳理报告里的重点和下一步安排。'
      if (/模糊|黑影|闪光|视力|疼|看不清|飞蚊/.test(text)) return '谢谢你告诉我这些感受。你可以先记下它从什么时候开始、是左眼还是右眼更明显、是否影响阅读或走路。带着这些细节和近期检查记录联系眼科，会让沟通更顺畅。\n\n如果变化来得很突然，或已经影响日常活动，可以把眼科咨询安排在更靠前的时间。'
      return '我听到了。你可以再告诉我一点：这是最近刚出现的感受，还是已经持续了一段时间？它更影响阅读、看屏幕，还是夜间视物？\n\n我会帮你把重点整理成清楚的问题，方便你和医生沟通。'
    }
  }
}
</script>

<style scoped>
.smart-page{min-height:calc(100vh - var(--navbar-height));padding:30px 38px 44px;background:#f4f9fd;color:#2a4155}.smart-header{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;max-width:1560px;margin:0 auto 22px}.page-kicker{display:inline-flex;align-items:center;gap:7px;padding:6px 10px;border-radius:99px;color:#4b83b2;background:#e7f3ff;font-size:12px;font-weight:600}.smart-header h1{margin:10px 0 8px;color:#1e4264;font-size:31px;letter-spacing:.04em}.smart-header p{margin:0;color:#71889b;font-size:14px}.guide-chips button{border:0;cursor:pointer}.smart-layout{display:grid;grid-template-columns:270px minmax(430px,1fr);gap:20px;align-items:stretch;max-width:1320px;margin:0 auto}.guide-panel,.conversation-card{border:1px solid #e2edf6;border-radius:18px;background:#fff;box-shadow:0 10px 28px rgba(51,104,147,.06)}.guide-panel{position:relative;overflow:hidden;display:flex;flex-direction:column;min-height:645px;padding:18px 18px 16px;background:linear-gradient(175deg,#ecf7ff 0%,#fbfdff 60%,#f4faff 100%)}.guide-top{position:relative;z-index:2;color:#5c86a7;font-size:12px;font-weight:600}.presence-dot{display:inline-block;width:7px;height:7px;margin-right:6px;border-radius:50%;background:#65bf99;box-shadow:0 0 0 3px rgba(101,191,153,.14)}.guide-portrait{position:relative;z-index:1;flex:1;min-height:360px;margin:0 -20px -3px}.guide-portrait img{position:absolute;z-index:2;bottom:-26px;left:50%;width:285px;max-width:110%;height:100%;object-fit:contain;transform:translateX(-50%);filter:drop-shadow(0 15px 20px rgba(44,100,141,.19))}.portrait-light{position:absolute;left:50%;border-radius:50%;transform:translateX(-50%)}.light-one{bottom:44px;width:226px;height:226px;background:radial-gradient(circle,rgba(162,211,244,.48),rgba(162,211,244,0) 69%)}.light-two{bottom:18px;width:260px;height:55px;background:rgba(107,170,214,.12);filter:blur(12px)}.guide-copy{position:relative;z-index:3}.guide-copy h2{margin:0 0 8px;color:#315574;font-size:17px}.guide-copy p{margin:0;color:#728b9e;font-size:12px;line-height:1.8}.guide-chips{position:relative;z-index:3;display:flex;flex-wrap:wrap;gap:7px;margin-top:15px}.guide-chips button{padding:6px 9px;border:1px solid #d6e9f7;border-radius:99px;color:#4d80a7;background:rgba(255,255,255,.76);font-size:11px}.conversation-card{display:flex;flex-direction:column;min-height:645px;overflow:hidden}.conversation-header{display:flex;align-items:center;gap:12px;padding:17px 20px;border-bottom:1px solid #eaf1f6}.assistant-avatar{overflow:hidden;width:42px;height:42px;border:2px solid #daedfb;border-radius:50%}.assistant-avatar img,.message-avatar:not(.user-avatar){width:100%;height:100%;object-fit:cover;object-position:65% 24%}.conversation-header h2{margin:0;color:#27455f;font-size:16px}.conversation-header p{margin:4px 0 0;color:#91a1ae;font-size:12px}.conversation-actions{display:flex;gap:7px;margin-left:auto}.conversation-actions button{display:inline-flex;align-items:center;gap:5px;border:1px solid #dbeaf5;border-radius:8px;padding:7px 9px;color:#4d7e9f;background:#f8fcff;font-size:12px;cursor:pointer}.conversation-actions button:first-child{border-color:#b7d9ef;color:#337bad;background:#ecf7ff}.conversation-actions button:hover{border-color:#84b9dc;background:#edf8ff}.conversation-messages{flex:1;min-height:360px;overflow-y:auto;padding:25px 23px 5px;background:linear-gradient(180deg,#fbfdff 0%,#f6fafe 100%)}.message-row{display:flex;align-items:flex-start;gap:10px;margin-bottom:20px}.message-avatar{display:grid;place-items:center;flex:0 0 32px;width:32px;height:32px;overflow:hidden;border-radius:50%;background:#e4f2ff;color:#4c88b8;font-size:17px}.message-content{max-width:min(80%,600px)}.message-author{display:block;margin:0 0 6px 2px;color:#899baa;font-size:11px}.message-bubble{white-space:pre-wrap;padding:12px 14px;border:1px solid #e4edf5;border-radius:4px 14px 14px 14px;color:#3b5368;background:#fff;font-size:14px;line-height:1.82;box-shadow:0 4px 12px rgba(48,105,148,.04)}.message-row.user{flex-direction:row-reverse}.message-row.user .message-author{text-align:right;margin-right:2px}.message-row.user .message-bubble{border-color:#d7eafb;border-radius:14px 4px 14px 14px;color:#2d648f;background:#eaf6ff}.user-avatar{background:#d9e9f7;color:#3978a8}.thinking-bubble{display:flex;align-items:center;gap:5px;min-width:56px;padding-top:16px;padding-bottom:16px}.thinking-bubble i{width:5px;height:5px;border-radius:50%;background:#7fa7c7;animation:typing 1.1s infinite ease-in-out}.thinking-bubble i:nth-child(2){animation-delay:.15s}.thinking-bubble i:nth-child(3){animation-delay:.3s}@keyframes typing{0%,80%,100%{transform:translateY(0);opacity:.35}40%{transform:translateY(-4px);opacity:1}}.conversation-compose{padding:14px 17px 17px;border-top:1px solid #ecf2f7}.quick-question-row{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:12px}.quick-question-row button{border:1px solid #dceaf6;border-radius:99px;padding:6px 9px;color:#5a83a4;background:#f8fcff;font-size:11px;cursor:pointer}.compose-form{display:flex;align-items:flex-end;gap:10px}.compose-form ::v-deep .el-textarea__inner{border-color:#dce8f2;border-radius:12px;background:#fbfdff;line-height:1.6}.compose-form .el-button{height:42px;border:0;border-radius:10px;padding:0 17px;background:#4c8fc3;box-shadow:0 7px 14px rgba(58,132,182,.18)}.compose-form .el-button span{margin-left:6px}.dialog-title{display:flex;align-items:center;gap:12px}.dialog-title-icon{display:grid;place-items:center;width:42px;height:42px;border-radius:12px;color:#4c8fc3;background:#e3f2fe;font-size:20px}.dialog-title h2{margin:0;color:#37536d;font-size:18px}.dialog-title p{margin:4px 0 0;color:#8ba0b1;font-size:12px}.booking-section{margin:10px 0 23px}.booking-section h3{margin:0 0 12px;color:#526a7e;font-size:14px}.doctor-list{display:grid;gap:9px}.doctor-option{display:flex;align-items:center;gap:11px;width:100%;padding:12px;border:1px solid #e3ecf4;border-radius:12px;background:#fff;text-align:left;cursor:pointer}.doctor-option.selected{border-color:#83b8de;background:#f3faff;box-shadow:0 0 0 3px rgba(104,170,216,.1)}.doctor-avatar{display:grid;place-items:center;flex:0 0 38px;width:38px;height:38px;border-radius:50%;font-size:16px;font-weight:600}.doctor-avatar.blue{color:#3f82b3;background:#dceefc}.doctor-avatar.mint{color:#438d80;background:#dff3ed}.doctor-avatar.violet{color:#7b6aac;background:#eee9fb}.doctor-option>span:nth-child(2){flex:1}.doctor-option strong,.doctor-option small,.doctor-option em{display:block}.doctor-option strong{color:#456077;font-size:13px}.doctor-option small{margin-top:3px;color:#8299ab;font-size:11px}.doctor-option em{margin-top:4px;color:#5f91b6;font-size:11px;font-style:normal}.doctor-option>i{color:#4b94c6}.slot-list{display:grid;grid-template-columns:repeat(2,1fr);gap:9px}.slot-list button{padding:11px;border:1px solid #e1ebf3;border-radius:9px;color:#58738a;background:#fff;font-size:12px;cursor:pointer}.slot-list button.selected{border-color:#7db5df;color:#3478aa;background:#eff8ff}.booking-summary{display:flex;align-items:center;gap:8px;padding:11px 12px;border-radius:9px;color:#4b8876;background:#eef9f5;font-size:13px}.booking-summary i{font-size:17px}.dialog-footer{display:flex;justify-content:flex-end;gap:8px}@media(max-width:1050px){.smart-layout{grid-template-columns:230px minmax(0,1fr)}.smart-page{padding:26px}.guide-portrait img{width:260px}.guide-panel,.conversation-card{min-height:620px}}@media(max-width:760px){.smart-page{padding:18px 15px 32px}.smart-layout{display:flex;flex-direction:column}.guide-panel{min-height:430px}.guide-portrait{min-height:275px}.guide-portrait img{width:220px}.conversation-card{min-height:570px}.conversation-messages{min-height:310px}.message-content{max-width:calc(100% - 42px)}.conversation-actions{gap:4px}.conversation-actions button{padding:6px 7px;font-size:11px}.compose-form .el-button{padding:0 11px}.compose-form .el-button span{display:none}.slot-list{grid-template-columns:1fr}.appointment-dialog{width:calc(100% - 28px)!important}}
/* Keep the desktop consultation experience as one continuous workspace instead of a row of floating cards. */
.smart-page {
  min-height: calc(100vh - var(--navbar-height));
  padding: 0;
  background: #f5f9fd;
}

.smart-header {
  max-width: none;
  margin: 0;
  padding: 22px 34px 16px;
  background: #fff;
  border-bottom: 1px solid #e7eff5;
}

.smart-layout {
  grid-template-columns: 286px minmax(0, 1fr);
  gap: 0;
  max-width: none;
  min-height: calc(100vh - var(--navbar-height));
  margin: 0;
  background: #fff;
}

.guide-panel,
.conversation-card {
  border: 0;
  border-radius: 0;
  box-shadow: none;
}

.guide-panel {
  padding: 22px 24px 18px;
  border-right: 1px solid #e1ebf3;
}

.conversation-header {
  padding-right: 24px;
  padding-left: 24px;
}

@media (max-width: 1050px) {
  .smart-header { padding: 20px 26px 15px; }
  .smart-layout { grid-template-columns: 242px minmax(0, 1fr); }
  .smart-page { padding: 0; }
}

@media (max-width: 760px) {
  .smart-page { padding: 0; }
  .smart-header { padding: 18px 16px 14px; }
  .smart-header h1 { font-size: 26px; }
  .guide-panel { border-right: 0; border-bottom: 1px solid #e1ebf3; }
  .conversation-messages { padding-right: 16px; padding-left: 16px; }
}
</style>

<style>
.case-trigger {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 156px;
  margin: 0 2px 0 12px;
  padding: 4px 8px 4px 16px;
  border: 0;
  border-left: 1px solid #e5eef5;
  color: #496e8c;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.case-trigger:hover { background: #f6fbff; border-radius: 8px; }
.case-trigger:hover strong { color: #2e7eb8; }
.case-trigger-label { color: #93a8b8; font-size: 11px; line-height: 1.2; }
.case-trigger strong { display: flex; align-items: center; gap: 6px; margin-top: 3px; color: #416783; font-size: 13px; font-weight: 600; transition: color .2s ease; }
.case-trigger strong i { font-size: 11px; }
.assistant-intro { min-width: 0; padding-right: 2px; }
.assistant-intro h2 { letter-spacing: .025em; }
.assistant-intro p { overflow: hidden; max-width: 330px; white-space: nowrap; text-overflow: ellipsis; }

.case-picker-popper { padding: 0 !important; overflow: hidden; border: 1px solid #dbe9f3 !important; border-radius: 12px !important; box-shadow: 0 12px 30px rgba(51, 98, 134, .14) !important; }
.case-picker-heading { padding: 14px 16px 11px; border-bottom: 1px solid #edf3f7; background: #f8fcff; }
.case-picker-heading span, .case-picker-heading small { display: block; }
.case-picker-heading span { color: #365b78; font-size: 14px; font-weight: 650; }
.case-picker-heading small { margin-top: 4px; color: #8098aa; font-size: 11px; }
.case-option { position: relative; display: grid; grid-template-columns: 1fr auto; gap: 2px 12px; width: 100%; padding: 12px 16px; border: 0; border-bottom: 1px solid #f0f4f7; background: #fff; color: #6f899d; text-align: left; cursor: pointer; }
.case-option:last-child { border-bottom: 0; }
.case-option:hover, .case-option.selected { background: #f1f9ff; }
.case-option.selected { box-shadow: inset 3px 0 0 #5aa1d1; }
.case-option-name strong, .case-option-name small { display: block; }
.case-option-name strong { color: #3e627d; font-size: 13px; }
.case-option-name small, .case-option > span:nth-child(2) { color: #8aa0b0; font-size: 11px; line-height: 1.5; }
.case-option > span:nth-child(2) { grid-column: 1; }
.case-option > i { position: absolute; top: 50%; right: 16px; transform: translateY(-50%); color: #3987bb; }

.guide-top { font-size: 13px; }
.guide-copy h2 { font-size: 18px; }
.guide-copy p { font-size: 13px; }
.guide-chips button, .quick-question-row button { font-size: 12px; }
.conversation-header h2 { font-size: 17px; }
.conversation-header p { font-size: 13px; }
.conversation-actions button { font-size: 13px; }
.message-author { font-size: 12px; }
.message-bubble { font-size: 15px; }
.case-trigger-label { font-size: 13px; }
.case-trigger strong { font-size: 15px; }
.case-picker-heading span { font-size: 16px; }
.case-picker-heading small, .case-option-name small, .case-option > span:nth-child(2) { font-size: 13px; }
.case-option-name strong { font-size: 15px; }

.guide-top { font-size: 14px; }
.guide-copy h2 { font-size: 20px; }
.guide-copy p { font-size: 15px; }
.guide-chips button, .quick-question-row button { font-size: 13px; }
.conversation-header h2 { font-size: 18px; }
.conversation-header p { font-size: 14px; }
.conversation-actions button { font-size: 14px; }
.message-author { font-size: 13px; }
.message-bubble { font-size: 16px; }
.dialog-title p { font-size: 14px; }
.booking-section h3 { font-size: 16px; }
.doctor-option strong { font-size: 15px; }
.doctor-option small, .doctor-option em { font-size: 14px; }
.slot-list button { font-size: 14px; }
.booking-summary { font-size: 15px; }

@media (max-width: 760px) {
  .case-trigger { min-width: 116px; padding-right: 5px; padding-left: 7px; }
  .case-trigger-label { display: none; }
  .case-trigger strong { margin-top: 0; font-size: 12px; }
}
</style>
