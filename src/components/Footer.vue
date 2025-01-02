<template>
  <footer class="bg-base-200 mt-auto">
    <div class="max-w-6xl mx-auto px-4 py-8">
      <div class="flex flex-col md:flex-row justify-between items-center gap-4">
        <!-- 左侧版权信息 -->
        <div class="text-center md:text-left">
          <p class="text-sm text-base-content/70">
            © {{ currentYear }} TLDR Tech. All rights reserved.
          </p>
        </div>

        <!-- 中间作者信息 -->
        <div class="text-center">
          <p class="text-sm text-base-content/70">
            Created by
            <a
              href="https://ctlandu.github.io"
              target="_blank"
              rel="noopener noreferrer"
              class="text-primary hover:underline"
            >
              @colintang
            </a>
          </p>
        </div>

        <!-- 右侧链接 -->
        <div class="flex gap-4">
          <router-link
            to="/privacy"
            class="text-sm text-base-content/70 hover:text-primary"
          >
            隐私政策
          </router-link>
          <router-link
            to="/terms"
            class="text-sm text-base-content/70 hover:text-primary"
          >
            使用条款
          </router-link>
          <a
            href="mailto:jizhoutang@outlook.com"
            class="text-sm text-base-content/70 hover:text-primary"
          >
            联系我们
          </a>
        </div>
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
  },
};
</script>
