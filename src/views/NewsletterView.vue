<template>
  <ErrorBoundary @retry="fetchData">
    <div>
      <!-- Navbar -->
      <Navbar />

      <div class="max-w-3xl mx-auto px-4 py-8">
        <!-- 日期选择器 -->
        <nav class="bg-white p-6 mb-8 rounded-xl shadow-lg">
          <ul class="flex flex-wrap gap-4 justify-center items-center">
            <li>
              <button
                @click="navigateTo(today)"
                class="px-5 py-2.5 rounded-lg font-medium transition-all duration-300 bg-green-400 text-gray-600 hover:bg-gray-100 hover:-translate-y-0.5"
              >
                今日新闻
              </button>
            </li>
            <li>
              <button
                @click="navigateTo(yesterday)"
                class="px-5 py-2.5 mr-10 rounded-lg font-medium transition-all duration-300 bg-blue-400 text-gray-600 hover:bg-gray-100 hover:-translate-y-0.5"
              >
                昨日新闻
              </button>
            </li>
            <li v-for="date in adjustedDates" :key="date">
              <button
                @click="navigateTo(date)"
                :class="[
                  'px-5 py-2.5 rounded-lg font-medium transition-all duration-300',
                  'hover:bg-gray-100 hover:-translate-y-0.5',
                  date === currentDate
                    ? 'bg-blue-300 text-white shadow-md shadow-blue-300'
                    : 'bg-gray-50 text-gray-600',
                ]"
              >
                {{ date }}
              </button>
            </li>
          </ul>
        </nav>

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
      dates: [],
      articles: [],
      loading: false,
    };
  },
  computed: {
    today() {
      return new Date().toISOString().split('T')[0];
    },
    yesterday() {
      const date = new Date();
      date.setDate(date.getDate() - 1);
      return date.toISOString().split('T')[0];
    },
    adjustedDates() {
      const current = new Date(this.currentDate);
      if (isNaN(current.getTime())) {
        return [];
      }
      const nextDay = new Date(current);
      nextDay.setDate(current.getDate() + 1);
      const previousDay = new Date(current);
      previousDay.setDate(current.getDate() - 1);

      return [
        nextDay.toISOString().split('T')[0],
        this.currentDate,
        previousDay.toISOString().split('T')[0],
      ];
    },
  },
  methods: {
    async fetchData() {
      this.loading = true;
      try {
        const date = this.$route.params.date;

        // 验证日期是否有效且不是未来日期
        const requestDate = new Date(date);
        const today = new Date();
        if (isNaN(requestDate.getTime()) || requestDate > today) {
          throw new Error('无效的日期或未来日期');
        }

        const API_URL =
          window.location.hostname === 'localhost'
            ? 'http://localhost:5000'
            : 'https://tldr-chinese-backend.onrender.com';

        const response = await axios.get(`${API_URL}/api/newsletter/${date}`);
        this.articles = response.data.articles;
        this.dates = response.data.dates;
        this.currentDate = date;
      } catch (error) {
        console.error('Error details:', error);
        this.articles = [];
        this.error = '获取数据失败：' + error.message;
      } finally {
        this.loading = false;
      }
    },
    navigateTo(date) {
      this.$router.push(`/newsletter/${date}`).then(() => {
        this.$router.go(0);
      });
    },
  },
  watch: {
    '$route.params.date': {
      handler: 'fetchData',
      immediate: true,
    },
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
