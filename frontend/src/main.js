import './assets/main.css';

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createManager } from '@vue-youtube/core';
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";

import App from './App.vue';
import router from './router';

const app = createApp(App);

app.use(createPinia());
app.use(router);

const options = {
    position: "top-right",
    timeout: 10000,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: false,
    draggablePercent: 0.4,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: false,
    icon: true,
    rtl: false
};
app.use(Toast, options);

app.use(createManager());

app.mount('#app')
