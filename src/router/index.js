import { createRouter, createWebHistory } from "vue-router";
import NewsletterView from "../views/NewsletterView.vue";

const routes = [
  {
    path: "/newsletter/:date?",
    name: "newsletter",
    component: NewsletterView,
  },
  {
    path: "/",
    redirect: "/newsletter",
  },
  {
    path: "/newsletter",
    redirect: () => {
      return `/newsletter/${new Date().toISOString().split("T")[0]}`;
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
