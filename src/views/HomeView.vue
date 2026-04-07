<template>
  <div class="min-h-screen bg-base-100 flex flex-col">
    <Navbar />

    <!-- 主要内容 -->
    <main>
      <!-- 庆祝动画 -->
      <div
        v-if="showCelebration"
        class="fixed inset-0 flex items-center justify-center z-50 pointer-events-none"
      >
        <div class="celebration-animation text-center">
          <div class="text-4xl sm:text-6xl mb-2">🎉</div>
          <div class="text-xl sm:text-2xl font-bold text-primary">
            感谢订阅！
          </div>
        </div>
      </div>

      <!-- Hero Section -->
      <div class="max-w-4xl mx-auto px-4 py-6">
        <!-- 标题和描述 -->
        <div class="text-center mb-6">
          <h1
            class="text-3xl sm:text-4xl font-bold inline-flex flex-wrap justify-center gap-2"
          >
            <span class="text-primary">每日科技新闻</span>
            <span class="text-base-content">用中文读懂全球科技圈</span>
          </h1>

          <p class="text-base text-base-content/80 mt-2">
            每天
            <span class="text-primary font-bold animate-pulse">3 分钟</span
            >，了解最新科技动态。我们精选并翻译全球科技新闻，助你掌握行业脉搏。
          </p>
        </div>

        <!-- 订阅表单 -->
        <div class="max-w-md mx-auto mb-8">
          <div class="flex flex-col gap-3">
            <input
              v-model="email"
              type="email"
              :placeholder="$t('emailPlaceholder')"
              @keyup.enter="handleSubscribe"
              class="input input-md h-12 w-full bg-base-200 border-2 border-primary/20 focus:border-primary transition-all duration-300"
              :class="{ 'input-error': error }"
            />
            <button
              @click="handleSubscribe"
              :disabled="loading"
              class="btn btn-primary btn-md h-12 text-white font-bold relative overflow-hidden group w-full sm:w-auto"
            >
              <span class="relative z-10">{{
                loading ? '订阅中...' : '订阅 (完全免费！)'
              }}</span>
            </button>
          </div>

          <!-- 错误/成功消息和订阅者数量 -->
          <div class="flex flex-col items-center text-center gap-2 mt-2">
            <p
              v-if="message"
              :class="error ? 'text-error' : 'text-success'"
              class="text-sm"
            >
              {{ message }}
            </p>
            <p class="text-base-content/60 text-sm">
              已有
              <span class="font-bold text-primary">{{
                formattedSubscriberCount
              }}</span>
              位读者订阅
            </p>
          </div>
        </div>

        <!-- 特点展示 -->
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4 items-start mb-6">
          <!-- 特点展示 -->
          <div class="col-span-1 flex items-center gap-2">
            <div class="text-2xl">🎯</div>
            <div>
              <h3 class="font-bold text-sm">精选内容</h3>
              <p class="text-base-content/70 text-xs">每日筛选重要科技新闻</p>
            </div>
          </div>

          <div class="col-span-1 flex items-center gap-2">
            <div class="text-2xl">🚀</div>
            <div>
              <h3 class="font-bold text-sm">快速阅读</h3>
              <p class="text-base-content/70 text-xs">3分钟了解科技动态</p>
            </div>
          </div>

          <div class="col-span-1 flex items-center gap-2">
            <div class="text-2xl">💡</div>
            <div>
              <h3 class="font-bold text-sm">深度洞察</h3>
              <p class="text-base-content/70 text-xs">提供专业解读视角</p>
            </div>
          </div>
        </div>

        <!-- 微信扫码部分 -->
        <div class="py-2 rounded-lg">
          <div
            class="flex flex-col md:flex-row items-center justify-center gap-4"
          >
            <img
              src="/assets/扫码_搜索联合传播样式-标准色版.png"
              alt="微信公众号二维码"
              class="w-64 h-auto object-contain"
            />
            <div class="text-center">
              <h3 class="text-lg font-bold text-primary mb-1">
                扫码关注微信公众号
              </h3>
              <p class="text-base-content/70 text-sm">获取每日科技资讯</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 精选新闻栏目 -->
      <div class="max-w-4xl mx-auto px-4 py-1">
        <h2 class="text-2xl font-bold mb-6 text-center">🌟 精选新闻</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 科技公司动态 -->
          <div
            class="card bg-base-200 shadow-xl hover:shadow-2xl transition-all duration-300"
          >
            <a
              :href="featuredNews.company?.url"
              target="_blank"
              class="cursor-pointer"
            >
              <figure class="h-48">
                <img
                  :src="featuredNews.company?.image || 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect width=%22400%22 height=%22300%22 fill=%22%23f3f4f6%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 font-family=%22Arial, sans-serif%22 font-size=%2216%22 fill=%22%239ca3af%22%3E暂无图片%3C/text%3E%3C/svg%3E'"
                  :alt="featuredNews.company?.title"
                  class="w-full h-full object-cover"
                  @error="handleImageError($event, 'company')"
                />
              </figure>
              <div class="card-body p-4">
                <span class="text-xs text-primary font-semibold mb-2"
                  >科技公司动态</span
                >
                <h3
                  class="card-title text-base mb-2 hover:text-primary transition-colors"
                >
                  {{ featuredNews.company?.title }}
                </h3>
                <p class="text-sm text-base-content/70">
                  {{ truncateText(featuredNews.company?.content) }}
                </p>
                <div class="text-xs text-base-content/50 mt-2">
                  {{ featuredNews.company?.date }}
                </div>
              </div>
            </a>
          </div>

          <!-- 科技要闻 -->
          <div
            class="card bg-base-200 shadow-xl hover:shadow-2xl transition-all duration-300"
          >
            <a
              :href="featuredNews.headlines?.url"
              target="_blank"
              class="cursor-pointer"
            >
              <figure class="h-48">
                <img
                  :src="featuredNews.headlines?.image || 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect width=%22400%22 height=%22300%22 fill=%22%23f3f4f6%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 font-family=%22Arial, sans-serif%22 font-size=%2216%22 fill=%22%239ca3af%22%3E暂无图片%3C/text%3E%3C/svg%3E'"
                  :alt="featuredNews.headlines?.title"
                  class="w-full h-full object-cover"
                  @error="handleImageError($event, 'headlines')"
                />
              </figure>
              <div class="card-body p-4">
                <span class="text-xs text-primary font-semibold mb-2"
                  >科技要闻</span
                >
                <h3
                  class="card-title text-base mb-2 hover:text-primary transition-colors"
                >
                  {{ featuredNews.headlines?.title }}
                </h3>
                <p class="text-sm text-base-content/70">
                  {{ truncateText(featuredNews.headlines?.content) }}
                </p>
                <div class="text-xs text-base-content/50 mt-2">
                  {{ featuredNews.headlines?.date }}
                </div>
              </div>
            </a>
          </div>

          <!-- 未来科技 -->
          <div
            class="card bg-base-200 shadow-xl hover:shadow-2xl transition-all duration-300"
          >
            <a
              :href="featuredNews.future?.url"
              target="_blank"
              class="cursor-pointer"
            >
              <figure class="h-48">
                <img
                  :src="featuredNews.future?.image || 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect width=%22400%22 height=%22300%22 fill=%22%23f3f4f6%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 font-family=%22Arial, sans-serif%22 font-size=%2216%22 fill=%22%239ca3af%22%3E暂无图片%3C/text%3E%3C/svg%3E'"
                  :alt="featuredNews.future?.title"
                  class="w-full h-full object-cover"
                  @error="handleImageError($event, 'future')"
                />
              </figure>
              <div class="card-body p-4">
                <span class="text-xs text-primary font-semibold mb-2"
                  >未来科技</span
                >
                <h3
                  class="card-title text-base mb-2 hover:text-primary transition-colors"
                >
                  {{ featuredNews.future?.title }}
                </h3>
                <p class="text-sm text-base-content/70">
                  {{ truncateText(featuredNews.future?.content) }}
                </p>
                <div class="text-xs text-base-content/50 mt-2">
                  {{ featuredNews.future?.date }}
                </div>
              </div>
            </a>
          </div>
        </div>
      </div>

      <LatestArticles />

      <!-- FAQ Section (SEO + GEO) -->
      <div class="max-w-4xl mx-auto px-4 py-8">
        <h2 class="text-2xl font-bold mb-6 text-center">常见问题</h2>
        <div class="space-y-4">
          <div class="collapse collapse-arrow bg-base-200">
            <input type="radio" name="faq-accordion" checked="checked" />
            <div class="collapse-title text-lg font-medium">
              「太长不看」是什么？
            </div>
            <div class="collapse-content">
              <p>
                「太长不看」是一个每日科技新闻中文速递平台，灵感来自英文 TLDR
                Newsletter。我们每天精选全球科技领域最重要的新闻，翻译成中文并提供简明摘要，帮助中文读者快速了解科技行业动态。内容涵盖
                AI 人工智能、编程开发、创业投资、前沿科技等领域。
              </p>
            </div>
          </div>
          <div class="collapse collapse-arrow bg-base-200">
            <input type="radio" name="faq-accordion" />
            <div class="collapse-title text-lg font-medium">
              多久更新一次？
            </div>
            <div class="collapse-content">
              <p>
                我们每个工作日更新一期，通常在北京时间上午发布。每期包含
                15-20
                条精选科技新闻，分为科技公司动态、编程与数据科学、前沿科技、科技要闻等多个板块。
              </p>
            </div>
          </div>
          <div class="collapse collapse-arrow bg-base-200">
            <input type="radio" name="faq-accordion" />
            <div class="collapse-title text-lg font-medium">
              如何订阅每日邮件？
            </div>
            <div class="collapse-content">
              <p>
                在页面顶部输入您的邮箱地址并点击「订阅」按钮即可。订阅完全免费，我们会在每个工作日将最新的科技新闻摘要发送到您的邮箱。您也可以关注我们的微信公众号获取每日推送。
              </p>
            </div>
          </div>
          <div class="collapse collapse-arrow bg-base-200">
            <input type="radio" name="faq-accordion" />
            <div class="collapse-title text-lg font-medium">
              内容来源是什么？
            </div>
            <div class="collapse-content">
              <p>
                我们的内容来源于全球主流科技媒体和行业报道，包括 TechCrunch、The
                Verge、Ars Technica
                等权威来源。我们的编辑团队会筛选最有价值的新闻进行翻译和摘要整理，确保读者能在最短时间内获取最重要的信息。
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 添加 Footer -->
    <Footer />
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import Footer from '../components/Footer.vue';
import LatestArticles from '../components/LatestArticles.vue';
import axios from 'axios';
import { useHead } from '@unhead/vue';

export default {
  name: 'HomeView',
  components: {
    Navbar,
    LatestArticles,
    Footer,
  },
  setup() {
    useHead({
      title: '太长不看 - 每日科技新闻中文速递',
      meta: [
        {
          name: 'description',
          content:
            '每天5分钟掌握全球科技脉搏。太长不看精选并翻译全球科技新闻，涵盖AI、编程、创业、科学等领域。免费订阅每日邮件，用中文读懂全球科技圈。',
        },
        { property: 'og:type', content: 'website' },
        { property: 'og:title', content: '太长不看 - 每日科技新闻中文速递' },
        {
          property: 'og:description',
          content:
            '每天5分钟掌握全球科技脉搏。精选并翻译全球科技新闻，涵盖AI、编程、创业、科学等领域。',
        },
        {
          property: 'og:url',
          content: 'https://tldrnewsletter.cn/',
        },
      ],
      link: [{ rel: 'canonical', href: 'https://tldrnewsletter.cn/' }],
      script: [
        {
          type: 'application/ld+json',
          innerHTML: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: [
              {
                '@type': 'Question',
                name: '「太长不看」是什么？',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: '「太长不看」是一个每日科技新闻中文速递平台，灵感来自英文 TLDR Newsletter。我们每天精选全球科技领域最重要的新闻，翻译成中文并提供简明摘要，帮助中文读者快速了解科技行业动态。',
                },
              },
              {
                '@type': 'Question',
                name: '多久更新一次？',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: '每个工作日更新一期，通常在北京时间上午发布。每期包含15-20条精选科技新闻，分为科技公司动态、编程与数据科学、前沿科技、科技要闻等多个板块。',
                },
              },
              {
                '@type': 'Question',
                name: '如何订阅每日邮件？',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: '在页面顶部输入邮箱地址并点击「订阅」按钮即可。订阅完全免费，每个工作日会将最新的科技新闻摘要发送到您的邮箱。',
                },
              },
              {
                '@type': 'Question',
                name: '内容来源是什么？',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: '内容来源于全球主流科技媒体和行业报道，包括 TechCrunch、The Verge、Ars Technica 等权威来源。编辑团队筛选最有价值的新闻进行翻译和摘要整理。',
                },
              },
            ],
          }),
        },
      ],
    });
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
      featuredNews: {
        company: {
          title: '',
          content: '',
          image: '',
        },
        headlines: {
          title: '',
          content: '',
          image: '',
        },
        future: {
          title: '',
          content: '',
          image: '',
        },
      },
    };
  },
  computed: {
    subscriberMessage() {
      return `加入超过${this.subscriberCount.toLocaleString()}读者的每日推送邮件`;
    },
  },
  async mounted() {
    await this.fetchSubscriberCount();
    await this.fetchFeaturedNews();
  },
  methods: {
    async fetchSubscriberCount() {
      try {
        const API_URL = import.meta.env.VITE_API_URL || '';
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
          const API_URL = import.meta.env.VITE_API_URL || '';
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

    truncateText(text) {
      return text.length > 100 ? text.substring(0, 100) + '...' : text;
    },

    async fetchFeaturedNews() {
      try {
        const API_URL = import.meta.env.VITE_API_URL || '';
        const response = await axios.get(`${API_URL}/api/featured-news`);
        if (response.data.success) {
          this.featuredNews = response.data.featuredNews;
        }
      } catch (error) {
        console.error('Error fetching featured news:', error);
      }
    },

    handleImageError(event, category) {
      // 当图片加载失败时，使用一个透明的 placeholder
      // 使用 1x1 透明 PNG 的 base64 编码
      event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="400" height="300" fill="%23f3f4f6"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="%239ca3af"%3E图片加载失败%3C/text%3E%3C/svg%3E';
      console.log(`Image load error for ${category}:`, event.target.alt);
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

<style scoped>
@keyframes bounce-slow {
  0%,
  100% {
    transform: translateY(-1%);
  }
  50% {
    transform: translateY(1%);
  }
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

.card {
  @apply transition-all duration-300;
}

.card:hover {
  @apply transform -translate-y-1;
}

.card figure img {
  @apply transition-transform duration-300;
}

.card:hover figure img {
  @apply transform scale-105;
}

/* 添加水平弹跳动画 */
@keyframes bounce-x {
  0%,
  100% {
    transform: translateX(25%) rotate(180deg);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: translateX(0) rotate(180deg);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}

.animate-bounce-x {
  animation: bounce-x 1s infinite;
}

/* 按钮悬停效果 */
.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow:
    0 4px 6px -1px rgb(0 0 0 / 0.1),
    0 2px 4px -2px rgb(0 0 0 / 0.1);
}

/* 脉冲动画增强 */
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}
</style>
