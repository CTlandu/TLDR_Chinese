import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createI18n } from 'vue-i18n';
import './style.css';

const messages = {
  en: {
    welcome: 'Welcome to TLDR Daily Tech News',
    description:
      'Stay updated with the latest tech news in both English and Chinese.',
    subscribe: 'Subscribe Now',
  },
  zh: {
    welcome: '欢迎来到 TLDR 每日科技新闻',
    description: '获取最新的中英文科技新闻。',
    subscribe: '立即订阅',
  },
};

const i18n = createI18n({
  locale: 'zh', // 默认语言
  messages,
});

const app = createApp(App);
app.use(router);
app.use(i18n);
app.mount('#app');
