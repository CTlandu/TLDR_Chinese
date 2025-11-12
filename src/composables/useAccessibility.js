import { ref, watch } from 'vue';

// 字体大小选项
export const FONT_SIZES = {
  SMALL: 'small',
  MEDIUM: 'medium',
  LARGE: 'large',
};

// 色盲模式选项
export const COLOR_MODES = {
  NORMAL: 'normal',
  HIGH_CONTRAST: 'high-contrast',
  COLOR_BLIND_FRIENDLY: 'color-blind-friendly',
};

// 全局状态
const fontSize = ref(FONT_SIZES.MEDIUM);
const colorMode = ref(COLOR_MODES.NORMAL);

// 从 localStorage 加载设置
const loadSettings = () => {
  const savedFontSize = localStorage.getItem('accessibility-font-size');
  const savedColorMode = localStorage.getItem('accessibility-color-mode');

  if (savedFontSize && Object.values(FONT_SIZES).includes(savedFontSize)) {
    fontSize.value = savedFontSize;
  }

  if (savedColorMode && Object.values(COLOR_MODES).includes(savedColorMode)) {
    colorMode.value = savedColorMode;
  }
};

// 初始化时加载设置
loadSettings();

export function useAccessibility() {
  // 设置字体大小
  const setFontSize = (size) => {
    if (Object.values(FONT_SIZES).includes(size)) {
      fontSize.value = size;
      localStorage.setItem('accessibility-font-size', size);
      applyFontSize(size);
    }
  };

  // 设置色盲模式
  const setColorMode = (mode) => {
    if (Object.values(COLOR_MODES).includes(mode)) {
      colorMode.value = mode;
      localStorage.setItem('accessibility-color-mode', mode);
      applyColorMode(mode);
    }
  };

  // 应用字体大小到 document
  const applyFontSize = (size) => {
    const root = document.documentElement;
    root.setAttribute('data-font-size', size);
  };

  // 应用色盲模式到 document
  const applyColorMode = (mode) => {
    const root = document.documentElement;
    root.setAttribute('data-color-mode', mode);
  };

  // 初始化应用当前设置
  applyFontSize(fontSize.value);
  applyColorMode(colorMode.value);

  // 监听变化
  watch(fontSize, (newSize) => {
    applyFontSize(newSize);
  });

  watch(colorMode, (newMode) => {
    applyColorMode(newMode);
  });

  return {
    fontSize,
    colorMode,
    setFontSize,
    setColorMode,
    FONT_SIZES,
    COLOR_MODES,
  };
}

