import { createRouter, createWebHistory } from "vue-router";
import NewsletterView from "../views/NewsletterView.vue";

const routes = [
  {
    path: "/newsletter/:date",
    name: "newsletter",
    component: NewsletterView,
  },
  {
    path: "/",
    redirect: "/newsletter/2024-10-31", // 默认日期
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
