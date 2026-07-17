import { createApp } from 'vue';
import { createHead } from '@unhead/vue/client';
import App from './App.vue';
import router from './router';
import { createI18n } from 'vue-i18n';
import '@fontsource/nunito/400.css';
import '@fontsource/nunito/600.css';
import '@fontsource/nunito/700.css';
import '@fontsource/nunito/800.css';
import './style.css';
import { inject } from '@vercel/analytics';

const messages = {
  zh: {
    number: '5',
    welcomePrefix: '分钟掌握',
    welcomeSuffix: '全球科技脉搏',
    free: '免费',
    descriptionPrefix: '订阅每日邮件，获取最新科技资讯。',
    descriptionSuffix: '获取创业、科技和编程领域最有趣的新闻摘要！',
    subscribe: '立即订阅',
    emailPlaceholder: '请输入您的邮箱地址',
    latestNews: '最新科技资讯',
    readMore: '阅读更多',
    sections: {
      'Big Tech & Startups': '科技公司',
      'Programming, Design & Data Science': '编程开发',
      'Science & Futuristic Technology': '前沿科技',
      Miscellaneous: '综合要闻',
      'Quick Links': '速览',
    },
  },
};

const i18n = createI18n({
  locale: 'zh',
  messages,
});

const head = createHead();

const app = createApp(App);
app.use(head);
app.use(router);
app.use(i18n);
app.mount('#app');

// 初始化 Vercel Analytics
inject();
