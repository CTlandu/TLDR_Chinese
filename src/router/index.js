import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import NewsletterView from '../views/NewsletterView.vue';
import NotFound from '../views/NotFound.vue';

const routes = [
  {
    path: '/newsletter/:date?',
    name: 'newsletter',
    component: NewsletterView,
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound,
  },
  { path: '/', component: HomeView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
