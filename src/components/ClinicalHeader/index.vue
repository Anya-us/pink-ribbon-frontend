<template>
  <header class="page-header">
    <div>
      <h1>{{ title }}</h1>
      <p>{{ description }}</p>
    </div>
    <div v-if="$slots.default" class="page-actions"><slot /></div>
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
