<template>
  <div class="video-player">
    <video
      class="video-content"
      :src="videoSrc"
      controls
      playsinline
    ></video>
  </div>
</template>

<script>
import videoSrc from '@/assets/video1.mp4'

export default {
  name: "VideoPlayer",
  data() {
    return {
      videoSrc
    }
  }
}
</script>

<style scoped>
.video-player {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.video-content {
  width: 100%;
  height: auto; /* ✅ 自动保持视频比例 */
  display: block;
  object-fit: cover; /* 可改为 contain 看需求 */
}
</style>
