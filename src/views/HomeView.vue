<template>
  <div>
    <!-- Navbar -->
    <Navbar />
    <!-- Hero Section -->
    <section class="bg-base-300 text-base-content py-24">
      <div class="container mx-auto text-center px-4">
        <h1 class="text-5xl font-bold mb-6">
          <span class="text-6xl text-primary animate-pulse">{{
            $t('number')
          }}</span>
          {{ $t('welcomePrefix') }}
          <span class="whitespace-nowrap">
            {{ $t('welcomeSuffix') }}
            <span class="text-4xl">💓</span>
            <span class="text-4xl">💻</span>
          </span>
        </h1>

        <p class="text-xl mb-12 max-w-2xl mx-auto">
          <span class="text-primary font-bold">{{ $t('free') }}</span>
          {{ $t('descriptionPrefix') }}
          <br />
          {{ $t('descriptionSuffix') }}
        </p>

        <div
          class="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-2xl mx-auto"
        >
          <input
            type="email"
            :placeholder="$t('emailPlaceholder')"
            class="input input-bordered input-lg w-full max-w-lg text-lg border-primary shadow-lg hover:shadow-primary/50 transition-all duration-300 animate-bounce-slow focus:animate-none"
          />
          <button
            class="btn btn-primary btn-lg text-lg min-w-[200px] hover:scale-105 transition-transform"
          >
            {{ $t('subscribe') }}
          </button>
        </div>

        <p class="mt-8 text-lg opacity-75">
          {{ $t('joinCommunity') }}
        </p>
      </div>
    </section>

    <!-- Latest Articles Section -->
    <LatestArticles />
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import LatestArticles from '../components/LatestArticles.vue';

export default {
  name: 'HomeView',
  components: {
    Navbar,
    LatestArticles,
  },
  methods: {
    changeLanguage(lang) {
      this.$i18n.locale = lang;
    },
  },
};
</script>

<style>
@keyframes bounce-slow {
  0%,
  100% {
    transform: translateY(-1%);
  }
  50% {
    transform: translateY(1%);
  }
}

.animate-bounce-slow {
  animation: bounce-slow 2s infinite;
}

.input:focus {
  outline: none;
  border-color: theme('colors.primary');
  box-shadow: 0 0 0 2px theme('colors.primary' / 20%);
}
</style>
