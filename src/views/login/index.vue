<template>
  <main class="login-page">
    <section class="login-story">
      <div class="login-brand"><img :src="mark" width="46" height="46" alt=""><div>糖网诊疗<span>多模态筛查与管理</span></div></div>
      <clinical-photo-carousel class="login-scene" :slides="scenes" />
      <div class="story-content">
        <h1>让每一次筛查，<br>连接更清晰的诊疗。</h1>
        <p>汇集眼底影像与临床信息，<br>衔接医生复核与持续随访。</p>
        <div class="story-steps"><span>影像采集</span><i class="el-icon-arrow-right" /><span>医生复核</span><i class="el-icon-arrow-right" /><span>持续随访</span></div>
      </div>
      <p class="login-footnote">糖尿病视网膜病变多模态诊疗系统</p>
    </section>
    <section class="login-form-area">
      <el-form ref="loginForm" :model="loginForm" :rules="rules" class="login-form" label-position="top" @submit.native.prevent="handleLogin">
        <div class="eyebrow">欢迎回来</div>
        <h2>登录诊疗工作空间</h2>
        <p class="login-description">从这里开始今天的筛查与复核。</p>
        <el-form-item label="用户名" prop="username">
          <el-input v-model.trim="loginForm.username" label="用户名" name="username" autocomplete="username" placeholder="请输入用户名" prefix-icon="el-icon-user" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" label="密码" name="password" type="password" autocomplete="current-password" placeholder="请输入密码" prefix-icon="el-icon-lock" show-password />
        </el-form-item>
        <el-button class="login-submit" type="primary" native-type="submit" :loading="loading">{{ loading ? '正在登录…' : '进入工作空间' }}<i class="el-icon-right" /></el-button>
        <div class="login-demo"><i class="el-icon-info" aria-hidden="true" /><div><strong>演示账户</strong><p>用户名 admin 或 editor，密码 111111。<br>当前使用演示登录与示例病例。</p></div></div>
      </el-form>
    </section>
  </main>
</template>
<script>
import ClinicalPhotoCarousel from '@/components/ClinicalPhotoCarousel'
export default {
  name: 'Login',
  components: { ClinicalPhotoCarousel },
  data() {
    return {
      mark: process.env.BASE_URL + 'retina-mark.svg',
      scenes: [
        { src: process.env.BASE_URL + 'images/login/eye-examination.jpg', alt: '医护使用眼科检查设备为患者检查眼睛', position: 'center 38%' },
        { src: process.env.BASE_URL + 'images/login/clinical-consultation.jpg', alt: '眼科医护与患者交流并记录检查信息', position: 'center 36%' },
        { src: process.env.BASE_URL + 'images/login/eye-care.jpg', alt: '眼科医护为患者进行细致的眼部检查', position: 'center 38%' }
      ],
      loginForm: { username: 'admin', password: '111111' },
      rules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少 6 位', trigger: 'blur' }]
      },
      loading: false
    }
  },
  methods: {
    handleLogin() {
      if (this.loading) return
      this.$refs.loginForm.validate(async valid => {
        if (!valid) return
        this.loading = true
        try {
          await this.$store.dispatch('user/login', this.loginForm)
          const redirect = this.$route.query.redirect
          this.$router.push(typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//') && !redirect.startsWith('/login') ? redirect : '/dashboard')
        } catch (error) {
          // The request layer displays the login failure.
        } finally {
          this.loading = false
        }
      })
    }
  }
}
</script>
<style scoped>
.login-page { min-height: 100vh; display: grid; grid-template-columns: 1.08fr 1fr; background: var(--panel); }
.login-story { --scene-surface-rgb: 250, 251, 252; display: flex; flex-direction: column; min-height: 100vh; background: var(--panel); }
.login-brand { display: flex; gap: 12px; align-items: center; padding: 30px 8% 24px; color: var(--heading); font-size: 22px; font-weight: 600; }
.login-brand span { display: block; color: var(--muted); font-size: 12px; font-weight: 400; letter-spacing: .08em; margin-top: 3px; }
.login-scene { flex-shrink: 0; }
.story-content { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 12px 8% 26px; background: linear-gradient(180deg, rgb(var(--scene-surface-rgb)) 0%, #FCFDFD 55%, var(--panel) 100%); }
.story-content h1 { font-size: 34px; font-weight: 600; line-height: 1.5; margin: 0 0 16px; }
.story-content p { font-size: 14px; line-height: 1.9; color: var(--muted); margin: 0; }
.story-steps { display: flex; align-items: center; gap: 18px; margin-top: 24px; font-size: 12px; color: var(--primary); }
.story-steps i { color: #789B8F; font-size: 11px; }
.login-footnote { color: var(--muted); font-size: 11px; padding: 0 8% 24px; margin: 0; }
.login-form-area { display: grid; place-items: center; padding: 48px; }
.login-form { width: 100%; max-width: 380px; }
.login-form h2 { margin: 10px 0 12px; font-size: 26px; font-weight: 600; }
.login-description { color: var(--muted); margin: 0 0 34px; }
.login-form ::v-deep .el-form-item { margin-bottom: 24px; }
.login-form ::v-deep .el-input__inner { height: 48px; line-height: 48px; border-radius: 8px; }
.login-form ::v-deep .el-input__icon { line-height: 48px; }
.login-form ::v-deep .el-input__inner:focus { box-shadow: 0 0 0 3px var(--primary-soft); }
.login-submit { width: 100%; height: 48px; margin-top: 6px; border-radius: 8px; font-size: 15px; }
.login-submit i { margin-left: 14px; }
.login-demo { display: flex; align-items: baseline; gap: 10px; margin-top: 26px; padding: 16px; background: var(--page); border-radius: 8px; font-size: 12px; color: var(--muted); }
.login-demo strong, .login-demo i { color: var(--primary); }
.login-demo p { margin: 4px 0 0; line-height: 1.8; }
@media (min-width: 1700px) {
  .story-content h1 { font-size: 36px; }
}
@media (max-width: 1000px) and (min-width: 768px) {
  .login-form-area { padding: 36px; }
  .story-content h1 { font-size: 28px; }
  .story-steps { gap: 12px; }
}
@media (max-height: 800px) and (min-width: 768px) {
  .login-brand { padding-top: 20px; padding-bottom: 14px; }
  .login-scene { max-height: calc(100vh - 324px); }
  .story-content { padding-top: 6px; padding-bottom: 16px; }
  .story-content h1 { font-size: 28px; margin-bottom: 12px; }
  .story-steps { margin-top: 12px; }
  .login-footnote { padding-bottom: 12px; }
}
@media (max-width: 767px) {
  .login-page { display: block; }
  .login-story { min-height: auto; }
  .login-brand { padding: 16px 24px 12px; font-size: 21px; }
  .login-brand img { width: 34px; height: 34px; }
  .login-scene { max-height: 180px; }
  .story-content { padding: 10px 24px 24px; }
  .story-content h1 { font-size: 22px; line-height: 1.45; margin: 0; }
  .story-content p, .story-steps, .login-footnote { display: none; }
  .login-form-area { padding: 32px 24px; }
  .login-form h2 { font-size: 24px; }
  .login-description { font-size: 13px; margin-bottom: 28px; }
}
</style>
