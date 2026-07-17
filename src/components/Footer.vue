<template>
  <footer class="mt-auto border-t border-white/5">
    <div
      class="max-w-content mx-auto w-full px-4 sm:px-6 py-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-base-content/50"
    >
      <p>© {{ currentYear }} 太长不看 · 每日科技新闻中文速递</p>
      <div class="flex items-center gap-5">
        <router-link
          :to="`/newsletter/${today}`"
          class="hover:text-base-content transition-colors"
        >
          往期存档
        </router-link>
        <a
          href="https://mp.weixin.qq.com/s/8k55rjuc4GCsYlrD_i5n3A"
          target="_blank"
          rel="noopener"
          class="hover:text-base-content transition-colors"
        >
          微信公众号
        </a>
        <a
          href="mailto:jizhoutang@outlook.com"
          class="hover:text-base-content transition-colors"
        >
          联系我们
        </a>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer',
  computed: {
    currentYear() {
      return new Date().getFullYear();
    },
    today() {
      return new Date().toISOString().split('T')[0];
    },
  },
};
</script>
