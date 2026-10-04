<template>
  <main class="clinical-page assistant-page">
    <clinical-header title="眼健康助手" description="了解采集、共识评估与随访流程，整理准备向医生确认的问题。">
      <span class="status-pill primary"><i class="el-icon-chat-dot-round" />流程问答演示</span>
    </clinical-header>
    <demo-notice text="当前使用本地预置流程问答，未连接在线大模型或医生咨询服务；对话只在本次会话内保留。" />
    <div class="assistant-layout">
      <section class="panel conversation-panel">
        <div class="conversation-heading"><span class="assistant-mark"><i class="el-icon-view" /></span><div><h2>眼健康助手</h2><p>为筛查流程提供清晰的解释</p></div><span class="status-pill">预置问答</span></div>
        <div ref="messages" class="conversation-messages" role="log" aria-live="polite" aria-label="对话记录">
          <article v-for="message in messages" :key="message.id" class="message-row" :class="message.role">
            <span class="message-avatar"><i :class="message.role === 'user' ? 'el-icon-user' : 'el-icon-view'" aria-hidden="true" /></span>
            <div class="message-content"><span class="message-author">{{ message.role === 'user' ? '你' : '眼健康助手 · 演示' }}</span><div class="message-bubble">{{ message.text }}</div></div>
          </article>
        </div>
        <div class="conversation-compose">
          <div class="quick-question-row"><button v-for="question in questions.slice(0, 3)" :key="question.title" type="button" @click="sendQuestion(question)">{{ question.title }}</button></div>
          <form class="compose-form" @submit.prevent="send">
            <el-input v-model="input" label="输入流程问题" type="textarea" :rows="2" resize="none" maxlength="500" placeholder="输入流程问题，Enter 发送，Shift + Enter 换行" aria-label="输入流程问题" @keydown.enter.native.exact="handleEnter" />
            <el-button type="primary" native-type="submit" :disabled="!input.trim()" aria-label="发送消息"><i class="el-icon-position" /><span>发送</span></el-button>
          </form>
          <p>演示问答不会读取影像或生成诊断；可向医生确认的事项可记录到随访准备清单。</p>
        </div>
      </section>
      <div>
        <section class="panel">
          <div class="panel-heading"><h2>你可能想了解</h2><i class="el-icon-question muted" /></div>
          <div class="question-list"><button v-for="question in questions" :key="question.title" type="button" @click="sendQuestion(question)"><span>{{ question.title }}</span><i class="el-icon-arrow-right" /></button></div>
        </section>
        <section class="panel section-gap assistant-next">
          <span class="assistant-note-icon"><i class="el-icon-edit-outline" /></span>
          <h3>把问题带到下一次复核</h3>
          <p>整理检查资料、记录症状变化，或保存需要医生确认的报告问题。</p>
          <router-link class="text-link" to="/followup/index">打开准备与随访清单 <i class="el-icon-right" /></router-link>
        </section>
      </div>
    </div>
  </main>
</template>
<script>
import ClinicalHeader from '@/components/ClinicalHeader'
import DemoNotice from '@/components/DemoNotice'

import { questions } from '@/mock/dr/content'

export default {
  name: 'Chat',
  components: { ClinicalHeader, DemoNotice },
  data() {
    return {
      questions,
      input: '',
      counter: 1,
      messages: [{ id: 0, role: 'assistant', text: '你好，我是眼健康助手。\n可以帮助你了解双眼资料采集、共识草稿、报告签发和随访流程。先从一个问题开始吧。' }]
    }
  },
  methods: {
    handleEnter(event) {
      if (event.isComposing || event.keyCode === 229) return
      event.preventDefault()
      this.send()
    },
    scrollToLatest() { this.$nextTick(() => { if (this.$refs.messages) this.$refs.messages.scrollTop = this.$refs.messages.scrollHeight }) },
    append(text, role) { this.messages.push({ id: this.counter++, role, text }); this.scrollToLatest() },
    sendQuestion(question) { this.append(question.title, 'user'); this.append(question.answer, 'assistant') },
    send() {
      const text = this.input.trim()
      if (!text) return
      this.append(text, 'user')
      this.input = ''
      const match = questions.find(question => question.pattern.test(text))
      this.append(match ? match.answer : '当前演示助手可以解释资料采集、DME 未评估、共识草稿、报告签发与随访流程。\n关于个人影像、具体诊断、药物或治疗选择，请在医生复核时确认；这里没有读取影像或调用诊疗模型。你可以将这个问题记录到“处置与随访”的准备清单。', 'assistant')
    }
  }
}
</script>
<style scoped>
.assistant-layout { display: grid; grid-template-columns: minmax(0, 1.9fr) minmax(260px, 1fr); gap: 20px; align-items: start; }
.conversation-heading { display: flex; align-items: center; gap: 12px; padding: 18px 24px; border-bottom: 1px solid var(--border); }
.assistant-mark { display: grid; place-items: center; width: 40px; height: 40px; background: var(--primary-soft); color: var(--primary); border-radius: 8px; font-size: 23px; }
.conversation-heading h2 { font-size: 16px; margin: 0; }
.conversation-heading p { font-size: 12px; color: var(--muted); margin: 3px 0 0; }
.conversation-heading .status-pill { margin-left: auto; }
.conversation-messages { min-height: 350px; height: min(48vh, 460px); overflow-y: auto; padding: 25px 24px; background: #F8FBF9; }
.message-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 24px; }
.message-avatar { display: grid; place-items: center; width: 30px; height: 30px; flex-shrink: 0; border-radius: 7px; background: var(--primary-soft); color: var(--primary); font-size: 18px; }
.message-content { max-width: 88%; min-width: 0; }
.message-author { font-size: 11px; color: var(--muted); display: block; margin-bottom: 7px; }
.message-bubble { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 14px; line-height: 1.85; border: 1px solid var(--border); padding: 13px 16px; background: var(--panel); border-radius: 0 8px 8px 8px; }
.message-row.user { flex-direction: row-reverse; }
.user .message-avatar { color: var(--blue); background: var(--blue-soft); }
.user .message-author { text-align: right; }
.user .message-bubble { background: var(--primary-soft); color: var(--primary-hover); border-color: #CFDED6; border-radius: 8px 0 8px 8px; }
.conversation-compose { border-top: 1px solid var(--border); padding: 16px 20px 12px; }
.quick-question-row { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 13px; }
.quick-question-row button { border: 1px solid var(--border); border-radius: 5px; padding: 5px 8px; color: var(--muted); font-size: 11px; background: var(--panel); cursor: pointer; }
.quick-question-row button:hover { color: var(--primary); background: var(--primary-soft); border-color: #A9C5B8; }
.compose-form { display: flex; align-items: flex-end; gap: 10px; }
.compose-form .el-button { height: 42px; flex-shrink: 0; }
.compose-form .el-button span { margin-left: 7px; }
.conversation-compose > p { font-size: 11px; color: var(--muted); margin: 9px 0 0; }
.question-list { padding: 4px 22px; }
.question-list button { display: flex; width: 100%; justify-content: space-between; align-items: center; gap: 10px; padding: 17px 0; border: none; border-bottom: 1px solid #E7EEEB; text-align: left; font-size: 13px; color: var(--text); background: transparent; cursor: pointer; }
.question-list button:last-child { border-bottom: 0; }
.question-list button:hover { color: var(--primary); }
.question-list i { font-size: 11px; color: var(--muted); }
.assistant-next { padding: 24px; background: #EDF4EF; }
.assistant-note-icon { display: grid; place-items: center; width: 36px; height: 36px; background: #DDEBE2; color: var(--primary); border-radius: 7px; font-size: 20px; }
.assistant-next h3 { font-size: 17px; margin: 14px 0 8px; }
.assistant-next p { font-size: 13px; color: var(--muted); margin: 0 0 20px; }
.assistant-next .text-link { font-size: 12px; }
@media (max-width: 1100px) { .assistant-layout { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 767px) {
  .conversation-heading { padding: 16px; }
  .conversation-messages { padding: 20px 16px; min-height: 300px; height: 400px; }
  .message-content { max-width: calc(100% - 40px); }
  .conversation-compose { padding: 14px; }
  .compose-form { gap: 8px; }
  .compose-form .el-button { padding: 10px; }
}
</style>
