<template>
  <ErrorBoundary @retry="fetchData">
    <div class="min-h-screen bg-base-100 flex flex-col">
      <Navbar />

      <main class="flex-grow">
        <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
          <h1 class="text-2xl sm:text-3xl font-bold text-center mb-4 sm:mb-8">
            {{ newsletter?.generated_title || '今日科技要闻速递' }}【<time
              :datetime="currentDate"
              >{{ currentDate }}</time
            >】
          </h1>

          <div
            v-if="loading"
            class="flex flex-col items-center justify-center min-h-[200px] sm:min-h-[300px]"
          >
            <span
              class="loading loading-spinner loading-lg text-primary"
            ></span>
            <p class="mt-4 text-base sm:text-lg">正在获取内容，请稍候...</p>
          </div>

          <div v-else>
            <section
              v-for="section in articles"
              :key="section.section"
              :aria-label="section.section"
              class="mb-8 sm:mb-12"
            >
              <h2
                class="divider text-xl sm:text-2xl font-bold break-words max-w-full px-2 sm:px-4"
              >
                {{ section.section }}
              </h2>

              <article
                v-for="article in section.articles"
                :key="article.url"
                class="card bg-base-200 shadow-xl mb-4 sm:mb-8"
              >
                <div class="card-body p-4 sm:p-6">
                  <h3 class="card-title text-base sm:text-lg md:text-xl">
                    <a
                      :href="article.url"
                      target="_blank"
                      rel="noopener"
                      class="link link-primary hover:underline"
                    >
                      {{ article.title }}
                    </a>
                  </h3>
                  <p class="italic text-sm sm:text-base text-base-content/70">
                    {{ article.title_en }}
                  </p>

                  <div v-if="article.image_url" class="my-2 sm:my-4">
                    <img
                      :src="article.image_url"
                      :alt="article.title"
                      loading="lazy"
                      width="672"
                      height="192"
                      class="rounded-lg w-full max-w-2xl mx-auto h-32 sm:h-48 object-cover"
                      @error="handleImageError($event, article)"
                    />
                  </div>

                  <div class="space-y-2 sm:space-y-4 mt-2 sm:mt-4">
                    <div
                      class="prose prose-sm sm:prose-base lg:prose-lg max-w-none"
                      v-html="article.content"
                    ></div>
                    <a
                      :href="article.url"
                      target="_blank"
                      rel="noopener"
                      class="link link-hover text-xs sm:text-sm hover:underline block"
                    >
                      (阅读更多)
                    </a>
                    <div class="bg-base-300 text-base-content rounded-lg">
                      <div
                        class="p-3 sm:p-4 text-sm sm:text-base"
                        v-html="article.content_en"
                      ></div>
                    </div>
                  </div>
                </div>
              </article>
            </section>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  </ErrorBoundary>
</template>

<script>
import axios from 'axios';
import { computed, ref } from 'vue';
import { useHead } from '@unhead/vue';
import ErrorBoundary from '../components/ErrorBoundary.vue';
import Navbar from '../components/Navbar.vue';
import Footer from '../components/Footer.vue';

export default {
  name: 'NewsletterView',
  components: {
    ErrorBoundary,
    Navbar,
    Footer,
  },
  setup() {
    const newsletterData = ref(null);
    const currentDateRef = ref('');
    const articlesRef = ref([]);

    const firstArticleDesc = computed(() => {
      if (!articlesRef.value.length) return '';
      const firstSection = articlesRef.value[0];
      if (!firstSection?.articles?.length) return '';
      const text = firstSection.articles[0].content || '';
      const stripped = text.replace(/<[^>]*>/g, '');
      return stripped.substring(0, 150);
    });

    useHead({
      title: computed(
        () =>
          `${newsletterData.value?.generated_title || '今日科技要闻速递'}【${currentDateRef.value}】| 太长不看`
      ),
      meta: [
        {
          name: 'description',
          content: computed(
            () =>
              firstArticleDesc.value ||
              '太长不看每日科技新闻速递，涵盖AI、编程、创业、科学等领域。'
          ),
        },
        { property: 'og:type', content: 'article' },
        {
          property: 'og:title',
          content: computed(
            () =>
              `${newsletterData.value?.generated_title || '今日科技要闻速递'}【${currentDateRef.value}】`
          ),
        },
        {
          property: 'og:description',
          content: computed(
            () =>
              firstArticleDesc.value ||
              '太长不看每日科技新闻速递'
          ),
        },
        {
          property: 'og:url',
          content: computed(
            () =>
              `https://tldrnewsletter.cn/newsletter/${currentDateRef.value}`
          ),
        },
        {
          property: 'article:published_time',
          content: computed(() => currentDateRef.value),
        },
      ],
      link: [
        {
          rel: 'canonical',
          href: computed(
            () =>
              `https://tldrnewsletter.cn/newsletter/${currentDateRef.value}`
          ),
        },
      ],
      script: [
        {
          type: 'application/ld+json',
          innerHTML: computed(() => {
            if (!articlesRef.value.length || !currentDateRef.value) return '{}';
            const items = [];
            let position = 1;
            for (const section of articlesRef.value) {
              for (const article of section.articles || []) {
                items.push({
                  '@type': 'ListItem',
                  position: position++,
                  item: {
                    '@type': 'NewsArticle',
                    headline: article.title,
                    alternativeHeadline: article.title_en,
                    description: (article.content || '').replace(/<[^>]*>/g, '').substring(0, 200),
                    url: article.url,
                    image: article.image_url || undefined,
                    datePublished: currentDateRef.value,
                    inLanguage: 'zh-CN',
                    publisher: {
                      '@type': 'Organization',
                      name: '太长不看',
                      url: 'https://tldrnewsletter.cn',
                    },
                  },
                });
              }
            }
            return JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'ItemList',
              name: newsletterData.value?.generated_title || '今日科技要闻速递',
              itemListElement: items,
            });
          }),
        },
      ],
    });

    return { newsletterData, currentDateRef, articlesRef };
  },
  data() {
    return {
      currentDate: '',
      articles: [],
      loading: false,
      newsletter: null,
    };
  },
  methods: {
    async fetchData(date) {
      this.loading = true;
      try {
        // 使用相对路径，Vercel 会自动路由到后端
        const API_URL = import.meta.env.VITE_API_URL || '';

        const dateParam = date || this.$route.params.date || 'latest';
        const response = await axios.get(
          `${API_URL}/api/newsletter/${dateParam}`,
          {
            withCredentials: false,
            headers: {
              'Content-Type': 'application/json',
              Accept: 'application/json',
            },
          }
        );
        this.articles = response.data.sections;
        this.currentDate = response.data.currentDate;
        this.newsletter = response.data;
        // Sync with setup refs for dynamic meta tags
        this.articlesRef = response.data.sections;
        this.currentDateRef = response.data.currentDate;
        this.newsletterData = response.data;
      } catch (error) {
        console.error('Error details:', error);
        this.articles = [];
        this.error = '获取数据失败：' + error.message;
      } finally {
        this.loading = false;
      }
    },
    handleImageError(event, article) {
      event.target.style.display = 'none';
      article.image_url = null;
    },
  },
  watch: {
    $route: {
      handler(to, from) {
        const newDate = to.params.date;
        if (newDate) {
          this.fetchData(newDate);
        }
      },
    },
  },
  mounted() {
    this.fetchData(this.$route.params.date);
  },
};
</script>

<style>
/* 只保留必要的自定义样式，其他都用 Tailwind 类替代 */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
