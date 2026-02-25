import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import BrowseView from '../views/BrowseView.vue'
import UploadView from '../views/UploadView.vue'
import AboutView from '../views/AboutView.vue'
import GameView from '../views/GameView.vue'
import UploadSongView from '../views/UploadSongView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView,
        },
        {
            path: '/browse',
            name: 'browse',
            component: BrowseView,
        },
        {
            path: '/upload',
            name: 'upload',
            component: UploadView,
        },
        {
            path: '/about',
            name: 'about',
            component: AboutView,
        },
        {
            path: '/game',
            name: 'game',
            component: GameView,
            props: route => ({ id: route.query.id }),
        },
        {
            path: '/upload_song',
            name: 'upload_song',
            component: UploadSongView,
            props: route => ({ id: route.query.id }),
        },
    ],
})

export default router
