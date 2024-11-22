<template>
  <div class="min-h-screen bg-base-100 flex items-center justify-center">
    <div
      class="max-w-md w-full mx-4 p-8 bg-base-200 rounded-lg shadow-xl text-center"
    >
      <div class="mb-8">
        <svg
          class="w-16 h-16 mx-auto text-success"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>

      <h2 class="text-2xl font-bold mb-4">取消订阅成功</h2>

      <div class="space-y-4 mb-8">
        <p class="text-base-content/70">
          您已成功取消订阅 TLDR Chinese 每日科技新闻。
        </p>
        <p class="text-base-content/70">如果您改变主意，随时可以重新订阅。</p>
      </div>

      <div class="flex justify-center space-x-4">
        <router-link to="/" class="btn btn-primary"> 返回首页 </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UnsubscribedView',
};
</script>
