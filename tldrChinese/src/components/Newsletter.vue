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

    <div class="content">
      <h1>TLDR Newsletter - {{ currentDate }}</h1>

      <div v-for="section in articles" :key="section.section" class="section">
        <h2>{{ section.section }}</h2>
        <div v-html="section.content" class="section-content"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Newsletter",
  props: {
    currentDate: {
      type: String,
      required: true,
    },
    dates: {
      type: Array,
      required: true,
    },
    articles: {
      type: Array,
      required: true,
      default: () => [],
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

.navbar a {
  padding: 0.5rem 1rem;
  text-decoration: none;
  color: #666;
  border-radius: 4px;
}

.navbar a.active {
  background: #0066cc;
  color: white;
}

h1 {
  text-align: center;
  color: #333;
}

h2 {
  margin-top: 30px;
  padding-bottom: 10px;
  border-bottom: 2px solid #eee;
  color: #444;
}

.section-content :deep(blockquote) {
  border-left: 4px solid #ddd;
  margin: 15px 0;
  padding: 10px 20px;
  color: #666;
  background: #f9f9f9;
}

.section-content :deep(a) {
  color: #0066cc;
  text-decoration: none;
}

.section-content :deep(a:hover) {
  text-decoration: underline;
}
</style>
