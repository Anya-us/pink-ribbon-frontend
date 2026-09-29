<template>
  <div class="video-player">
    <video :src="src" controls width=100% :height="height"></video>
  </div>
</template>

<script>
export default {
  name: "VideoPlayer",
  props: {
    src: { type: String, required: true },
    width: { type: [String, Number], default: 600 },
    height: { type: [String, Number], default: 400 }
  }
}
</script>
