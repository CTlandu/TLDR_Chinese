<template>
  <ErrorBoundary @retry="fetchData">
    <div class="min-h-screen bg-base-100">
      <Navbar />
      <div class="max-w-3xl mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-center mb-8">
          TLDR每日科技新闻【{{ currentDate }}】
        </h1>

        <!-- 加载状态 -->
        <div
          v-if="loading"
          class="flex flex-col items-center justify-center min-h-[300px]"
        >
          <span class="loading loading-spinner loading-lg text-primary"></span>
          <p class="mt-4 text-lg">正在获取内容，请稍候...</p>
        </div>

        <!-- 内容区域 -->
        <div v-else>
          <div v-for="section in articles" :key="section.section" class="mb-12">
            <div class="divider text-2xl font-bold">{{ section.section }}</div>

            <div
              v-for="article in section.articles"
              :key="article.url"
              class="card bg-base-200 shadow-xl mb-8"
            >
              <div class="card-body">
                <h2 class="card-title">
                  <a
                    :href="article.url"
                    target="_blank"
                    class="link link-primary"
                  >
                    {{ article.title }}
                  </a>
                </h2>
                <p class="italic text-base-content/70">
                  {{ article.title_en }}
                </p>

                <div v-if="article.image_url" class="my-4">
                  <img
                    :src="article.image_url"
                    :alt="article.title"
                    class="rounded-lg w-full max-w-2xl mx-auto h-48 object-cover"
                    @error="handleImageError($event, article)"
                  />
                </div>

                <div class="space-y-4 mt-4">
                  <div
                    class="prose prose-invert text-lg"
                    v-html="article.content"
                  ></div>
                  <a
                    :href="article.url"
                    target="_blank"
                    class="link link-hover text-sm hover:underline"
                  >
                    (阅读更多)
                  </a>
                  <div class="bg-base-300 text-base-content">
                    <div class="p-4" v-html="article.content_en"></div>
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
        this.articles = response.data.articles;
        this.currentDate = response.data.currentDate;
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
