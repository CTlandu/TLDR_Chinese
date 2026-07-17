<template>
  <nav aria-label="往期存档" class="mb-6 sm:mb-8">
    <div class="flex items-center gap-2 overflow-x-auto pb-1">
      <span class="shrink-0 pr-1 text-xs font-semibold text-base-content/40">
        往期
      </span>
      <router-link
        v-for="date in dates"
        :key="date"
        :to="`/newsletter/${date}`"
        :class="[
          'shrink-0 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
          date === currentDate
            ? 'bg-primary text-white'
            : 'border border-white/10 bg-base-200 text-base-content/70 hover:border-white/20 hover:text-base-content',
        ]"
      >
        {{ date.slice(5) }}
      </router-link>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'DateSelector',
  props: {
    dates: {
      type: Array,
      default: () => [],
    },
    currentDate: {
      type: String,
      default: '',
    },
  },
};
</script>
