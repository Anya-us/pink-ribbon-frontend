<template>
  <div class="dr-eye-switcher" role="group" aria-label="选择眼别">
    <button v-for="eye in choices" :key="eye.code" type="button" :aria-pressed="String(value === eye.code)" :class="{ active: value === eye.code }" @click="$emit('input', eye.code)">{{ eye.label }}</button>
  </div>
</template>
<script>
export default { name: 'DrEyeSwitcher', props: { value: { type: String, default: 'OD', validator: value => ['OD', 'OS'].includes(value) }}, data() { return { choices: [{ code: 'OD', label: '右眼 OD' }, { code: 'OS', label: '左眼 OS' }] } } }
</script>
<style scoped>
.dr-eye-switcher { display: inline-flex; gap: 3px; }
button { border: 0; border-radius: 5px; padding: 7px 10px; background: transparent; color: var(--muted); cursor: pointer; font-size: 12px; }
button:hover { background: var(--primary-soft); }
button.active { background: var(--primary-soft); color: var(--primary-hover); font-weight: 600; }
</style>
