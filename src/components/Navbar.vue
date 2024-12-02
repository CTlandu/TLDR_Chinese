<template>
  <div class="navbar bg-base-200">
    <div class="flex-1 flex items-center gap-2 pl-4">
      <router-link to="/" class="flex items-center gap-2">
        <img src="../../assets/logo.png" alt="TLDR Logo" class="h-8 w-8" />
        <span class="rainbow-text font-bold text-xl">太长不看</span>
      </router-link>
      <div class="divider divider-horizontal mx-2"></div>
      <router-link :to="`/newsletter/${today}`" class="btn btn-ghost">
        今日新闻
      </router-link>
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
.rainbow-text {
  background: linear-gradient(
    to right,
    #ff0000,
    /* #ff8000,
    #ffff00, */ #00ff00,
    #00ffff,
    #0000ff,
    #8000ff
  );
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: rainbow-move 5s linear infinite;
  background-size: 200% auto;
}

@keyframes rainbow-move {
  0% {
    background-position: 0% center;
  }
  100% {
    background-position: 200% center;
  }
}
</style>
