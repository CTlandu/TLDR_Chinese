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
    redirect: () => {
      const today = new Date().toISOString().split("T")[0];
      return `/newsletter/${today}`;
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
