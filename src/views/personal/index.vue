<template>
  <div class="personal-info">
    <!-- 顶部按钮组 -->
    <div class="btn-group">
      <button class="tab-btn" :class="{ active: currentPage === 'left' }" 
      @click="switchPage('left')">基本信息</button>
      <div class="divider"></div>
      <button class="tab-btn" :class="{ active: currentPage === 'right' }"
      @click="switchPage('right')">临床信息</button>
    </div>

    <!-- 页面内容，带渐变效果 -->
    <transition name="fade" mode="out-in">
      <keep-alive> <!--保证页面来回切换不会销毁数据-->
        <component :is="currentPageComponent" :key="currentPage" />
      </keep-alive>  
    </transition>
  </div>
</template>

<script>
import LeftPage from './LeftPage/index'
import RightPage from './RightPage/index'

export default {
  name: 'Personal',
  components: { LeftPage, RightPage },
  data() {
    return {
      currentPage: 'left'
    }
  },
  computed: {
    currentPageComponent() {
      return this.currentPage === 'left' ? LeftPage : RightPage
    }
  },
  methods: {
    switchPage(page) {
      this.currentPage = page
    }
  }
}
</script>

<style scoped>
.personal-info {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
    background-color: #f5f7fa;
}
/* 顶部按钮组 */
.btn-group {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  margin-top: 30px;
}
/* 无背景无边框按钮 */
.tab-btn {
  background: none;
  border: none;
  font-size: 16px;
  padding: 8px 16px;
  cursor: pointer;
  color: #666;
  transition: color 0.3s, font-weight 0.3s;
}
.tab-btn:hover {
  color: #ffccd3;
}
.tab-btn.active {
  color: #f5adb8;
  font-weight: bold;
}
.divider {
  width: 1px;
  height: 20px;
  background: #ddd;
  margin: 0 12px;
}
/* 渐入渐出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.6s ease;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>