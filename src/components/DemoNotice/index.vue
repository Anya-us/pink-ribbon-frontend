<template>
  <div class="demo-notice" role="note">
    <i class="el-icon-info" aria-hidden="true" />
    <span><strong>演示环境</strong><span class="notice-divider">·</span>{{ text }}</span>
  </div>
</template>
<script>
export default {
  name: 'DemoNotice',
  props: { text: { type: String, default: '页面病例与评估结果为示例数据，AI 草稿需由医生复核后签发。' }}
}
</script>
<style scoped>
.demo-notice { display: flex; align-items: baseline; gap: 9px; padding: 11px 15px; margin-bottom: 20px; border: 1px solid #CFDDD8; border-radius: 6px; color: var(--muted); background: #EDF3F0; font-size: 13px; line-height: 1.7; }
.demo-notice i, .demo-notice strong { color: var(--primary); }
.notice-divider { margin: 0 9px; }
</style>
