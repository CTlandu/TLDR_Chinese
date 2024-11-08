<template>
  <div>
    <!-- Navbar -->
    <Navbar />
    <!-- Hero Section -->
    <section class="hero bg-primary text-white py-20">
      <div class="container mx-auto text-center">
        <h1 class="text-5xl font-bold mb-4">{{ $t('welcome') }}</h1>
        <p class="text-xl mb-8">{{ $t('description') }}</p>
        <input
          type="email"
          placeholder="Email Address"
          class="px-4 py-2 rounded-lg text-gray-800"
        />
        <button
          class="bg-purple-600 text-white px-6 py-2 rounded-lg ml-2 hover:bg-purple-700"
        >
          {{ $t('subscribe') }}
        </button>
        <p class="mt-4 text-sm">Join 1,250,000 readers for one daily email</p>
      </div>
    </section>
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';

export default {
  name: 'HomeView',
  components: {
    Navbar,
  },
  methods: {
    changeLanguage(lang) {
      this.$i18n.locale = lang;
    },
  },
};
</script>

<style>
.hero {
  background-image: url('https://via.placeholder.com/1500x500?text=Tech+Image');
  background-size: cover;
  background-position: center;
}
</style>
