<template>
  <router-view></router-view>
</template>

<script>
import { onMounted } from 'vue';
import { useAccessibility } from './composables/useAccessibility';

export default {
  name: 'App',
  setup() {
    // 在应用启动时初始化可访问性设置
    onMounted(() => {
      useAccessibility();
    });
  },
};
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
</style>
