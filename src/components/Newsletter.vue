<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <nav class="bg-base-200 rounded-lg shadow-md mb-8 p-4">
      <ul class="flex flex-wrap gap-2 justify-center">
        <li v-for="date in dates" :key="date">
          <router-link
            :to="'/newsletter/' + date"
            :class="[
              'px-3 py-2 rounded-md text-sm sm:text-base transition-colors duration-200',
              date === currentDate
                ? 'bg-primary text-primary-content'
                : 'text-base-content hover:bg-base-300',
            ]"
          >
            {{ date }}
          </router-link>
        </li>
      </ul>
    </nav>

    <div class="space-y-8">
      <h1
        class="text-2xl sm:text-3xl lg:text-4xl font-bold text-center text-base-content mb-8"
      >
        {{ generated_title }} 【{{ currentDate }}】
      </h1>

      <div v-for="section in articles" :key="section.section" class="space-y-4">
        <h2
          class="text-xl sm:text-2xl font-semibold text-base-content border-b border-base-300 pb-2"
        >
          {{ section.section }}
        </h2>
        <div
          v-html="section.content"
          class="prose prose-sm sm:prose lg:prose-lg max-w-none text-base-content"
        ></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Newsletter',
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
  watch: {
    // 监听 currentDate 的变化
    currentDate(newDate) {
      // 如果返回的日期与 URL 中的日期不同，更新路由
      if (newDate !== this.$route.params.date) {
        this.$router.replace(`/newsletter/${newDate}`);
      }
    },
  },
};
</script>

<style>
.prose :deep(blockquote) {
  @apply border-l-4 border-base-300 bg-base-200 my-4 px-4 py-2 text-base-content/80;
}

.prose :deep(a) {
  @apply text-primary hover:text-primary-focus transition-colors duration-200;
}

.prose :deep(p) {
  @apply text-base sm:text-lg leading-relaxed mb-4;
}

.prose :deep(img) {
  @apply rounded-lg max-w-full h-auto mx-auto my-4;
}

@media (max-width: 640px) {
  .prose :deep(blockquote) {
    @apply px-3 py-2 text-sm;
  }

  .prose :deep(p) {
    @apply text-sm leading-relaxed;
  }
}
</style>
