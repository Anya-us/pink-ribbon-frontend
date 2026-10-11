<template>
  <div class="demo-notice" role="note">
    <i class="el-icon-info" aria-hidden="true" />
    <span><strong>提示</strong><span class="notice-divider">·</span>{{ text }}</span>
  </div>
</template>
<script>
export default {
  name: 'DemoNotice',
  props: { text: { type: String, default: '页面病例与评估结果为示例数据，AI 草稿需由医生复核后签发。' }}
}
</script>
<style scoped>
.demo-notice { display: none; }
.demo-notice i, .demo-notice strong { color: var(--primary); }
.notice-divider { margin: 0 9px; }
</style>
