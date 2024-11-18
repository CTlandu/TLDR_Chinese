import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import NewsletterView from '../views/NewsletterView.vue';
import SubscriptionSuccess from '../views/SubscriptionSuccess.vue';
import SubscriptionError from '../views/SubscriptionError.vue';
import NotFound from '../views/NotFound.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
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
  {
    path: '/subscription/success',
    name: 'SubscriptionSuccess',
    component: SubscriptionSuccess,
  },
  {
    path: '/subscription/error',
    name: 'SubscriptionError',
    component: SubscriptionError,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
