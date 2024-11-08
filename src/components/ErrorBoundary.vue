<template>
  <div v-if="error" class="error-boundary">
    <p>{{ error }}</p>
    <button @click="retry">重试</button>
  </div>
  <slot v-else></slot>
</template>

<script>
export default {
  name: 'ErrorBoundary',
  emits: ['retry'],
  data() {
    return {
      error: null,
    };
  },
  methods: {
    retry() {
      this.error = null;
      this.$emit('retry');
    },
  },
  errorCaptured(err) {
    this.error = err.message;
    console.error('Error captured:', err);
    return false;
  },
};
</script>
