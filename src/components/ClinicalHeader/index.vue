<template>
  <header v-if="$slots.default" class="page-header">
    <div class="page-actions"><slot /></div>
  </header>
</template>
<script>
export default {
  name: 'ClinicalHeader',
  props: {
    title: { type: String, required: true },
    description: { type: String, default: '' }
  }
}
</script>
