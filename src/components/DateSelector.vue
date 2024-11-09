<template>
  <nav class="bg-white p-6 mb-8 rounded-xl shadow-lg">
    <ul class="flex flex-wrap gap-4 justify-center items-center">
      <li>
        <button
          @click="$emit('navigate', today)"
          class="px-5 py-2.5 rounded-lg font-medium transition-all duration-300 bg-green-400 text-gray-600 hover:bg-gray-100 hover:-translate-y-0.5"
        >
          今日新闻
        </button>
      </li>
      <li>
        <button
          @click="$emit('navigate', yesterday)"
          class="px-5 py-2.5 mr-10 rounded-lg font-medium transition-all duration-300 bg-blue-400 text-gray-600 hover:bg-gray-100 hover:-translate-y-0.5"
        >
          昨日新闻
        </button>
      </li>
      <li v-for="date in adjustedDates" :key="date">
        <button
          @click="$emit('navigate', date)"
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
</template>

<script>
export default {
  props: {
    currentDate: String,
    adjustedDates: Array,
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
  },
};
</script>
