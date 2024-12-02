import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import NewsletterView from '../views/NewsletterView.vue';
import SubscriptionSuccess from '../views/SubscriptionSuccess.vue';
import SubscriptionError from '../views/SubscriptionError.vue';
import NotFound from '../views/NotFound.vue';
import UnsubscribedView from '../views/UnsubscribedView.vue';

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
    path: '/subscription/success',
    name: 'SubscriptionSuccess',
    component: SubscriptionSuccess,
  },
  {
    path: '/subscription/error',
    name: 'SubscriptionError',
    component: SubscriptionError,
  },
  {
    path: '/unsubscribed',
    name: 'UnsubscribedView',
    component: UnsubscribedView,
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
