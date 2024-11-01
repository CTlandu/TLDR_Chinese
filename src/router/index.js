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
  {
    path: "/:pathMatch(.*)*",
    redirect: "/newsletter",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 添加导航守卫
router.beforeEach((to, from, next) => {
  console.log("Route change:", {
    from: from.fullPath,
    to: to.fullPath,
    params: to.params,
  });
  next();
});

export default router;
