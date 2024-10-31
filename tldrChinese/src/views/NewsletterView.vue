<template>
  <div class="newsletter">
    <nav class="navbar">
      <ul>
        <li v-for="date in dates" :key="date">
          <router-link
            :to="'/newsletter/' + date"
            :class="{ active: date === currentDate }"
          >
            {{ date }}
          </router-link>
        </li>
      </ul>
    </nav>

    <h1>TLDR Newsletter - {{ currentDate }}</h1>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在获取内容，请稍候...</p>
    </div>

    <div v-else>
      <div v-for="section in articles" :key="section.section" class="section">
        <h2 class="section-title">{{ section.section }}</h2>
        <div
          v-for="article in section.articles"
          :key="article.url"
          class="article"
        >
          <div class="article-header">
            <a :href="article.url" target="_blank" class="article-title">
              {{ article.title }}
            </a>
            <div class="article-title-en">{{ article.title_en }}</div>
          </div>

          <div class="article-content">
            <div class="content-zh" v-html="article.content"></div>
            <blockquote
              class="content-en"
              v-html="article.content_en"
            ></blockquote>
          </div>
          <div class="article-divider"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

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
        const date = this.$route.params.date || "2024-10-31";
        const response = await axios.get(
          `http://localhost:5000/api/newsletter/${date}`
        );

        this.currentDate = response.data.currentDate;
        this.dates = response.data.dates;
        this.articles = response.data.articles;
      } catch (error) {
        console.error("Error fetching newsletter:", error);
      } finally {
        this.loading = false;
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

<style scoped>
.newsletter {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.section-title {
  margin: 40px 0 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #eee;
  color: #2c3e50;
  font-size: 1.8em;
}

.article {
  margin-bottom: 30px;
}

.article-header {
  margin-bottom: 15px;
}

.article-title {
  display: block;
  font-size: 1.4em;
  color: #0066cc;
  text-decoration: none;
  margin-bottom: 5px;
  font-weight: bold;
}

.article-title:hover {
  text-decoration: underline;
}

.article-title-en {
  color: #666;
  font-size: 1.1em;
  font-style: italic;
}

.article-content {
  margin: 15px 0;
}

.content-zh {
  margin-bottom: 15px;
  line-height: 1.6;
  color: #2c3e50;
}

.content-en {
  background: #f8f9fa;
  padding: 15px;
  margin: 10px 0;
  border-left: 4px solid #0066cc;
  color: #666;
  font-size: 0.95em;
}

.article-divider {
  margin: 30px 0;
  border-bottom: 1px solid #eee;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #0066cc;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 20px;
  color: #666;
  font-size: 1.1em;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.navbar {
  background: white;
  padding: 1.5rem;
  margin: 0 0 2rem 0;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.navbar ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.navbar a {
  padding: 0.6rem 1.2rem;
  text-decoration: none;
  color: #666;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
  background: #f8f9fa;
}

.navbar a:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.navbar a.active {
  background: #0066cc;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 102, 204, 0.3);
}

/* 添加渐变边缘效果 */
.navbar::before,
.navbar::after {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  width: 30px;
  pointer-events: none;
  z-index: 1;
}

.navbar::before {
  left: 0;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 1),
    rgba(255, 255, 255, 0)
  );
}

.navbar::after {
  right: 0;
  background: linear-gradient(
    to left,
    rgba(255, 255, 255, 1),
    rgba(255, 255, 255, 0)
  );
}
</style>
