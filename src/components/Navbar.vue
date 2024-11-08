<template>
  <nav class="bg-white shadow-md p-4 flex justify-between items-center">
    <div class="flex items-center space-x-4">
      <router-link to="/" class="text-xl font-bold text-primary"
        >TLDR每日科技新闻💻</router-link
      >
      <router-link
        :to="`/newsletter/${today}`"
        class="text-gray-700 hover:text-primary"
        >今日科技新闻</router-link
      >
      <span class="text-gray-700">广告投放</span>
    </div>
    <div class="flex items-center space-x-2">
      <button
        @click="changeLanguage('en')"
        class="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
      >
        🇺🇸 English
      </button>
      <button
        @click="changeLanguage('zh')"
        class="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
      >
        🇨🇳 中文
      </button>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navbar',
  computed: {
    today() {
      const date = new Date();
      return date.toISOString().split('T')[0];
    },
  },
  methods: {
    changeLanguage(lang) {
      this.$i18n.locale = lang;
    },
  },
};
</script>

<style scoped>
nav {
  background-color: #f8f9fa;
}
</style>
