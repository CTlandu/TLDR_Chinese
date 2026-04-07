<template>
  <div class="min-h-screen bg-base-100">
    <Navbar />
    <div class="flex items-center justify-center py-16">
      <div class="max-w-md mx-auto text-center p-8">
        <div class="text-6xl mb-6">🎉</div>
        <h1 class="text-3xl font-bold mb-4">订阅确认成功！</h1>
        <p class="text-lg mb-8">
          {{ message }}
        </p>
        <router-link to="/" class="btn btn-primary"> 返回首页 </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import { useRouter } from 'vue-router';
import { useHead } from '@unhead/vue';

export default {
  name: 'SubscriptionSuccess',
  components: {
    Navbar,
  },
  setup() {
    useHead({
      title: '订阅确认成功 | 太长不看',
      meta: [{ name: 'robots', content: 'noindex, nofollow' }],
    });
  },
  data() {
    return {
      message:
        '感谢您订阅 TLDR Chinese 每日科技新闻。\n您将开始收到我们的每日更新。',
    };
  },
  created() {
    // 移除这些检查，让页面直接显示
    const status = this.$route.query.status;
    if (status === 'already_confirmed') {
      this.message = '您已经成功订阅过了！\n我们会继续为您发送每日科技新闻。';
    }
  },
};
</script>
