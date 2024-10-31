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

    <div v-for="section in articles" :key="section.section" class="section">
      <h2>{{ section.section }}</h2>
      <div v-html="section.content" class="section-content"></div>
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
    };
  },
  async created() {
    await this.fetchData();
  },
  methods: {
    async fetchData() {
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

/* 复用原有的 CSS 样式 */
.navbar {
  background: #f8f9fa;
  padding: 1rem;
  margin-bottom: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.section-content :deep(blockquote) {
  border-left: 4px solid #ddd;
  margin: 15px 0;
  padding: 10px 20px;
  color: #666;
  background: #f9f9f9;
}

/* 其他样式可以从原有的 HTML 模板中复制过来 */
</style>
