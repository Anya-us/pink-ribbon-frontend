<template>
  <section class="panel"><div class="panel-heading"><div><h2>检查时间线</h2><p>每次检查单独记录，按时间查看双眼资料。</p></div><span class="muted small-text">{{ examinations.length }} 次检查</span></div><div v-if="!examinations.length" class="empty-state">暂无检查记录</div><ol v-else class="dr-examination-timeline"><li v-for="exam in examinations" :key="exam.id"><div class="timeline-header"><time>{{ exam.performedAt.slice(0, 10) }}</time><span class="status-pill" :class="exam.status === 'signed' ? 'success' : 'warning'">{{ exam.status === 'signed' ? '合成报告已签发' : '资料 / 审核待完成' }}</span></div><p>{{ exam.id }}</p><div class="timeline-eyes"><span v-for="eye in eyes" :key="eye"><strong>{{ eye === 'OD' ? '右眼 OD' : '左眼 OS' }}</strong><quality-status :status="exam.eyes[eye].quality.status" /><span>{{ gradeInfo(exam.eyes[eye].drGrade).label }}</span></span></div><el-button type="text" @click="$emit('select', exam.id)">查看本次检查 <i class="el-icon-right" /></el-button></li></ol></section>
</template>
<script>
import { gradeInfo } from '@/data/retina-demo'
import QualityStatus from './QualityStatus'
export default { name: 'DrExaminationTimeline', components: { QualityStatus }, props: { examinations: { type: Array, default: () => [] }}, data() { return { eyes: ['OD', 'OS'] } }, methods: { gradeInfo }}
</script>
<style scoped>
.dr-examination-timeline { list-style: none; padding: 0 24px; margin: 0; }
li { padding: 22px 0; border-bottom: 1px solid var(--border); }
li:last-child { border: 0; }
.timeline-header { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
time { font-weight: 600; color: var(--heading); }
p { margin: 6px 0 14px; font-size: 12px; color: var(--muted); }
.timeline-eyes { display: flex; gap: 20px; flex-wrap: wrap; }
.timeline-eyes > span { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; font-size: 13px; }
.timeline-eyes strong { font-weight: 500; }
</style>
