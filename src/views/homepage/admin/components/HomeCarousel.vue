<template>
  <el-carousel :interval="2000" type="card" :autoplay="true" height="300px">
    <el-carousel-item v-for="(banner, index) in banners" :key="index">
        <a :href="banner.link" target="_blank" rel="noopener noreferrer">
          <img :src="banner.img" class="banner-img" />
        </a>
    </el-carousel-item>
  </el-carousel>
</template>

<script>
import banner1 from '@/assets/home_images/banner1.png'
import banner2 from '@/assets/home_images/banner2.png'
import banner3 from '@/assets/home_images/banner3.png'

export default {
  name: 'HomeCarousel',
  data() {
    return {
      carouselHeight: (window.innerWidth * 3 / 4) + 'px',
      banners: [
        {
          img: banner1
        },
        {
          img: banner2,
          link: 'https://github.com'
        },
        {
          img: banner3,
          link: 'https://vuejs.org'
        }
      ]
    }
  },
  mounted(){
    window.addEventListener('resize',() => {
      this.carouselHeight = (window.innerWidth * 3 / 4) +'px'
    })
  }
}
</script>

<style scoped>
.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}
</style>
