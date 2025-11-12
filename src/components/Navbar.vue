<template>
  <div class="navbar bg-base-200">
    <div class="flex-1 flex items-center gap-2 pl-4">
      <router-link to="/" class="flex items-center gap-2">
        <img src="../../assets/logo-3.png" alt="TLDR Logo" class="h-8 w-8" />
        <span class="rainbow-text font-bold text-xl">太长不看</span>
      </router-link>
      <div class="divider divider-horizontal mx-2"></div>
      <router-link :to="`/newsletter/${today}`" class="btn btn-ghost">
        今日新闻
      </router-link>
      <span class="text-base-content/60">广告投放</span>
    </div>

    <!-- 可访问性设置按钮 -->
    <div class="flex-none pr-4">
      <div class="dropdown dropdown-end">
        <label tabindex="0" class="btn btn-ghost btn-circle" title="可访问性设置">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            class="w-6 h-6 stroke-current"
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
          class="dropdown-content menu p-4 shadow-lg bg-base-100 rounded-box w-72 mt-3 border border-base-300"
        >
          <h3 class="font-bold text-lg mb-3 px-2">可访问性设置</h3>

          <!-- 字体大小设置 -->
          <div class="mb-4">
            <label class="label">
              <span class="label-text font-semibold">📝 字体大小</span>
            </label>
            <div class="btn-group w-full">
              <button
                @click="setFontSize(FONT_SIZES.SMALL)"
                :class="[
                  'btn btn-sm flex-1',
                  fontSize === FONT_SIZES.SMALL ? 'btn-primary' : 'btn-outline',
                ]"
              >
                小
              </button>
              <button
                @click="setFontSize(FONT_SIZES.MEDIUM)"
                :class="[
                  'btn btn-sm flex-1',
                  fontSize === FONT_SIZES.MEDIUM ? 'btn-primary' : 'btn-outline',
                ]"
              >
                中
              </button>
              <button
                @click="setFontSize(FONT_SIZES.LARGE)"
                :class="[
                  'btn btn-sm flex-1',
                  fontSize === FONT_SIZES.LARGE ? 'btn-primary' : 'btn-outline',
                ]"
              >
                大
              </button>
            </div>
          </div>

          <!-- 色盲模式设置 -->
          <div>
            <label class="label">
              <span class="label-text font-semibold">🎨 显示模式</span>
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

          <!-- 提示信息 -->
          <div class="alert alert-info mt-4 py-2 text-xs">
            <span>设置会自动保存到您的浏览器</span>
          </div>
        </div>
      </div>
    </div>
  </div>
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
};
</script>

<style scoped>
.rainbow-text {
  background: linear-gradient(
    to right,
    #ff0000,
    /* #ff8000,
    #ffff00, */ #00ff00,
    #00ffff,
    #0000ff,
    #8000ff
  );
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: rainbow-move 5s linear infinite;
  background-size: 200% auto;
}

@keyframes rainbow-move {
  0% {
    background-position: 0% center;
  }
  100% {
    background-position: 200% center;
  }
}
</style>
