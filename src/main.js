import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createI18n } from 'vue-i18n';
import './style.css';

const messages = {
  en: {
    number: '5',
    welcomePrefix: 'Minutes to Catch up With',
    welcomeSuffix: 'Tech',
    free: 'FREE',
    descriptionPrefix: 'daily email subscription to stay updated.',
    descriptionSuffix:
      'Get the most interesting stories in startups, tech, and programming!',
    subscribe: 'Subscribe Now',
    emailPlaceholder: 'Enter your email address',
    joinCommunity: 'Join 1,250,000+ readers for one daily email',
  },
  zh: {
    number: '5',
    welcomePrefix: '分钟掌握',
    welcomeSuffix: '全球科技脉搏',
    free: '免费',
    descriptionPrefix: '订阅每日邮件，获取最新科技资讯。',
    descriptionSuffix: '获取创业、科技和编程领域最有趣的新闻摘要！',
    subscribe: '立即订阅',
    emailPlaceholder: '请输入您的邮箱地址',
    joinCommunity: '加入超过1,250,000读者的每日推送邮件',
    latestNews: '最新科技资讯',
    readMore: '阅读更多',
    sections: {
      'Big Tech & Startups': '科技公司动态',
      'Programming, Design & Data Science': '编程/设计/数据科学',
      'Science & Futuristic Technology': '未来科技',
      Miscellaneous: '科技要闻',
      'Quick Links': '速闻链接',
    },
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
