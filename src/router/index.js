import { createRouter, createWebHistory } from "vue-router";
import NewsletterView from "../views/NewsletterView.vue";
import NotFound from "../views/NotFound.vue";

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
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: NotFound,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
