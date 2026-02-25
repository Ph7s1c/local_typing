<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted, onBeforeUnmount } from 'vue';
import LogoComponent from '@/components/LogoComponent.vue'

const isMobile = ref(false);

const checkIfMobile = () => {
    isMobile.value = window.innerWidth <= 700;
};

onMounted(() => {
    checkIfMobile();
    window.addEventListener('resize', checkIfMobile);
});

onBeforeUnmount(() => {
    window.removeEventListener('resize', checkIfMobile);
});
</script>


<template>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Color+Emoji&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:ital,wght@0,200..900;1,200..900&display=swap"
        rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap" rel="stylesheet">

    <div v-if="!isMobile">
        <header>
            <div class="head-links">
                <RouterLink to="/" class="link" active-class="active-link" title="Homepage">
                    <div class="icon-pair">
                        <span class="aligned-icons">
                            <img src="@/assets/home_icon.svg" width="30" height="30">
                            Home
                        </span>
                    </div>
                </RouterLink>
                <RouterLink to="/upload" class="link" active-class="active-link" title="Sync a song">
                    <div class="icon-pair">
                        <span class="aligned-icons">
                            <img src="@/assets/upload_song_icon.svg" width="30" height="30">
                            Upload
                        </span>
                    </div>
                </RouterLink>
            </div>

            <div class="head-middle">
                <RouterLink to="/" title="MelodyType">
                    <LogoComponent />
                </RouterLink>
            </div>

            <div class="head-links">
                <RouterLink to="/about" class="link" active-class="active-link" title="About">
                    <div class="icon-pair">
                        <span class="aligned-icons">
                            <img src="@/assets/about_icon.svg" width="30" height="30">
                            About
                        </span>
                    </div>
                </RouterLink>
                <RouterLink to="/browse" class="link" active-class="active-link" title="Browse saved songs">
                    <div class="icon-pair">
                        <span class="aligned-icons">
                            <img src="@/assets/profile_icon.svg" width="30" height="30">
                            Browse
                        </span>
                    </div>
                </RouterLink>
            </div>
        </header>
        <RouterView />
    </div>
    <div v-else>
        <!-- Content to display for mobile users -->
        <h1>Sorry, we don't yet support mobile.</h1>
        <p>Please use a laptop / desktop computer to play.</p>
    </div>

</template>

<style scoped>
header {
    /* Positioning Child elements */
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    justify-content: space-between;
    gap: 250px;

    /* Positioning the topbar */
    position: relative;
    width: 96%;
    height: 75px;
    margin-top: 2%;
    margin-left: 2%;
    margin-right: 2%;
}

.head-links {
    font-size: 125%;
    max-height: 30px;
    opacity: 60%;
    overflow: hidden;
}

.head-links a {
    margin-left: 5px;
    margin-right: 5px;
}

.head-middle {
    position: absolute;
    /* Position it absolutely within the container */
    left: 50%;
    transform: translateX(-50%);
}

.icon-pair {
    display: inline-block;
}

.link {
    opacity: 70%;
}

.link:hover {
    opacity: 90%;
}

.link:active {
    opacity: 60%;
}

.active-link {
    opacity: 100%;
}

.aligned-icons {
    display: flex;
    align-items: center;
    gap: 5px;
}
</style>
