<template>
  <header class="bg-base-100 border-b border-white/5">
    <div
      class="max-w-content mx-auto w-full px-4 sm:px-6 h-16 flex items-center justify-between gap-4"
    >
      <!-- 左侧 wordmark -->
      <router-link to="/" class="flex items-baseline gap-2 shrink-0">
        <span class="text-xl font-extrabold tracking-tight text-base-content">
          TLDR<span class="text-primary">中文版</span>
        </span>
        <span class="hidden sm:inline text-xs text-base-content/40 font-semibold">
          太长不看
        </span>
      </router-link>

      <!-- 右侧导航 -->
      <nav class="flex items-center gap-3 sm:gap-5">
        <router-link
          :to="`/newsletter/${today}`"
          class="text-sm font-semibold text-base-content/70 hover:text-base-content transition-colors"
        >
          今日新闻
        </router-link>
        <a
          href="https://mp.weixin.qq.com/s/8k55rjuc4GCsYlrD_i5n3A"
          target="_blank"
          rel="noopener"
          class="hidden sm:inline text-sm font-semibold text-base-content/70 hover:text-base-content transition-colors"
        >
          微信公众号
        </a>
        <button
          @click="goSubscribe"
          class="btn btn-primary btn-sm h-9 min-h-0 px-4 text-white font-bold"
        >
          订阅
        </button>

        <!-- 可访问性设置（收敛为小图标） -->
        <div class="dropdown dropdown-end">
          <label
            tabindex="0"
            class="btn btn-ghost btn-sm btn-circle text-base-content/60 hover:text-base-content"
            title="可访问性设置"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              class="w-5 h-5 stroke-current"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </label>
          <div
            tabindex="0"
            class="dropdown-content menu p-4 shadow-xl bg-base-200 rounded-box w-72 mt-3 border border-white/10 z-[60]"
          >
            <h3 class="font-bold text-base mb-3 px-1">可访问性设置</h3>

            <!-- 字体大小 -->
            <div class="mb-4">
              <label class="label py-1">
                <span class="label-text font-semibold">字体大小</span>
              </label>
              <div class="join w-full">
                <button
                  @click="setFontSize(FONT_SIZES.SMALL)"
                  :class="[
                    'btn btn-sm join-item flex-1',
                    fontSize === FONT_SIZES.SMALL ? 'btn-primary' : 'btn-outline',
                  ]"
                >
                  小
                </button>
                <button
                  @click="setFontSize(FONT_SIZES.MEDIUM)"
                  :class="[
                    'btn btn-sm join-item flex-1',
                    fontSize === FONT_SIZES.MEDIUM ? 'btn-primary' : 'btn-outline',
                  ]"
                >
                  中
                </button>
                <button
                  @click="setFontSize(FONT_SIZES.LARGE)"
                  :class="[
                    'btn btn-sm join-item flex-1',
                    fontSize === FONT_SIZES.LARGE ? 'btn-primary' : 'btn-outline',
                  ]"
                >
                  大
                </button>
              </div>
            </div>

            <!-- 显示模式 -->
            <div>
              <label class="label py-1">
                <span class="label-text font-semibold">显示模式</span>
              </label>
              <div class="flex flex-col gap-2">
                <button
                  @click="setColorMode(COLOR_MODES.NORMAL)"
                  :class="[
                    'btn btn-sm justify-start',
                    colorMode === COLOR_MODES.NORMAL ? 'btn-primary' : 'btn-outline',
                  ]"
                >
                  <span class="flex-1 text-left">标准模式</span>
                  <span v-if="colorMode === COLOR_MODES.NORMAL">✓</span>
                </button>
                <button
                  @click="setColorMode(COLOR_MODES.HIGH_CONTRAST)"
                  :class="[
                    'btn btn-sm justify-start',
                    colorMode === COLOR_MODES.HIGH_CONTRAST ? 'btn-primary' : 'btn-outline',
                  ]"
                >
                  <span class="flex-1 text-left">高对比度</span>
                  <span v-if="colorMode === COLOR_MODES.HIGH_CONTRAST">✓</span>
                </button>
                <button
                  @click="setColorMode(COLOR_MODES.COLOR_BLIND_FRIENDLY)"
                  :class="[
                    'btn btn-sm justify-start',
                    colorMode === COLOR_MODES.COLOR_BLIND_FRIENDLY
                      ? 'btn-primary'
                      : 'btn-outline',
                  ]"
                >
                  <span class="flex-1 text-left">色盲友好</span>
                  <span v-if="colorMode === COLOR_MODES.COLOR_BLIND_FRIENDLY">✓</span>
                </button>
              </div>
            </div>

            <p class="text-xs text-base-content/50 mt-4">设置会自动保存到浏览器</p>
          </div>
        </div>
      </nav>
    </div>
  </header>
</template>

<script>
import { useAccessibility } from '../composables/useAccessibility';

export default {
  name: 'Navbar',
  setup() {
    const { fontSize, colorMode, setFontSize, setColorMode, FONT_SIZES, COLOR_MODES } =
      useAccessibility();

    return {
      fontSize,
      colorMode,
      setFontSize,
      setColorMode,
      FONT_SIZES,
      COLOR_MODES,
    };
  },
  computed: {
    today() {
      const date = new Date();
      return date.toISOString().split('T')[0];
    },
  },
  methods: {
    goSubscribe() {
      if (this.$route.path === '/') {
        const el = document.getElementById('subscribe');
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          return;
        }
      }
      this.$router.push('/');
    },
  },
};
</script>
