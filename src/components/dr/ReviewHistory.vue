<template>
  <section class="panel"><div class="panel-heading"><h2>审核记录</h2><span class="muted small-text">{{ records.length }} 条</span></div><div v-if="!records.length" class="empty-state"><i class="el-icon-document-checked" /><h3>尚无审核记录</h3><p>医生确认后，记录审核意见、操作人与时间。</p></div><ol v-else class="dr-review-history"><li v-for="record in records" :key="record.id"><div><strong>{{ record.action }}</strong><time>{{ formatTime(record.createdAt) }}</time></div><p>{{ record.actor }} · {{ record.comment }}</p><small>合成记录 · {{ record.id }}</small></li></ol></section>
</template>
<script>
export default { name: 'DrReviewHistory', props: { records: { type: Array, default: () => [] }}, methods: { formatTime(value) { return value.slice(0, 16).replace('T', ' ') } }}
</script>
<style scoped>
.dr-review-history { list-style: none; margin: 0; padding: 4px 24px; }
li { padding: 18px 0; border-bottom: 1px solid var(--border); }
li:last-child { border: 0; }
li > div { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
strong { color: var(--heading); font-size: 14px; }
p { margin: 6px 0; }
time, small { color: var(--muted); font-size: 12px; }
</style>
