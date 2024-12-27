<template>
  <ErrorBoundary @retry="fetchData">
    <div class="min-h-screen bg-base-100">
      <Navbar />
      <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-center mb-4 sm:mb-8">
          {{ newsletter?.generated_title || '今日科技要闻速递' }}【{{
            currentDate
          }}】
        </h1>

        <div
          v-if="loading"
          class="flex flex-col items-center justify-center min-h-[200px] sm:min-h-[300px]"
        >
          <span class="loading loading-spinner loading-lg text-primary"></span>
          <p class="mt-4 text-base sm:text-lg">正在获取内容，请稍候...</p>
        </div>

        <div v-else>
          <div
            v-for="section in articles"
            :key="section.section"
            class="mb-8 sm:mb-12"
          >
            <div
              class="divider text-xl sm:text-2xl font-bold break-words max-w-full px-2 sm:px-4"
            >
              {{ section.section }}
            </div>

            <div
              v-for="article in section.articles"
              :key="article.url"
              class="card bg-base-200 shadow-xl mb-4 sm:mb-8"
            >
              <div class="card-body p-4 sm:p-6">
                <h2 class="card-title text-base sm:text-lg md:text-xl">
                  <a
                    :href="article.url"
                    target="_blank"
                    class="link link-primary hover:underline"
                  >
                    {{ article.title }}
                  </a>
                </h2>
                <p class="italic text-sm sm:text-base text-base-content/70">
                  {{ article.title_en }}
                </p>

                <div v-if="article.image_url" class="my-2 sm:my-4">
                  <img
                    :src="article.image_url"
                    :alt="article.title"
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
            </div>
          </div>
        </div>
      </div>
    </div>
  </ErrorBoundary>
</template>

<script>
import axios from 'axios';
import ErrorBoundary from '../components/ErrorBoundary.vue';
import Navbar from '../components/Navbar.vue';

export default {
  name: 'NewsletterView',
  components: {
    ErrorBoundary,
    Navbar,
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
        const API_URL =
          window.location.hostname === 'localhost'
            ? 'http://localhost:5000'
            : 'https://tldr-chinese-backend.onrender.com';

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
      immediate: true,
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
