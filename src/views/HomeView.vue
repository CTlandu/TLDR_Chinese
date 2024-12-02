<template>
  <div>
    <Navbar />
    <!-- 庆祝动画 -->
    <div
      v-if="showCelebration"
      class="fixed inset-0 flex items-center justify-center z-50 pointer-events-none"
    >
      <div class="celebration-animation text-center">
        <div class="text-4xl sm:text-6xl mb-2">🎉</div>
        <div class="text-xl sm:text-2xl font-bold text-primary">感谢订阅！</div>
      </div>
    </div>

    <!-- Hero Section -->
    <section class="bg-base-300 text-base-content py-4 sm:py-8">
      <div class="container mx-auto text-center px-4">
        <!-- 响应式标题 -->
        <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 sm:mb-6">
          <span
            class="text-4xl sm:text-5xl lg:text-6xl text-primary animate-pulse"
          >
            {{ $t('number') }}
          </span>
          {{ $t('welcomePrefix') }}
          <span class="whitespace-normal sm:whitespace-nowrap">
            {{ $t('welcomeSuffix') }}
            <span class="text-2xl sm:text-4xl">💓</span>
            <span class="text-2xl sm:text-4xl">💻</span>
          </span>
        </h1>

        <!-- 响应式描述文本 -->
        <p class="text-base sm:text-xl mb-8 sm:mb-12 max-w-2xl mx-auto px-4">
          <span class="text-primary font-bold">{{ $t('free') }}</span>
          {{ $t('descriptionPrefix') }}
          <br class="hidden sm:block" />
          {{ $t('descriptionSuffix') }}
        </p>

        <!-- 订阅表单 -->
        <div
          class="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-2xl mx-auto px-4"
        >
          <input
            v-model="email"
            type="email"
            :placeholder="$t('emailPlaceholder')"
            @keyup.enter="handleSubscribe"
            class="input input-bordered input-lg w-full max-w-lg text-base sm:text-lg border-primary shadow-lg hover:shadow-primary/50 transition-all duration-300 animate-bounce-slow focus:animate-none"
            :class="{ 'input-error': error }"
          />
          <button
            @click="handleSubscribe"
            :disabled="loading"
            class="btn btn-primary btn-lg text-base sm:text-lg w-full sm:w-auto sm:min-w-[200px] hover:scale-105 transition-transform"
          >
            {{ loading ? '订阅中...' : $t('subscribe') }}
          </button>
        </div>

        <!-- 消息提示 -->
        <div v-if="message" class="mt-4 text-center px-4">
          <div
            :class="error ? 'text-error' : 'text-success'"
            class="text-sm sm:text-base"
          >
            {{ message }}
          </div>
        </div>

        <!-- 订阅者数量 -->
        <p class="mt-6 sm:mt-8 text-base sm:text-lg opacity-75 px-4">
          加入超过
          <span
            class="font-bold text-primary transition-all duration-500"
            :class="{ 'animate-number': isCountAnimating }"
          >
            {{ formattedSubscriberCount }}
          </span>
          读者的每日推送邮件
        </p>
      </div>
    </section>

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
      subscriberCount: 5000, // 默认值
      showCelebration: false,
      isCountAnimating: false,
      formattedSubscriberCount: '5,000',
    };
  },
  computed: {
    subscriberMessage() {
      return `加入超过${this.subscriberCount.toLocaleString()}读者的每日推送邮件`;
    },
  },
  async mounted() {
    await this.fetchSubscriberCount();
  },
  methods: {
    async fetchSubscriberCount() {
      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
        const response = await axios.get(`${API_URL}/api/subscriber-count`);
        if (response.data.success) {
          this.subscriberCount = response.data.count;
        }
      } catch (error) {
        console.error('Error fetching subscriber count:', error);
        // 如果获取失败，保持默认值 5000
      }
    },
    async handleSubscribe() {
      try {
        // 基本的邮箱格式验证
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!this.email || !emailRegex.test(this.email)) {
          this.showMessage('请输入有效的邮箱地址', true);
          return;
        }

        this.loading = true;
        this.message = '';
        this.error = false;

        try {
          const API_URL =
            import.meta.env.VITE_API_URL || 'http://localhost:5000';
          const response = await axios.post(`${API_URL}/api/subscribe`, {
            email: this.email.toLowerCase().trim(),
          });

          this.showMessage(response.data.message);
          this.email = '';

          // 显示庆祝动画
          this.showCelebration = true;
          setTimeout(() => {
            this.showCelebration = false;
          }, 2000);

          // 更新并动画显示新的订阅者数量
          await this.animateSubscriberCount();
        } catch (error) {
          console.error('Error:', error);
          this.showMessage(
            error.response?.data?.error || '订阅失败，请稍后重试',
            true
          );
        } finally {
          this.loading = false;
        }
      } catch (error) {
        console.error('Error:', error);
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

    async animateSubscriberCount() {
      const oldCount = this.subscriberCount;
      const newCount = oldCount + 1;

      // 开始动画
      this.isCountAnimating = true;

      // 使用 requestAnimationFrame 实现平滑计数动画
      const startTime = performance.now();
      const duration = 1000; // 1秒动画

      const animate = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // 使用 easeOut 效果
        const easeProgress = 1 - Math.pow(1 - progress, 3);

        const currentCount = Math.floor(
          oldCount + (newCount - oldCount) * easeProgress
        );
        this.formattedSubscriberCount = currentCount.toLocaleString();

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          this.subscriberCount = newCount;
          this.isCountAnimating = false;
        }
      };

      requestAnimationFrame(animate);
    },
  },
  watch: {
    subscriberCount: {
      immediate: true,
      handler(newValue) {
        this.formattedSubscriberCount = newValue.toLocaleString();
      },
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

.celebration-animation {
  animation: celebrate 2s ease-out forwards;
}

@keyframes celebrate {
  0% {
    transform: scale(0.5) translateY(100px);
    opacity: 0;
  }
  20% {
    transform: scale(1.2) translateY(0);
    opacity: 1;
  }
  80% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
  100% {
    transform: scale(1.1) translateY(-20px);
    opacity: 0;
  }
}

.animate-number {
  animation: pulse 0.5s ease-in-out;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
    color: theme('colors.primary');
  }
  100% {
    transform: scale(1);
  }
}

/* 确保动画元素在最上层 */
.fixed {
  position: fixed;
  z-index: 9999;
}

.recaptcha-container {
  margin: 1rem 0;
  display: flex;
  justify-content: center;
}
</style>
