import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createI18n } from 'vue-i18n';
import './style.css';

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
      'Big Tech & Startups': '科技公司动态 🏢 Big Tech & Startups',
      'Programming, Design & Data Science':
        '编程/设计/数据科学 👨‍💻 Programming, Design & Data Science',
      'Science & Futuristic Technology':
        '未来科技 🔬 Science & Futuristic Technology',
      Miscellaneous: '科技要闻 📌 Miscellaneous',
      'Quick Links': '速闻链接 ⚡️ Quick Links',
    },
  },
};

const i18n = createI18n({
  locale: 'zh',
  messages,
});

const app = createApp(App);
app.use(router);
app.use(i18n);
app.mount('#app');
