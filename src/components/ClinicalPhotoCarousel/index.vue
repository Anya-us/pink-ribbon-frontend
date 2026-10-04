<template>
  <section class="clinical-photo-carousel" :style="{ '--photo-fade-duration': fadeDuration + 'ms' }" aria-label="眼科诊疗场景">
    <img
      v-for="(slide, index) in slides"
      :key="slide.src"
      :src="slide.src"
      :alt="slide.alt"
      :class="['scene-photo', { 'is-active': index === activeIndex || (activeIndex < 0 && index === 0), 'is-entering': index === incomingIndex, 'is-visible': index === incomingIndex && fading }]"
      :aria-hidden="index !== activeIndex"
      :fetchpriority="index === 0 ? 'high' : 'low'"
      :style="{ objectPosition: slide.position || 'center' }"
      width="1600"
      height="1067"
      loading="eager"
      decoding="async"
      @load="onPhotoLoad(index, $event)"
      @error="onPhotoError(index)"
      @transitionend="onTransitionEnd(index, $event)"
    >
    <div v-if="activeIndex >= 0 && readyCount > 1" class="photo-controls">
      <div class="photo-selectors" aria-label="选择诊疗场景">
        <button
          v-for="(slide, index) in slides"
          :key="slide.src"
          type="button"
          :class="{ selected: index === displayedIndex }"
          :aria-label="'查看第 ' + (index + 1) + ' 张诊疗场景'"
          :aria-current="index === displayedIndex ? 'true' : undefined"
          :disabled="photoStates[index] !== 'ready' || incomingIndex !== null"
          @click="selectPhoto(index)"
        />
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'ClinicalPhotoCarousel',
  props: {
    slides: { type: Array, required: true },
    holdDuration: { type: Number, default: 6000 },
    fadeDuration: { type: Number, default: 1600 }
  },
  data() {
    return {
      activeIndex: -1,
      incomingIndex: null,
      fading: false,
      photoStates: this.slides.map(() => 'pending'),
      reducedMotion: false
    }
  },
  computed: {
    readyCount() { return this.photoStates.filter(state => state === 'ready').length },
    displayedIndex() { return this.fading ? this.incomingIndex : this.activeIndex }
  },
  created() {
    this._alive = true
    this._rotationTimer = null
    this._fadeTimer = null
    this._fadeFrame = null
    this._motionQuery = null
  },
  mounted() {
    document.addEventListener('visibilitychange', this.onVisibilityChange)
    if (window.matchMedia) {
      this._motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
      this.reducedMotion = this._motionQuery.matches
      if (this._motionQuery.addEventListener) {
        this._motionQuery.addEventListener('change', this.onMotionChange)
      } else {
        this._motionQuery.addListener(this.onMotionChange)
      }
    }
    this.scheduleRotation()
  },
  beforeDestroy() {
    this._alive = false
    this.clearRotation()
    this.clearTransition()
    document.removeEventListener('visibilitychange', this.onVisibilityChange)
    if (this._motionQuery) {
      if (this._motionQuery.removeEventListener) {
        this._motionQuery.removeEventListener('change', this.onMotionChange)
      } else {
        this._motionQuery.removeListener(this.onMotionChange)
      }
    }
  },
  methods: {
    async onPhotoLoad(index, event) {
      const photo = event.target
      if (photo.decode) {
        try {
          await photo.decode()
        } catch (error) {
          if (!photo.complete || !photo.naturalWidth) {
            if (this._alive) this.onPhotoError(index)
            return
          }
        }
      }
      if (!this._alive || !photo.naturalWidth) return
      this.$set(this.photoStates, index, 'ready')
      if (this.activeIndex < 0) this.activeIndex = index
      this.scheduleRotation()
    },
    onPhotoError(index) {
      if (!this._alive) return
      this.$set(this.photoStates, index, 'error')
      if (this.incomingIndex === index) {
        this.clearTransition()
        this.incomingIndex = null
        this.fading = false
      }
      if (this.activeIndex === index) {
        this.activeIndex = this.photoStates.findIndex(state => state === 'ready')
      }
      this.scheduleRotation()
    },
    clearRotation() {
      window.clearTimeout(this._rotationTimer)
      this._rotationTimer = null
    },
    clearTransition() {
      window.clearTimeout(this._fadeTimer)
      window.cancelAnimationFrame(this._fadeFrame)
      this._fadeTimer = null
      this._fadeFrame = null
    },
    scheduleRotation() {
      this.clearRotation()
      if (!this._alive || document.hidden || this.reducedMotion ||
        this.activeIndex < 0 || this.readyCount < 2 || this.incomingIndex !== null) return
      this._rotationTimer = window.setTimeout(this.advance, this.holdDuration)
    },
    advance() {
      if (!this._alive || document.hidden || this.reducedMotion) return
      for (let offset = 1; offset < this.slides.length; offset++) {
        const index = (this.activeIndex + offset) % this.slides.length
        if (this.photoStates[index] === 'ready') {
          this.startTransition(index)
          return
        }
      }
    },
    selectPhoto(index) {
      if (index === this.activeIndex || this.photoStates[index] !== 'ready' || this.incomingIndex !== null) return
      this.startTransition(index)
    },
    startTransition(index) {
      if (!this._alive || this.photoStates[index] !== 'ready') return
      this.clearRotation()
      if (this.reducedMotion) {
        this.activeIndex = index
        return
      }
      this.incomingIndex = index
      this.fading = false
      // Keep the decoded current photo opaque beneath the incoming photo.
      this.$nextTick(() => {
        if (!this._alive || this.incomingIndex !== index) return
        this._fadeFrame = window.requestAnimationFrame(() => {
          this._fadeFrame = window.requestAnimationFrame(() => {
            if (!this._alive || this.incomingIndex !== index) return
            this.fading = true
            this._fadeTimer = window.setTimeout(this.finishTransition, this.fadeDuration + 100)
          })
        })
      })
    },
    onTransitionEnd(index, event) {
      if (event.propertyName === 'opacity' && this.fading && index === this.incomingIndex) this.finishTransition()
    },
    finishTransition() {
      this.clearTransition()
      if (this.incomingIndex !== null) {
        this.activeIndex = this.incomingIndex
        this.incomingIndex = null
        this.fading = false
      }
      this.scheduleRotation()
    },
    onVisibilityChange() {
      if (document.hidden) {
        this.clearRotation()
        if (this.incomingIndex !== null) this.finishTransition()
      } else {
        this.scheduleRotation()
      }
    },
    onMotionChange(event) {
      this.reducedMotion = event.matches
      if (this.reducedMotion && this.incomingIndex !== null) this.finishTransition()
      this.scheduleRotation()
    }
  }
}
</script>

<style scoped>
.clinical-photo-carousel { position: relative; isolation: isolate; width: 100%; aspect-ratio: 3 / 2; overflow: hidden; background: rgb(var(--scene-surface-rgb, 250, 251, 252)); }
.scene-photo { position: absolute; inset: 0; display: block; width: 100%; height: 100%; object-fit: cover; opacity: 0; z-index: 0; }
.scene-photo.is-active { opacity: 1; z-index: 1; }
.scene-photo.is-entering { z-index: 2; transition: opacity var(--photo-fade-duration) cubic-bezier(.4, 0, .2, 1); will-change: opacity; }
.scene-photo.is-entering.is-visible { opacity: 1; }
.clinical-photo-carousel::after {
  content: "";
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: clamp(28px, 15%, 76px);
  pointer-events: none;
  z-index: 3;
  background: linear-gradient(180deg,
    rgba(var(--scene-surface-rgb, 250, 251, 252), 0) 0%,
    rgba(var(--scene-surface-rgb, 250, 251, 252), .03) 18%,
    rgba(var(--scene-surface-rgb, 250, 251, 252), .11) 36%,
    rgba(var(--scene-surface-rgb, 250, 251, 252), .27) 54%,
    rgba(var(--scene-surface-rgb, 250, 251, 252), .52) 72%,
    rgba(var(--scene-surface-rgb, 250, 251, 252), .8) 88%,
    rgb(var(--scene-surface-rgb, 250, 251, 252)) 100%);
}
.photo-controls { position: absolute; z-index: 4; right: 24px; bottom: 24px; display: flex; align-items: center; gap: 10px; }
.photo-selectors { display: flex; gap: 4px; padding: 3px 6px; border-radius: 20px; background: transparent; }
.photo-selectors button { width: 24px; height: 26px; padding: 0; border: 0; background: transparent; cursor: pointer; position: relative; border-radius: 4px; }
.photo-selectors button::after { content: ""; position: absolute; left: 6px; right: 6px; top: 12px; height: 3px; border-radius: 2px; background: #819A92; }
.photo-selectors button.selected::after { background: #2D8075; }
.photo-selectors button:disabled { cursor: default; }
@media (max-width: 767px) {
  .photo-controls { right: 18px; bottom: 12px; gap: 7px; }
  .photo-selectors { padding: 1px 5px; }
}
@media (prefers-reduced-motion: reduce) {
  .scene-photo.is-entering { transition: none; }
}
</style>
