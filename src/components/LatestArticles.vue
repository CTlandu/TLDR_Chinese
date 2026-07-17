<template>
  <section class="max-w-content mx-auto w-full px-4 sm:px-6 pb-12">
    <h2 class="text-2xl font-extrabold text-base-content mb-8">更多新闻</h2>

    <div
      v-for="key in orderedKeys"
      :key="key"
      v-show="cards(key).length"
      class="mb-10"
    >
      <div class="flex items-baseline gap-2 mb-4">
        <h3 class="text-lg font-extrabold text-accent">
          {{ $t('sections.' + key) }}
        </h3>
        <span
          class="text-[11px] font-bold uppercase tracking-wider text-base-content/25"
        >
          {{ key }}
        </span>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        <a
          v-for="article in cards(key)"
          :key="article.url"
          :href="article.url"
          target="_blank"
          rel="noopener"
          class="group block overflow-hidden rounded-lg border border-white/5 bg-base-200 transition-colors hover:border-white/15 hover:bg-base-300"
        >
          <div class="aspect-[16/10] overflow-hidden bg-base-300">
            <img
              v-if="article.image_url && !failed[article.url]"
              :src="article.image_url"
              :alt="article.title"
              loading="lazy"
              class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
              @error="onImgError(article.url)"
            />
            <div
              v-else
              class="flex h-full w-full items-center justify-center text-xs text-base-content/20"
            >
              暂无配图
            </div>
          </div>
          <div class="p-3">
            <div class="mb-1.5 text-xs font-semibold text-accent">
              {{ article.relative_time }}
              <span class="text-base-content/25">·</span>
              {{ $t('sections.' + key) }}
            </div>
            <h4
              class="line-clamp-3 text-sm font-bold leading-snug text-base-content transition-colors group-hover:text-primary"
            >
              {{ zhTitle(article) }}
            </h4>
            <p
              v-if="enTitle(article)"
              class="mt-1.5 line-clamp-2 text-xs leading-snug text-base-content/40"
            >
              {{ enTitle(article) }}
            </p>
          </div>
        </a>
      </div>
    </div>
  </section>
</template>

<script>
import { stripLeadingEmoji, stripReadingTime } from '../utils/text';

export default {
  name: 'LatestArticles',
  props: {
    sections: {
      type: Object,
      default: () => ({}),
    },
    enMap: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      orderedKeys: [
        'Big Tech & Startups',
        'Programming, Design & Data Science',
        'Science & Futuristic Technology',
        'Miscellaneous',
        'Quick Links',
      ],
      failed: {},
    };
  },
  methods: {
    // 首篇文章已用于头条/侧栏，这里从第二篇开始展示，避免重复
    cards(key) {
      const list = this.sections[key];
      return Array.isArray(list) ? list.slice(1) : [];
    },
    zhTitle(article) {
      return stripLeadingEmoji(article?.title || '');
    },
    enTitle(article) {
      if (!article) return '';
      const direct = stripReadingTime(article.title_en || '');
      if (direct) return direct;
      return this.enMap[article.url] || '';
    },
    onImgError(url) {
      this.failed[url] = true;
    },
  },
};
</script>
