<template>
  <section class="py-10 bg-base-200">
    <div class="container mx-auto px-4">
      <h2 class="text-3xl font-bold text-center mb-8">
        {{ $t('latestNews') }}
      </h2>

      <div
        v-for="(articles, sectionName) in sections"
        :key="sectionName"
        class="mb-12"
      >
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold">
            {{ $t(`sections.${sectionName}`) }}
          </h3>
          <div class="flex gap-2">
            <button
              class="btn btn-circle btn-sm"
              @click="scrollSection(sectionName, -300)"
            >
              ❮
            </button>
            <button
              class="btn btn-circle btn-sm"
              @click="scrollSection(sectionName, 300)"
            >
              ❯
            </button>
          </div>
        </div>

        <div
          :ref="(el) => (sectionRefs[sectionName] = el)"
          class="flex overflow-x-auto gap-4 scroll-smooth hide-scrollbar"
          style="scroll-behavior: smooth; -webkit-overflow-scrolling: touch"
        >
          <div
            v-for="article in articles"
            :key="article.url"
            class="flex-none w-72"
          >
            <div
              class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow relative h-48"
            >
              <img
                :src="article.image_url"
                :alt="article.title"
                class="absolute inset-0 w-full h-full object-cover"
                @error="handleImageError($event, article)"
              />
              <div
                class="card-body absolute inset-0 bg-gradient-to-t from-black/70 to-transparent p-4 flex flex-col justify-end text-white"
              >
                <span class="text-xs opacity-80">{{
                  article.relative_time
                }}</span>
                <h3 class="text-lg font-bold line-clamp-2 mb-2">
                  {{ article.title }}
                </h3>
                <a
                  :href="article.url"
                  target="_blank"
                  class="btn btn-primary btn-sm w-fit self-end"
                >
                  {{ $t('readMore') }}
                </a>
              </div>
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
      sections: {},
      sectionRefs: {},
    };
  },
  async mounted() {
    try {
      const API_URL =
        window.location.hostname === 'localhost'
          ? 'http://localhost:5000'
          : 'https://tldr-chinese-backend.onrender.com';

      const response = await axios.get(
        `${API_URL}/api/latest-articles-by-section`
      );
      this.sections = response.data;
    } catch (error) {
      console.error('Error fetching latest articles:', error);
    }
  },
  methods: {
    handleImageError(event, article) {
      event.target.style.display = 'none';
      article.image_url = null;
    },
    scrollSection(sectionName, offset) {
      const element = this.sectionRefs[sectionName];
      if (element) {
        element.scrollLeft += offset;
      }
    },
  },
};
</script>

<style scoped>
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>
