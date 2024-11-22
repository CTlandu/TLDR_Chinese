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
            v-model="email"
            type="email"
            :placeholder="$t('emailPlaceholder')"
            @keyup.enter="handleSubscribe"
            class="input input-bordered input-lg w-full max-w-lg text-lg border-primary shadow-lg hover:shadow-primary/50 transition-all duration-300 animate-bounce-slow focus:animate-none"
            :class="{ 'input-error': error }"
          />
          <button
            @click="handleSubscribe"
            :disabled="loading"
            class="btn btn-primary btn-lg text-lg min-w-[200px] hover:scale-105 transition-transform"
          >
            {{ loading ? '订阅中...' : $t('subscribe') }}
          </button>
        </div>

        <div v-if="message" class="mt-4 text-center">
          <div :class="error ? 'text-error' : 'text-success'">
            {{ message }}
          </div>
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
import axios from 'axios';

export default {
  name: 'HomeView',
  components: {
    Navbar,
    LatestArticles,
  },
  data() {
    return {
      email: '',
      loading: false,
      message: '',
      error: false,
    };
  },
  methods: {
    changeLanguage(lang) {
      this.$i18n.locale = lang;
    },
    async handleSubscribe() {
      if (!this.email) {
        this.showMessage('请输入邮箱地址', true);
        return;
      }

      this.loading = true;
      this.message = '';
      this.error = false;

      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
        console.log('Using API URL:', API_URL);

        const normalizedEmail = this.email.toLowerCase().trim();

        const response = await axios.post(`${API_URL}/api/subscribe`, {
          email: normalizedEmail,
        });

        console.log('Response:', response.data);
        this.showMessage(response.data.message);
        this.email = ''; // 清空输入框
      } catch (error) {
        console.error('Error details:', error);
        this.showMessage(
          error.response?.data?.error || '订阅失败，请稍后重试',
          true
        );
      } finally {
        this.loading = false;
      }
    },

    showMessage(msg, isError = false) {
      this.message = msg;
      this.error = isError;

      // 3秒后清除消息
      setTimeout(() => {
        this.message = '';
        this.error = false;
      }, 5000);
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
