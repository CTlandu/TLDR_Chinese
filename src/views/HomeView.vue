<template>
  <div class="min-h-screen bg-base-100 flex flex-col">
    <Navbar />

    <main class="flex-1">
      <!-- 庆祝动画（保留，收敛） -->
      <div
        v-if="showCelebration"
        class="fixed inset-0 flex items-center justify-center z-[70] pointer-events-none"
      >
        <div class="celebration-animation rounded-lg bg-base-200/95 border border-white/10 px-6 py-4 text-center shadow-2xl">
          <div class="text-lg font-bold text-primary">感谢订阅！</div>
        </div>
      </div>

      <!-- Hero -->
      <section class="max-w-content mx-auto w-full px-4 sm:px-6 pt-10 sm:pt-12 pb-8">
        <h1
          class="text-3xl sm:text-4xl md:text-[42px] font-extrabold leading-[1.15] tracking-tight text-base-content"
        >
          每天 5 分钟，跟上全球科技
        </h1>
        <p class="mt-3 max-w-2xl text-base sm:text-lg text-base-content/60">
          免费的中文科技日报，精选并翻译 AI、大厂、开发者领域最重要的英文新闻。
        </p>

        <!-- 订阅表单 -->
        <div id="subscribe" class="mt-6 flex max-w-xl flex-col gap-3 sm:flex-row">
          <input
            v-model="email"
            type="email"
            :placeholder="$t('emailPlaceholder')"
            @keyup.enter="handleSubscribe"
            class="h-12 flex-1 rounded border-0 bg-white px-4 text-neutral-900 placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            @click="handleSubscribe"
            :disabled="loading"
            class="btn btn-primary h-12 min-h-0 shrink-0 px-6 text-base font-bold text-white"
          >
            {{ loading ? '订阅中...' : '免费订阅' }}
          </button>
        </div>

        <p
          v-if="message"
          :class="error ? 'text-error' : 'text-success'"
          class="mt-2 text-sm"
        >
          {{ message }}
        </p>

        <!-- 社会证明 -->
        <p class="mt-3 text-sm text-base-content/50">
          已有
          <span class="font-bold text-base-content">{{ formattedSubscriberCount }}</span>
          位读者订阅 · 每日一封 · 随时退订 ·
          <a
            href="https://mp.weixin.qq.com/s/8k55rjuc4GCsYlrD_i5n3A"
            target="_blank"
            rel="noopener"
            class="text-accent hover:underline"
          >
            微信公众号同步更新
          </a>
        </p>
      </section>

      <!-- 头条大卡 + 侧栏 -->
      <section
        v-if="featuredMain"
        class="max-w-content mx-auto w-full px-4 sm:px-6 pb-12"
      >
        <div class="grid gap-6 lg:grid-cols-3">
          <!-- 头条大卡 -->
          <a
            :href="featuredMain.url"
            target="_blank"
            rel="noopener"
            class="group flex flex-col overflow-hidden rounded-lg border border-white/5 bg-base-200 transition-colors hover:border-white/15 lg:col-span-2"
          >
            <div class="aspect-[16/9] overflow-hidden bg-base-300">
              <img
                v-if="featuredMain.image_url && !failed[featuredMain.url]"
                :src="featuredMain.image_url"
                :alt="featuredMain.title"
                class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.02]"
                @error="onImgError(featuredMain.url)"
              />
              <div
                v-else
                class="flex h-full w-full items-center justify-center text-sm text-base-content/20"
              >
                暂无配图
              </div>
            </div>
            <div class="p-5">
              <div class="mb-2 text-xs font-semibold text-accent">
                {{ featuredMain.relative_time }}
                <span class="text-base-content/25">·</span>
                {{ $t('sections.Big Tech & Startups') }}
              </div>
              <h2
                class="text-xl font-extrabold leading-snug text-base-content transition-colors group-hover:text-primary sm:text-2xl"
              >
                {{ zhTitle(featuredMain) }}
              </h2>
              <p
                v-if="enTitle(featuredMain)"
                class="mt-1.5 text-sm text-base-content/40"
              >
                {{ enTitle(featuredMain) }}
              </p>
              <p class="mt-3 line-clamp-3 text-sm text-base-content/60 sm:text-base">
                {{ featuredMain.content }}
              </p>
            </div>
          </a>

          <!-- 侧栏文章列表 -->
          <div class="flex flex-col">
            <a
              v-for="item in featuredSide"
              :key="item.url"
              :href="item.url"
              target="_blank"
              rel="noopener"
              class="group flex gap-3 border-b border-white/5 py-4 first:pt-0 last:border-0"
            >
              <div class="min-w-0 flex-1">
                <div class="mb-1 text-xs font-semibold text-accent">
                  {{ item.relative_time }}
                  <span class="text-base-content/25">·</span>
                  {{ $t('sections.' + item._section) }}
                </div>
                <h3
                  class="line-clamp-2 text-sm font-bold leading-snug text-base-content transition-colors group-hover:text-primary"
                >
                  {{ zhTitle(item) }}
                </h3>
                <p
                  v-if="enTitle(item)"
                  class="mt-1 line-clamp-1 text-xs text-base-content/40"
                >
                  {{ enTitle(item) }}
                </p>
              </div>
              <div class="h-20 w-20 shrink-0 overflow-hidden rounded bg-base-300">
                <img
                  v-if="item.image_url && !failed[item.url]"
                  :src="item.image_url"
                  :alt="item.title"
                  loading="lazy"
                  class="h-full w-full object-cover"
                  @error="onImgError(item.url)"
                />
              </div>
            </a>
          </div>
        </div>
      </section>

      <!-- 更多新闻（按分类分组） -->
      <LatestArticles :sections="sections" :en-map="enMap" />

      <!-- 微信公众号（安静的小区块） -->
      <section class="max-w-content mx-auto w-full px-4 sm:px-6 pb-12">
        <div
          class="flex max-w-md items-center gap-4 rounded-lg border border-white/5 bg-base-200 p-4 sm:p-5"
        >
          <img
            :src="wechatQr"
            alt="太长不看微信公众号二维码"
            class="h-20 w-20 shrink-0 rounded bg-white object-contain p-1"
          />
          <div>
            <h3 class="font-bold text-base-content">微信公众号同步更新</h3>
            <p class="mt-1 text-sm text-base-content/50">
              扫码关注「太长不看」，每日科技资讯推送到微信。
            </p>
          </div>
        </div>
      </section>

      <!-- FAQ（SEO / GEO，保留结构化数据） -->
      <section class="max-w-content mx-auto w-full px-4 sm:px-6 pb-16">
        <h2 class="mb-6 text-2xl font-extrabold text-base-content">常见问题</h2>
        <div class="max-w-3xl space-y-3">
          <div class="collapse collapse-arrow border border-white/5 bg-base-200">
            <input type="radio" name="faq-accordion" checked="checked" />
            <div class="collapse-title font-bold">「太长不看」是什么？</div>
            <div class="collapse-content text-sm text-base-content/70">
              <p>
                「太长不看」是一个每日科技新闻中文速递平台，灵感来自英文 TLDR
                Newsletter。我们每天精选全球科技领域最重要的新闻，翻译成中文并提供简明摘要，帮助中文读者快速了解科技行业动态。内容涵盖
                AI 人工智能、编程开发、创业投资、前沿科技等领域。
              </p>
            </div>
          </div>
          <div class="collapse collapse-arrow border border-white/5 bg-base-200">
            <input type="radio" name="faq-accordion" />
            <div class="collapse-title font-bold">多久更新一次？</div>
            <div class="collapse-content text-sm text-base-content/70">
              <p>
                我们每个工作日更新一期，通常在北京时间上午发布。每期包含 15-20
                条精选科技新闻，分为科技公司动态、编程与数据科学、前沿科技、科技要闻等多个板块。
              </p>
            </div>
          </div>
          <div class="collapse collapse-arrow border border-white/5 bg-base-200">
            <input type="radio" name="faq-accordion" />
            <div class="collapse-title font-bold">如何订阅每日邮件？</div>
            <div class="collapse-content text-sm text-base-content/70">
              <p>
                在页面顶部输入您的邮箱地址并点击「免费订阅」按钮即可。订阅完全免费，我们会在每个工作日将最新的科技新闻摘要发送到您的邮箱。您也可以关注我们的微信公众号获取每日推送。
              </p>
            </div>
          </div>
          <div class="collapse collapse-arrow border border-white/5 bg-base-200">
            <input type="radio" name="faq-accordion" />
            <div class="collapse-title font-bold">内容来源是什么？</div>
            <div class="collapse-content text-sm text-base-content/70">
              <p>
                我们的内容来源于全球主流科技媒体和行业报道，包括 TechCrunch、The
                Verge、Ars Technica
                等权威来源。我们的编辑团队会筛选最有价值的新闻进行翻译和摘要整理，确保读者能在最短时间内获取最重要的信息。
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>

    <Footer />
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import Footer from '../components/Footer.vue';
import LatestArticles from '../components/LatestArticles.vue';
import axios from 'axios';
import { useHead } from '@unhead/vue';
import wechatQr from '../../assets/太长不看-qr code.jpg';
import { stripLeadingEmoji, stripReadingTime } from '../utils/text';

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
      subscriberCount: 5000,
      showCelebration: false,
      formattedSubscriberCount: '5,000',
      sections: {},
      enMap: {},
      failed: {},
      wechatQr,
    };
  },
  computed: {
    featuredMain() {
      const list = this.sections['Big Tech & Startups'];
      return Array.isArray(list) && list.length ? list[0] : null;
    },
    featuredSide() {
      const keys = [
        'Programming, Design & Data Science',
        'Science & Futuristic Technology',
        'Miscellaneous',
        'Quick Links',
      ];
      return keys
        .map((k) => {
          const list = this.sections[k];
          return Array.isArray(list) && list.length
            ? { ...list[0], _section: k }
            : null;
        })
        .filter(Boolean);
    },
  },
  async mounted() {
    await Promise.all([
      this.fetchSubscriberCount(),
      this.fetchSections(),
      this.fetchEnglishTitles(),
    ]);
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
      }
    },
    async fetchSections() {
      try {
        const API_URL = import.meta.env.VITE_API_URL || '';
        const response = await axios.get(
          `${API_URL}/api/latest-articles-by-section`
        );
        this.sections = response.data || {};
      } catch (error) {
        console.error('Error fetching sections:', error);
      }
    },
    async fetchEnglishTitles() {
      // latest-articles 带有英文原标题，用 url 关联，为卡片补上克制的双语原标题
      try {
        const API_URL = import.meta.env.VITE_API_URL || '';
        const response = await axios.get(`${API_URL}/api/latest-articles`);
        const map = {};
        for (const section of response.data?.sections || []) {
          for (const a of section.articles || []) {
            if (a.url && a.title_en) {
              map[a.url] = a.title_en
                .replace(/\s*\(\d+\s*minute read\)\s*$/i, '')
                .trim();
            }
          }
        }
        this.enMap = map;
      } catch (error) {
        console.error('Error fetching english titles:', error);
      }
    },
    async handleSubscribe() {
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

        this.showCelebration = true;
        setTimeout(() => {
          this.showCelebration = false;
        }, 1800);

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
    },

    showMessage(msg, isError = false) {
      this.message = msg;
      this.error = isError;
      setTimeout(() => {
        this.message = '';
        this.error = false;
      }, 5000);
    },

    async animateSubscriberCount() {
      const oldCount = this.subscriberCount;
      const newCount = oldCount + 1;
      const startTime = performance.now();
      const duration = 1000;

      const animate = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const currentCount = Math.floor(
          oldCount + (newCount - oldCount) * easeProgress
        );
        this.formattedSubscriberCount = currentCount.toLocaleString();

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          this.subscriberCount = newCount;
        }
      };

      requestAnimationFrame(animate);
    },

    onImgError(url) {
      this.failed[url] = true;
    },

    zhTitle(article) {
      return stripLeadingEmoji(article?.title || '');
    },

    enTitle(article) {
      if (!article) return '';
      const direct = stripReadingTime(article.title_en || '');
      if (direct) return direct;
      return this.enMap[article.url] || '';
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
.celebration-animation {
  animation: celebrate 1.8s ease-out forwards;
}

@keyframes celebrate {
  0% {
    transform: scale(0.9) translateY(10px);
    opacity: 0;
  }
  15% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
  85% {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
  100% {
    transform: scale(1) translateY(-10px);
    opacity: 0;
  }
}
</style>
