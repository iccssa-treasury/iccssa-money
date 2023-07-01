import FomanticUI from 'vue-fomantic-ui';
import 'fomantic-ui-css/semantic.min.css';

// import '@/assets/geometry.css';
// import '@/assets/styles.css';

import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import UserApplicationsPage from './pages/UserApplicationsPage.vue';
import NewApplicationPage from './pages/NewApplicationPage.vue';
import ApplicationsPage from './pages/ApplicationsPage.vue';
import ApplicationPage from './pages/ApplicationPage.vue';
import NotFoundPage from './pages/NotFoundPage.vue';

// URL declarations.
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/me/applications/', component: UserApplicationsPage },
    { path: '/applications/new/', component: NewApplicationPage },
    { path: '/applications/', component: ApplicationsPage },
    { path: '/application/:pk/', component: ApplicationPage, props: true },
    // // See: https://router.vuejs.org/guide/essentials/dynamic-matching.html#catch-all-404-not-found-route
    { path: '/:pathMatch(.*)*', component: NotFoundPage },
  ],
  // Jump to top when switching between pages.
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 }; // behavior: 'smooth'
    }
  },
});

// Entry point.
const app = createApp(App);
app.use(FomanticUI);
app.use(router);
app.mount('#app');
