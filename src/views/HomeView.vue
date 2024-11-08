<template>
  <div>
    <!-- Language Switcher -->
    <div class="language-switcher text-right p-4">
      <button @click="changeLanguage('en')" class="mr-2">English</button>
      <button @click="changeLanguage('zh')">中文</button>
    </div>
    <!-- Hero Section -->
    <section class="hero bg-primary text-white py-20">
      <div class="container mx-auto text-center">
        <h1 class="text-5xl font-bold mb-4">{{ $t('welcome') }}</h1>
        <p class="text-xl mb-8">{{ $t('description') }}</p>
        <router-link
          to="/newsletter"
          class="bg-white text-primary px-6 py-3 rounded-lg hover:bg-gray-100"
        >
          {{ $t('subscribe') }}
        </router-link>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  methods: {
    changeLanguage(lang) {
      this.$i18n.locale = lang;
    },
  },
};
</script>

<style>
.hero {
  background-image: url('/path/to/your/image.jpg');
  background-size: cover;
  background-position: center;
}
</style>
