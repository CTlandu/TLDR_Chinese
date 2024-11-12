<template>
  <section class="py-12 bg-base-200">
    <div class="container mx-auto px-4">
      <h2 class="text-3xl font-bold text-center mb-8">
        {{ $t('latestNews') }}
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="article in articles"
          :key="article.url"
          class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow"
        >
          <figure v-if="article.image_url">
            <img
              :src="article.image_url"
              :alt="article.title"
              class="h-48 w-full object-cover"
              @error="handleImageError($event, article)"
            />
          </figure>
          <div class="card-body">
            <div class="flex items-center gap-2 mb-2">
              <span class="badge badge-primary">{{ article.section }}</span>
              <span class="text-sm opacity-60">{{ article.date }}</span>
            </div>
            <h3 class="card-title text-lg">{{ article.title }}</h3>
            <p
              class="text-base-content/70 line-clamp-3"
              v-html="article.content"
            ></p>
            <div class="card-actions justify-end mt-4">
              <a
                :href="article.url"
                target="_blank"
                class="btn btn-primary btn-sm"
              >
                {{ $t('readMore') }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LatestArticles',
  data() {
    return {
      articles: [],
    };
  },
  async mounted() {
    try {
      const API_URL =
        window.location.hostname === 'localhost'
          ? 'http://localhost:5000'
          : 'https://tldr-chinese-backend.onrender.com';

      const response = await axios.get(`${API_URL}/api/latest-articles`);
      this.articles = response.data;
    } catch (error) {
      console.error('Error fetching latest articles:', error);
    }
  },
  methods: {
    handleImageError(event, article) {
      event.target.style.display = 'none';
      article.image_url = null;
    },
  },
};
</script>
