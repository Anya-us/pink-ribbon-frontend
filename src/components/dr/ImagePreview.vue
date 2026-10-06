<template>
  <section class="panel eye-evidence">
    <div class="panel-heading"><h2>影像证据查看</h2><quality-status :status="quality.status" /></div>
    <div class="viewer-toolbar"><eye-switcher v-model="activeEye" /><div class="viewer-tabs" role="group" aria-label="选择影像模态"><button v-for="item in modalities" :key="item" type="button" :aria-pressed="String(modality === item)" :class="{ active: modality === item }" @click="modality = item">{{ item === 'CFP' ? '眼底彩照' : 'OCT' }}</button></div></div>
    <div class="image-canvas"><img v-if="imageUrl && !imageError" :src="imageUrl" :alt="eyeLabel + (localFile ? '本地原始影像' : '合成结构示意，非真实病例影像')" :style="{ transform: 'scale(' + zoom + ')' }" @error="imageError = true"><div v-else class="canvas-placeholder"><i class="el-icon-picture-outline" aria-hidden="true" /><strong>{{ imageError ? '无法预览此文件' : imageRecord && imageRecord.sourceType === 'local' ? '请重新选择本地文件' : imageRecord ? '此记录未配置可预览原图' : '暂无该眼影像资料' }}</strong><p>{{ localFile ? localFile.name : imageRecord ? imageRecord.fileName : '缺失资料保留未评估状态' }}</p></div><div class="canvas-caption">{{ eyeLabel }} {{ activeEye }} · {{ modality }}</div></div>
    <div class="preview-source"><source-device-tag :source="localFile ? 'local' : imageRecord ? imageRecord.sourceType : 'unknown'" :device="!localFile && imageRecord ? imageRecord.device : null" :institution="institution" /></div>
    <div class="viewer-footer"><span>{{ localFile ? '本地原图预览，未添加病灶标注。' : imageRecord && imageRecord.isSchematic ? '合成结构示意，非真实眼底图，不用于诊断。' : '图像记录与原图可用性分别显示。' }}</span><div v-if="imageUrl && !imageError" class="zoom-controls"><button type="button" aria-label="缩小影像" :disabled="zoom <= 1" @click="zoom = Math.max(1, zoom - .25)"><i class="el-icon-minus" /></button><span>{{ Math.round(zoom * 100) }}%</span><button type="button" aria-label="放大影像" :disabled="zoom >= 2" @click="zoom = Math.min(2, zoom + .25)"><i class="el-icon-plus" /></button><button type="button" aria-label="重置影像缩放" @click="zoom = 1"><i class="el-icon-refresh-left" /></button></div></div>
  </section>
</template>
<script>
import EyeSwitcher from './EyeSwitcher'
import QualityStatus from './QualityStatus'
import SourceDeviceTag from './SourceDeviceTag'
export default {
  name: 'DrImagePreview', components: { EyeSwitcher, QualityStatus, SourceDeviceTag },
  props: { examination: { type: Object, required: true }, images: { type: Array, default: () => [] }, files: { type: Object, default: () => ({}) }, institution: { type: String, default: '' }},
  data() { return { activeEye: 'OD', modality: 'CFP', modalities: ['CFP', 'OCT'], zoom: 1, imageError: false } },
  computed: {
    eyeLabel() { return this.activeEye === 'OD' ? '右眼' : '左眼' },
    localFile() { return this.files[(this.activeEye === 'OD' ? 'right' : 'left') + (this.modality === 'CFP' ? 'Cfp' : 'Oct')] },
    imageRecord() { return this.images.find(item => item.eye === this.activeEye && item.modality === this.modality) },
    imageUrl() { return this.localFile ? this.localFile.url : this.imageRecord && this.imageRecord.previewUrl ? process.env.BASE_URL + this.imageRecord.previewUrl : '' },
    quality() {
      if (this.examination.sourceType === 'local' && this.examination.eyes[this.activeEye]) return this.examination.eyes[this.activeEye].quality
      if (this.localFile) return { status: 'pending', reason: '本地选择，尚未质控。' }
      if (!this.imageRecord) return { status: 'missing', reason: '尚未登记该眼该模态影像。' }
      return { status: this.imageRecord.quality, reason: this.examination.eyes[this.activeEye].quality.reason }
    }
  },
  watch: { imageUrl() { this.zoom = 1; this.imageError = false }, 'examination.id'() { this.activeEye = 'OD'; this.modality = 'CFP'; this.zoom = 1; this.imageError = false } }
}
</script>
<style scoped>
.viewer-toolbar { display: flex; justify-content: space-between; gap: 10px; padding: 12px 18px; background: #F6F9F7; }
.viewer-tabs { display: flex; gap: 3px; }
.viewer-tabs button { border: 0; border-radius: 5px; padding: 7px 10px; background: transparent; color: var(--muted); cursor: pointer; font-size: 12px; }
.viewer-tabs button.active { background: var(--primary-soft); color: var(--primary-hover); }
.image-canvas { height: 340px; background: var(--viewer); display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
.image-canvas > img { width: 100%; height: 100%; object-fit: contain; }
.canvas-placeholder { text-align: center; color: #D9E6DF; padding: 25px 16px; max-width: 90%; overflow-wrap: anywhere; }
.canvas-placeholder i { display: block; font-size: 40px; margin-bottom: 15px; }
.canvas-placeholder p { font-size: 12px; color: #BCCEC6; }
.canvas-caption { position: absolute; top: 15px; left: 18px; color: #D9E6DF; font-size: 12px; background: #283B36; padding: 3px 9px; border-radius: 5px; }
.preview-source { padding: 12px 18px 0; }
.viewer-footer { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; padding: 12px 18px; font-size: 12px; color: var(--muted); }
.zoom-controls { display: flex; align-items: center; gap: 7px; }
.zoom-controls button { width: 28px; height: 28px; border: 1px solid var(--border); background: var(--panel); color: var(--primary); border-radius: 5px; cursor: pointer; }
.zoom-controls button:disabled { color: var(--input-border); cursor: default; }
@media (max-width: 767px) { .image-canvas { height: 280px; } .viewer-toolbar { padding: 10px; flex-wrap: wrap; } }
</style>
