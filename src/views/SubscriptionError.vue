<template>
  <div class="min-h-screen bg-base-100">
    <Navbar />
    <div class="flex items-center justify-center py-16">
      <div class="max-w-md mx-auto text-center p-8">
        <div class="text-6xl mb-6">😕</div>
        <h1 class="text-3xl font-bold mb-4">订阅确认失败</h1>
        <p class="text-lg mb-8">
          {{ message }}
        </p>
        <router-link to="/" class="btn btn-primary"> 返回首页重试 </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';

export default {
  name: 'SubscriptionError',
  components: {
    Navbar,
  },
  data() {
    return {
      message: '抱歉，确认链接可能已过期或无效。\n请重新尝试订阅。',
    };
  },
  created() {
    // 检查URL参数
    const message = this.$route.query.message;
    if (message === 'invalid_token') {
      this.message = '无效的确认链接。\n请重新尝试订阅。';
    }
  },
};
</script>
