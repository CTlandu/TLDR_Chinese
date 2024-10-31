<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <!-- 导航栏 -->
    <nav class="bg-white p-6 mb-8 rounded-xl shadow-lg">
      <ul class="flex flex-wrap gap-2 justify-center">
        <li v-for="date in dates" :key="date">
          <router-link
            :to="'/newsletter/' + date"
            :class="[
              'px-5 py-2.5 rounded-lg font-medium transition-all duration-300',
              'hover:bg-gray-100 hover:-translate-y-0.5',
              date === currentDate
                ? 'bg-primary text-white shadow-md shadow-primary/30'
                : 'bg-gray-50 text-gray-600',
            ]"
          >
            {{ date }}
          </router-link>
        </li>
      </ul>
    </nav>

    <h1 class="text-3xl font-bold text-center text-gray-800 mb-8">
      TLDR Newsletter - {{ currentDate }}
    </h1>

    <!-- 加载状态 -->
    <div
      v-if="loading"
      class="flex flex-col items-center justify-center min-h-[300px]"
    >
      <div
        class="w-12 h-12 border-4 border-gray-200 border-t-primary rounded-full animate-spin"
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
              class="text-xl font-bold text-primary hover:underline block mb-1"
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
              class="bg-gray-50 p-4 border-l-4 border-primary text-gray-600"
            >
              <div v-html="article.content_en"></div>
            </blockquote>
          </div>

          <div class="my-8 border-b border-gray-100"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export default {
  name: "NewsletterView",
  data() {
    return {
      currentDate: "",
      dates: [],
      articles: [],
      loading: false,
    };
  },
  async created() {
    await this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;
      try {
        const date = this.$route.params.date || "2024-03-19";
        const response = await axios.get(`${API_URL}/api/newsletter/${date}`);

        // 确保数据正确解码
        this.currentDate = response.data.currentDate;
        this.dates = response.data.dates;
        this.articles = response.data.articles.map((section) => ({
          ...section,
          articles: section.articles.map((article) => ({
            ...article,
            title: this.decodeString(article.title),
            content: this.decodeString(article.content),
          })),
        }));
      } catch (error) {
        console.error("Error fetching newsletter:", error);
      } finally {
        this.loading = false;
      }
    },

    decodeString(str) {
      try {
        // 处理可能的 Unicode 转义序列
        return str.replace(/\\u[\dA-F]{4}/gi, (match) =>
          String.fromCharCode(parseInt(match.replace(/\\u/g, ""), 16))
        );
      } catch (e) {
        return str;
      }
    },
  },
  watch: {
    "$route.params.date": {
      handler: "fetchData",
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
