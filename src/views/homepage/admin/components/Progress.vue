<template>
  <div class="case-analysis">
    <div class="case-item" v-for="item in cases" :key="item.label">
      <span class="case-label">{{ item.label }}</span>
      <el-progress
        :percentage="item.percentage"
        :color="item.color"
        :stroke-width="16"
        :show-text="false"
        class="case-progress"
      />
      <span class="case-value">{{ item.value }}人</span>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      cases: [
        { label: "系统使用人数", value: 130, percentage: 65, color: "#409EFF" },
        { label: "预测准确率", value: 100, percentage: 50, color: "#67C23A" },
        { label: "用户满意度", value: 100, percentage: 50, color: "#F56C6C" }
      ]
    };
  }
};
</script>

<style scoped>
.case-analysis {
  padding: 20px;
}
.case-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px; /* 行间距更大 */
}
.case-label {
  width: 120px;
  font-size: 14px;
  color: #333;
}
.case-progress {
  flex: 1;
  margin: 0 15px;
}
.case-value {
  width: 60px;
  text-align: right;
  font-size: 14px;
  color: #666;
}
</style>