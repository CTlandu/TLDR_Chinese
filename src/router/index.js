import { createRouter, createWebHistory } from "vue-router";
import NewsletterView from "../views/NewsletterView.vue";

const routes = [
  {
    path: "/newsletter/:date?",
    name: "newsletter",
    component: NewsletterView,
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/newsletter",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
