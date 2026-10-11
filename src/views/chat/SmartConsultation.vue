<template>
  <main class="consult-page">
    <section class="consult-hero">
      <div class="hero-copy">
        <span class="eyebrow"><i class="el-icon-chat-line-round" /> 温暖陪伴</span>
        <h1>你好，我是小晴</h1>
        <p>从今天的用眼感受，到复查前的准备，我愿意陪你慢慢聊，也会帮你把重点整理清楚。</p>
        <div class="hero-prompts">
          <button v-for="prompt in heroPrompts" :key="prompt" type="button" @click="sendPreset(prompt)">{{ prompt }} <i class="el-icon-arrow-right" /></button>
        </div>
      </div>
      <div class="hero-portrait-wrap">
        <span class="portrait-halo halo-one" />
        <span class="portrait-halo halo-two" />
        <img :src="consultantImage" class="hero-portrait" alt="智能问诊助手小晴">
        <div class="portrait-note"><span class="presence-dot" /> 小晴正在这里陪你</div>
      </div>
    </section>

    <section class="consult-content">
      <article class="conversation-card">
        <header class="conversation-header">
          <div class="assistant-avatar"><img :src="consultantImage" alt=""></div>
          <div><h2>智能问诊</h2><p>把关心的事说给我听</p></div>
          <span class="online-state"><i /> 在线</span>
        </header>

        <div ref="messages" class="conversation-messages" role="log" aria-live="polite" aria-label="智能问诊对话">
          <article v-for="message in messages" :key="message.id" class="message-row" :class="message.role">
            <img v-if="message.role === 'assistant'" :src="consultantImage" class="message-avatar" alt="">
            <span v-else class="message-avatar user-avatar"><i class="el-icon-user" /></span>
            <div class="message-content">
              <span class="message-author">{{ message.role === 'assistant' ? '小晴' : '我' }}</span>
              <div class="message-bubble">{{ message.text }}</div>
            </div>
          </article>
          <article v-if="isThinking" class="message-row assistant thinking-row">
            <img :src="consultantImage" class="message-avatar" alt="">
            <div class="message-content"><span class="message-author">小晴</span><div class="message-bubble thinking-bubble"><i /><i /><i /></div></div>
          </article>
        </div>

        <div class="conversation-compose">
          <div class="quick-question-row">
            <button v-for="question in quickQuestions" :key="question" type="button" @click="sendPreset(question)">{{ question }}</button>
          </div>
          <form class="compose-form" @submit.prevent="send">
            <el-input v-model="input" type="textarea" :rows="2" resize="none" maxlength="300" placeholder="例如：给我一些日常建议" aria-label="输入你的问题" @keydown.enter.native.exact="handleEnter" />
            <el-button type="primary" native-type="submit" :disabled="!input.trim() || isThinking"><i class="el-icon-position" /><span>发送</span></el-button>
          </form>
        </div>
      </article>

      <aside class="consult-sidebar">
        <section class="care-card today-card">
          <span class="card-icon blue"><i class="el-icon-sunny" /></span>
          <h3>今天，先照顾好自己</h3>
          <p>规律用餐、适度活动、让眼睛在忙碌中也有放松的时间。</p>
        </section>
        <section class="care-card">
          <div class="side-heading"><h3>你可以这样问我</h3><i class="el-icon-question" /></div>
          <button v-for="question in sideQuestions" :key="question" type="button" class="side-question" @click="sendPreset(question)"><span>{{ question }}</span><i class="el-icon-arrow-right" /></button>
        </section>
        <section class="care-card reminder-card">
          <span class="card-icon mint"><i class="el-icon-time" /></span>
          <div><h3>复查前的小准备</h3><p>带好近期检查记录，把眼睛的变化和想问的问题写下来。</p></div>
          <router-link class="reminder-link" :to="{ path: '/followup/index', query: $route.query }">查看我的复查安排 <i class="el-icon-right" /></router-link>
        </section>
      </aside>
    </section>
  </main>
</template>

<script>
import consultantImage from '@/assets/smart-consultant.png'

export default {
  name: 'SmartConsultation',
  data() {
    return {
      consultantImage,
      input: '',
      isThinking: false,
      counter: 1,
      heroPrompts: ['给我一些日常建议', '我想安排下一次复查'],
      quickQuestions: ['今天怎么照顾眼睛？', '给我一些日常建议', '复查前要准备什么？'],
      sideQuestions: ['最近看屏幕容易累，怎么调节？', '饮食和作息可以怎么安排？', '检查结果出来后要关注什么？'],
      messages: [{ id: 0, role: 'assistant', text: '你好，我是小晴。今天想聊聊用眼、饮食、作息，还是复查安排？你慢慢说，我在。' }]
    }
  },
  methods: {
    handleEnter(event) {
      if (event.isComposing || event.keyCode === 229) return
      event.preventDefault()
      this.send()
    },
    scrollToLatest() {
      this.$nextTick(() => {
        if (this.$refs.messages) this.$refs.messages.scrollTop = this.$refs.messages.scrollHeight
      })
    },
    append(text, role) {
      this.messages.push({ id: this.counter++, role, text })
      this.scrollToLatest()
    },
    sendPreset(text) {
      if (this.isThinking) return
      this.append(text, 'user')
      this.reply(text)
    },
    send() {
      const text = this.input.trim()
      if (!text || this.isThinking) return
      this.append(text, 'user')
      this.input = ''
      this.reply(text)
    },
    reply(text) {
      this.isThinking = true
      this.scrollToLatest()
      window.setTimeout(() => {
        this.append(this.replyFor(text), 'assistant')
        this.isThinking = false
        this.scrollToLatest()
      }, 420)
    },
    replyFor(text) {
      if (/建议|康复|恢复|调养|日常|饮食|作息|运动|怎么做|用眼|照顾|屏幕|累/.test(text)) {
        return '当然可以。你可以先试试这个容易坚持的日常安排：\n\n1. 早晚花一分钟记录当天的用眼感受和血糖情况，复查时带给医生参考。\n2. 连续看屏幕约 20—30 分钟后，望向远处放松一会儿，刻意多眨几次眼。\n3. 三餐尽量规律，餐盘里多留出蔬菜、优质蛋白和适量主食；饮水分次进行。\n4. 在身体舒适、医生已认可的前提下，把散步、拉伸或轻松骑行安排进一周，循序增加。\n5. 保持稳定的睡眠时间，睡前让眼睛离开手机一会儿。\n\n如果出现突然明显的视物模糊、黑影遮挡、闪光增多或眼部疼痛，可以优先联系眼科医生。你想先从饮食、作息还是用眼习惯开始调整？'
      }
      if (/复查|检查|报告|结果|预约/.test(text)) {
        return '复查前可以准备三样东西：近期检查记录、这段时间的血糖或生活记录，以及你最想确认的两三个问题。\n\n到检查当天，记得把左右眼感受分别说清楚，例如是否有看远看近的变化、夜间视物感受、黑影或闪光等。检查完成后，我也可以陪你一起梳理报告里的重点和下一步安排。'
      }
      if (/模糊|黑影|闪光|视力|疼|看不清|飞蚊/.test(text)) {
        return '谢谢你告诉我这些感受。你可以先记下它从什么时候开始、是左眼还是右眼更明显、是否影响阅读或走路。带着这些细节和近期检查记录联系眼科，会让沟通更顺畅。\n\n如果变化来得很突然，或已经影响日常活动，可以把眼科咨询安排在更靠前的时间。'
      }
      return '我听到了。你可以再告诉我一点：这是最近刚出现的感受，还是已经持续了一段时间？它更影响阅读、看屏幕，还是夜间视物？\n\n我会帮你把重点整理成清楚的问题，方便你和医生沟通。'
    }
  }
}
</script>

<style scoped>
.consult-page{min-height:calc(100vh - var(--navbar-height));padding:32px 42px 48px;background:#F5F9FD;color:#233548}.consult-hero{position:relative;overflow:hidden;display:grid;grid-template-columns:minmax(0,1.08fr) minmax(340px,.92fr);min-height:292px;padding:42px 56px 34px;border-radius:24px;background:linear-gradient(105deg,#EAF5FF 0%,#F6FBFF 57%,#EAF4FC 100%);box-shadow:0 16px 38px rgba(64,119,160,.10)}.consult-hero::after{content:'';position:absolute;width:350px;height:350px;right:-125px;bottom:-210px;border-radius:50%;background:rgba(121,185,228,.16)}.hero-copy{position:relative;z-index:2;max-width:560px;align-self:center}.eyebrow{display:inline-flex;align-items:center;gap:7px;padding:7px 11px;color:#4381B7;border-radius:999px;background:rgba(255,255,255,.76);font-size:13px;font-weight:600;letter-spacing:.05em}.hero-copy h1{margin:17px 0 12px;color:#1D3F61;font-size:34px;letter-spacing:.03em}.hero-copy>p{margin:0;color:#5D758A;font-size:15px;line-height:1.95}.hero-prompts{display:flex;flex-wrap:wrap;gap:10px;margin-top:25px}.hero-prompts button{display:inline-flex;align-items:center;gap:10px;border:1px solid rgba(80,143,190,.22);border-radius:10px;padding:10px 13px;color:#3A76A7;background:rgba(255,255,255,.78);font-size:13px;cursor:pointer;transition:transform .2s ease,box-shadow .2s ease}.hero-prompts button:hover{transform:translateY(-2px);box-shadow:0 8px 18px rgba(60,126,173,.13)}.hero-portrait-wrap{position:relative;z-index:1;min-height:240px}.hero-portrait{position:absolute;z-index:2;right:0;bottom:-34px;width:min(365px,100%);height:325px;object-fit:cover;object-position:65% 34%;border-radius:0 0 22px 22px;filter:saturate(.95)}.portrait-halo{position:absolute;border-radius:50%;border:1px solid rgba(100,166,213,.22)}.halo-one{width:260px;height:260px;right:45px;bottom:-12px}.halo-two{width:334px;height:334px;right:9px;bottom:-56px}.portrait-note{position:absolute;z-index:3;right:238px;bottom:36px;white-space:nowrap;padding:9px 12px;border-radius:10px;color:#53708A;background:rgba(255,255,255,.92);box-shadow:0 10px 22px rgba(51,96,129,.10);font-size:12px}.presence-dot{display:inline-block;width:7px;height:7px;margin-right:6px;border-radius:50%;background:#5EBD96;box-shadow:0 0 0 3px rgba(94,189,150,.14)}.consult-content{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(270px,.72fr);gap:22px;margin-top:24px;align-items:start}.conversation-card,.care-card{border:1px solid #E6EFF7;border-radius:18px;background:#FFF;box-shadow:0 10px 28px rgba(50,105,148,.06)}.conversation-header{display:flex;align-items:center;gap:12px;padding:18px 22px;border-bottom:1px solid #ECF2F7}.assistant-avatar{overflow:hidden;width:42px;height:42px;border:2px solid #DCEEFF;border-radius:50%}.assistant-avatar img,.message-avatar:not(.user-avatar){width:100%;height:100%;object-fit:cover;object-position:65% 26%}.conversation-header h2{margin:0;color:#24425E;font-size:16px}.conversation-header p{margin:4px 0 0;color:#8295A8;font-size:12px}.online-state{display:inline-flex;align-items:center;gap:6px;margin-left:auto;color:#5B9A7E;font-size:12px}.online-state i{width:7px;height:7px;border-radius:50%;background:#62BE97}.conversation-messages{height:min(52vh,510px);min-height:390px;overflow-y:auto;padding:26px 25px 10px;background:linear-gradient(180deg,#FBFDFF 0%,#F6FAFD 100%)}.message-row{display:flex;align-items:flex-start;gap:10px;margin-bottom:21px}.message-avatar{display:grid;place-items:center;flex:0 0 32px;width:32px;height:32px;overflow:hidden;border-radius:50%;background:#E4F2FF;color:#4C88B8;font-size:17px}.message-content{max-width:min(78%,600px)}.message-author{display:block;margin:0 0 6px 2px;color:#8294A7;font-size:11px}.message-bubble{white-space:pre-wrap;padding:13px 15px;border:1px solid #E4EDF5;border-radius:4px 14px 14px 14px;color:#3A5065;background:#FFF;font-size:14px;line-height:1.8;box-shadow:0 4px 12px rgba(48,105,148,.04)}.message-row.user{flex-direction:row-reverse}.message-row.user .message-author{text-align:right;margin-right:2px}.message-row.user .message-bubble{border-color:#D7EAFB;border-radius:14px 4px 14px 14px;color:#2D648F;background:#EAF6FF}.user-avatar{background:#D9E9F7;color:#3978A8}.thinking-bubble{display:flex;align-items:center;gap:5px;min-width:56px;padding-top:16px;padding-bottom:16px}.thinking-bubble i{width:5px;height:5px;border-radius:50%;background:#7FA7C7;animation:typing 1.1s infinite ease-in-out}.thinking-bubble i:nth-child(2){animation-delay:.15s}.thinking-bubble i:nth-child(3){animation-delay:.3s}@keyframes typing{0%,80%,100%{transform:translateY(0);opacity:.35}40%{transform:translateY(-4px);opacity:1}}.conversation-compose{padding:15px 18px 18px;border-top:1px solid #ECF2F7;background:#FFF;border-radius:0 0 18px 18px}.quick-question-row{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}.quick-question-row button{border:1px solid #DCEAF6;border-radius:999px;padding:6px 10px;color:#5983A4;background:#F8FCFF;font-size:12px;cursor:pointer}.quick-question-row button:hover{color:#3173A6;background:#EAF6FF}.compose-form{display:flex;align-items:flex-end;gap:10px}.compose-form ::v-deep .el-textarea__inner{border-color:#DCE8F2;border-radius:12px;background:#FBFDFF;line-height:1.6}.compose-form ::v-deep .el-textarea__inner:focus{border-color:#80B5DE;box-shadow:0 0 0 3px rgba(112,174,218,.12)}.compose-form .el-button{height:42px;border:0;border-radius:10px;padding:0 17px;background:#4C8FC3;box-shadow:0 7px 14px rgba(58,132,182,.18)}.compose-form .el-button:hover{background:#397CAF}.compose-form .el-button span{margin-left:6px}.consult-sidebar{display:grid;gap:18px}.care-card{padding:21px}.today-card{min-height:154px;border:0;background:linear-gradient(145deg,#EAF6FF,#F4FBFF)}.card-icon{display:grid;place-items:center;width:38px;height:38px;margin-bottom:12px;border-radius:12px;font-size:19px}.card-icon.blue{color:#4C8FC3;background:#D7ECFC}.card-icon.mint{color:#458B80;background:#DDF3EE}.care-card h3{margin:0 0 8px;color:#36526B;font-size:15px}.care-card p{margin:0;color:#70879B;font-size:13px;line-height:1.8}.side-heading{display:flex;align-items:center;justify-content:space-between;color:#87A5BC}.side-heading h3{margin:0}.side-heading i{font-size:18px}.side-question{display:flex;width:100%;align-items:center;justify-content:space-between;gap:10px;padding:14px 0;border:0;border-bottom:1px solid #EDF2F6;color:#526D84;background:transparent;text-align:left;font-size:13px;line-height:1.55;cursor:pointer}.side-question:last-child{border-bottom:0}.side-question:hover{color:#3C7FAF}.side-question i{color:#9AB2C6;font-size:12px}.reminder-card{display:grid;grid-template-columns:auto 1fr;column-gap:13px}.reminder-card .card-icon{margin:0}.reminder-card h3{margin-top:2px}.reminder-link{grid-column:1/-1;margin-top:17px;color:#3A7CAA;font-size:12px;font-weight:600}.reminder-link:hover{color:#286994}@media (max-width:1100px){.consult-page{padding:26px}.consult-hero{grid-template-columns:1fr 310px;padding-left:38px}.consult-content{grid-template-columns:1fr}.consult-sidebar{grid-template-columns:repeat(3,1fr)}.hero-portrait{width:310px}.portrait-note{right:178px}}@media (max-width:760px){.consult-page{padding:16px}.consult-hero{display:block;min-height:0;padding:30px 24px 0}.hero-copy h1{font-size:28px}.hero-portrait-wrap{height:238px}.hero-portrait{right:50%;width:278px;height:255px;transform:translateX(50%)}.portrait-note{right:50%;bottom:17px;transform:translateX(50%)}.halo-one{right:50%;transform:translateX(50%)}.halo-two{display:none}.consult-content{margin-top:16px}.conversation-messages{min-height:350px;height:430px;padding:20px 16px 8px}.message-content{max-width:calc(100% - 42px)}.conversation-compose{padding:13px}.compose-form .el-button{padding:0 12px}.compose-form .el-button span{display:none}.consult-sidebar{grid-template-columns:1fr}.today-card{min-height:auto}}
</style>
