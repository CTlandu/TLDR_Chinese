<template>
  <div class="navbar bg-base-200">
    <div class="flex-1">
      <router-link to="/" class="btn btn-ghost text-xl"
        >TLDR每日科技新闻💻</router-link
      >
      <router-link :to="`/newsletter/${today}`" class="btn btn-ghost"
        >今日新闻</router-link
      >
      <span class="text-base-content/60">广告投放</span>
    </div>
    <div class="flex-none gap-2">
      <button @click="changeLanguage('en')" class="btn btn-ghost btn-sm">
        🇺🇸 English
      </button>
      <button @click="changeLanguage('zh')" class="btn btn-ghost btn-sm">
        🇨🇳 中文
      </button>
    </div>
  </div>
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
