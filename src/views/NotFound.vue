<template>
  <div class="hero min-h-screen bg-base-200">
    <div class="hero-content text-center">
      <div class="max-w-md">
        <h1 class="text-5xl font-bold">404</h1>
        <p class="py-6">页面不存在</p>
        <router-link to="/newsletter" class="btn btn-primary"
          >返回首页</router-link
        >
      </div>
    </div>
  </div>
</template>

<script>
import { useHead } from '@unhead/vue';

export default {
  name: 'NotFound',
  setup() {
    useHead({
      title: '页面不存在 | 太长不看',
      meta: [{ name: 'robots', content: 'noindex, nofollow' }],
    });
  },
};
</script>
