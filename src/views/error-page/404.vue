<template>
  <main class="missing-page">
    <img :src="mark" width="64" height="64" alt="">
    <div class="eyebrow">404</div>
    <h1>这个页面暂时找不到</h1>
    <p>可以返回工作台，继续查看筛查病例与随访任务。</p>
    <el-button type="primary" @click="$router.push('/dashboard')">返回工作台</el-button>
  </main>
</template>
<script>
export default {
  name: 'Page404',
  data() { return { mark: process.env.BASE_URL + 'retina-mark.svg' } }
}
</script>
<style scoped>
.missing-page { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 24px; text-align: center; }
.missing-page .eyebrow { margin-top: 28px; }
.missing-page h1 { font-size: 26px; margin: 0; }
.missing-page p { color: var(--muted); margin: 16px 0 28px; }
</style>
