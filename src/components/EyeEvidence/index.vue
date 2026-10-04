<template><image-preview :examination="bundle.examination" :images="bundle.images" :files="files" :institution="bundle.institution.name" /></template>
<script>
import ImagePreview from '@/components/dr/ImagePreview'
import { currentBundle, demoState } from '@/data/retina-demo'
export default { name: 'EyeEvidence', components: { ImagePreview }, computed: { bundle: currentBundle, files() { return demoState.files } }}
</script>
