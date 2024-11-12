import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createI18n } from 'vue-i18n';
import './style.css';

const messages = {
  en: {
    welcome: 'Keep up with Tech in 5 minutes',
    description:
      'Stay updated with the latest tech news in both English and Chinese.',
    subscribe: 'Subscribe Now',
    latestNews: 'Latest Tech News',
    readMore: 'Read More',
  },
  zh: {
    welcome: '每日只需5分钟，掌握全球科技动脉',
    description: '获取最新的中英文科技新闻。',
    subscribe: '立即订阅',
    latestNews: '最新科技新闻',
    readMore: '阅读更多',
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
