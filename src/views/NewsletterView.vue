<template>
  <ErrorBoundary @retry="fetchData">
    <div>
      <!-- Navbar -->
      <Navbar />

      <div class="max-w-3xl mx-auto px-4 py-8">
        <!-- 日期选择器已移除 -->

        <h1 class="text-3xl font-bold text-center text-gray-800 mb-8">
          TLDR每日科技新闻【{{ currentDate }}】
        </h1>

        <!-- 加载状态 -->
        <div
          v-if="loading"
          class="flex flex-col items-center justify-center min-h-[300px]"
        >
          <div
            class="w-12 h-12 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"
          ></div>
          <p class="mt-4 text-lg text-gray-600">正在获取内容，请稍候...</p>
        </div>

        <!-- 内容区域 -->
        <div v-else>
          <div v-for="section in articles" :key="section.section" class="mb-12">
            <h2
              class="text-2xl font-bold text-gray-700 pb-3 border-b-2 border-gray-100 mb-6"
            >
              {{ section.section }}
            </h2>

            <div
              v-for="article in section.articles"
              :key="article.url"
              class="mb-8"
            >
              <div class="mb-4">
                <a
                  :href="article.url"
                  target="_blank"
                  class="text-xl font-bold text-blue-500 hover:underline block mb-1"
                >
                  {{ article.title }}
                </a>
                <div class="text-gray-600 italic">{{ article.title_en }}</div>
              </div>

              <div class="space-y-4">
                <div
                  class="text-gray-800 leading-relaxed"
                  v-html="article.content"
                ></div>
                <blockquote
                  class="bg-gray-50 p-4 border-l-4 border-blue-500 text-gray-600"
                >
                  <div v-html="article.content_en"></div>
                </blockquote>
              </div>

              <div class="my-8 border-b border-gray-100"></div>
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
          `${API_URL}/api/newsletter/${dateParam}`
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
