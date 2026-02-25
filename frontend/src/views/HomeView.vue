<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import pb from '@/services/pocketbase';
const router = useRouter();
const toast = useToast();
const inputRef = ref(null);
const isLoading = ref(false);
const settingsShown = ref(false);

const capSetting = ref(false);
const scharSetting = ref(false);
const foreignSetting = ref(false);
const apostropheSetting = ref(true);

const toggleCapSetting = async () => {
    capSetting.value = !capSetting.value;
}

const toggleScharSetting = async () => {
    scharSetting.value = !scharSetting.value;
}

const toggleForeignSetting = async () => {
    foreignSetting.value = !foreignSetting.value;
}

const toggleApostropheSetting = async () => {
    apostropheSetting.value = !apostropheSetting.value;
}

const toggleSettings = async () => {
    settingsShown.value = !settingsShown.value;
}

const closeSettings = async () => {
    settingsShown.value = false;
}

const fetchData = async (song_id) => {
    isLoading.value = true;

    try {
        const songUploads = await pb.collection('song_uploads').getFullList({
            filter: `song_id = "${song_id}"`,
        });
        return songUploads;
    } catch (error) {
        console.error('Error fetching song uploads:', error);
        toast.error('Database query failed! Try again in 5s.');
        isLoading.value = false;
    }
}

const createData = async (song_id) => {
    try {
        const response = await fetch(
            `${import.meta.env.VITE_LYRICS_API_URL}/?video_id=${song_id}`
        );
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error creating data:', error);
        // TODO: Right here add the fallback for bad titles
        toast.error("Song not found in database. Try a different link or a different song!");
        isLoading.value = false;
    }
};

const displayData = async (data, song_id) => {
    const resolvedData = await data;
    if (resolvedData === undefined) {
        isLoading.value = false;
        return
    }

    let query_parameters = {};

    const numEntries = resolvedData.length;
    if (numEntries === 0) {
        const response = await createData(song_id);
        if (!response.upload_id) {
            return
        }
        query_parameters.id = response.upload_id;
    } else if (numEntries === 1) {
        query_parameters.id = resolvedData[0].id;
    } else {
        //TODO: List possible lyrics versions
        query_parameters.id = resolvedData[numEntries - 1].id;
    }

    if (capSetting.value) {
        query_parameters.caps = "on";
    }
    if (scharSetting.value) {
        query_parameters.schars = "on";
    }
    if (foreignSetting.value) {
        query_parameters.foreign = "on";
    }
    if (!apostropheSetting.value) {
        query_parameters.apo = "off";
    }

    router.push({ path: '/game', query: query_parameters });
}

const handleSubmit = () => {
    const regex = /(?:https?:)?(?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtu\.be\/|youtube(?:-nocookie)?\.com\S*?[^\w\s-])([\w-]{11})(?=[^\w-]|$)(?![?=&+%\w.-]*(?:['"][^<>]*>|<\/a>))[?=&+%\w.-]*/gim;

    const inputValue = inputRef.value?.value;
    let video_id = null;

    if (inputValue.length === 11) {
        video_id = inputValue;
    } else {
        const match = regex.exec(inputValue);

        if (!match) {
            toast.warning("Invalid link, try copying the link url again!");
            return;
        }
        video_id = match[1];
    }

    const queryResults = fetchData(video_id);
    displayData(queryResults, video_id);
};

const startGame = (difficulty) => {
    // This would need to be implemented to handle the difficulty selection
    // For now, we'll just log it
    console.log(`Starting game with difficulty: ${difficulty}`);

    // Here you would set the appropriate parameters and redirect to the game page
    // Example:
    // router.push({ path: '/game', query: { difficulty: difficulty } });

    toast.info(`${difficulty} mode selected! This feature is coming soon.`);
};
</script>

<template>
    <main class="home-container">
        <div v-if="isLoading">
            <div class="lds-spinner">
                <div></div>
                <div></div>
                <div></div>
                <div></div>
                <div></div>
                <div></div>
                <div></div>
                <div></div>
                <div></div>
                <div></div>
                <div></div>
                <div></div>
            </div>
        </div>
        <div v-else class="content-container">
<!--
            <p class="tagline">Type to the rhythm of your favorite songs</p>
            <div class="difficulty-cards">
                <div class="card" @click="startGame('Easy')">
                    <div class="card-icon">🎵</div>
                    <h3>Easy</h3>
                    <p>0-30 WPM</p>
                    <div class="card-description">Perfect for beginners or casual typists</div>
                </div>

                <div class="card" @click="startGame('Medium')">
                    <div class="card-icon">🎶</div>
                    <h3>Medium</h3>
                    <p>30-60 WPM</p>
                    <div class="card-description">For experienced typists who want a challenge</div>
                </div>

                <div class="card" @click="startGame('Impossible')">
                    <div class="card-icon">🎼</div>
                    <h3>Impossible</h3>
                    <p>60+ WPM</p>
                    <div class="card-description">For typing masters only</div>
                </div>
            </div>

            <div class="divider">
                <span>or</span>
            </div>
!-->
            <div class="linkBox">
                <form @submit.prevent="handleSubmit">
                    <input ref="inputRef" type="text" name="link" placeholder="Paste a YouTube link to get started..."
                        autocorrect="off" autocapitalize="none">
                    <button type="submit" class="submit-button">
                        <img src="@/assets/right_arrow.svg" width="48" height="48" alt="Play">
                    </button>
                </form>
            </div>
        </div>

        <transition name="fade">
            <div v-if="settingsShown" class="settings-modal" @click="closeSettings">
                <div class="settings-window" @click.stop>
                    <div class="settings-content">
                        <div class="settings-topbar">
                            <h2>Lyric Settings</h2>
                        </div>

                        <div class="settings-list">
                            <div class="setting-item">
                                <span class="setting-label">Capital Letters</span>
                                <button @click="toggleCapSetting" class="toggle-button"
                                    :class="{ 'toggle-on': capSetting }">
                                    {{ capSetting ? "On" : "Off" }}
                                </button>
                            </div>

                            <div class="setting-item">
                                <span class="setting-label">Special Characters like -+,"():</span>
                                <button @click="toggleScharSetting" class="toggle-button"
                                    :class="{ 'toggle-on': scharSetting }">
                                    {{ scharSetting ? "On" : "Off" }}
                                </button>
                            </div>

                            <div class="setting-item">
                                <span class="setting-label">Foreign letters (accents) like é:</span>
                                <button @click="toggleForeignSetting" class="toggle-button"
                                    :class="{ 'toggle-on': foreignSetting }">
                                    {{ foreignSetting ? "On" : "Off" }}
                                </button>
                            </div>

                            <div class="setting-item">
                                <span class="setting-label">Apostrophes (') like they're and you're:</span>
                                <button @click="toggleApostropheSetting" class="toggle-button"
                                    :class="{ 'toggle-on': apostropheSetting }">
                                    {{ apostropheSetting ? "On" : "Off" }}
                                </button>
                            </div>
                        </div>

                        <button class="close-window-btn" @click="closeSettings">
                            ✖
                        </button>
                    </div>
                </div>
            </div>
        </transition>

        <div class="footer">
            <button class="settings-gear-btn" @click.prevent="toggleSettings">
                <img src="@/assets/gear_icon.svg" width="40" alt="Settings">
            </button>
        </div>
    </main>
</template>

<style scoped>
:root {
    /*--accent-color: #e25822;*/
    /* A warm orange/red that evokes music, similar to a vinyl record or musical note */
    --accent-color: #2596be;
    --background-color: #1e1e1e;
    --card-color: #2d2d2d;
    --text-color: #cccccc;
    --text-muted: #888888;
    --border-color: #3a3a3a;
}

.home-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 60vh;
    padding: 1rem;
    position: relative;
    background-color: var(--background-color);
    color: var(--text-color);
}

.tagline {
    font-size: 1.2rem;
    color: var(--text-muted);
}

.content-container {
    width: 100%;
    max-width: 1000px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
}

/* Difficulty Cards */
.difficulty-cards {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    width: 100%;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.card {
    font-family: Arial, sans-serif;
    background-color: var(--card-color);
    border-radius: 12px;
    padding: 1.5rem;
    width: 100%;
    max-width: 220px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
    border: 1px solid var(--border-color);
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    border-color: var(--accent-color);
}

.card:active {
    transform: translateY(-2px);
}

.card-icon {
    font-family: "Noto Color Emoji", sans-serif;
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: var(--accent-color);
}

.card h3 {
    font-size: 1.5rem;
    margin: 0 0 0.5rem 0;
    color: #ffffff;
}

.card p {
    font-size: 1.2rem;
    color: var(--accent-color);
    margin: 0 0 1rem 0;
    font-weight: 600;
}

.card-description {
    font-size: 0.9rem;
    color: var(--text-muted);
    line-height: 1.4;
}

/* Divider */
.divider {
    width: 100%;
    text-align: center;
    margin: 1rem 0;
    position: relative;
}

.divider::before,
.divider::after {
    content: "";
    position: absolute;
    top: 50%;
    width: 40%;
    height: 1px;
    background-color: var(--border-color);
}

.divider::before {
    left: 0;
}

.divider::after {
    right: 0;
}

.divider span {
    background-color: var(--background-color);
    padding: 0 1rem;
    position: relative;
    color: var(--text-muted);
}

/* Link Box */
.linkBox {
    width: 100%;
    max-width: 700px;
    margin: 1rem auto 2rem;
}

form {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: var(--card-color);
    border-radius: 12px;
    padding: 0.5rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
}

form:focus-within {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3), 0 0 0 2px rgba(152, 163, 166, 0.3);
}

form input {
    flex: 1;
    border: none;
    background-color: transparent;
    font-size: 180%;
    padding: 0.8rem 1.2rem;
    color: #ffffff;
    height: 3rem;
    width: 100%;
}

.submit-button {
    background-color: var(--accent-color);
    border: none;
    border-radius: 8px;
    padding: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.submit-button:hover {
    background-color: #3a3a3a;
    transform: scale(1.05);
}

.submit-button:active {
    transform: scale(0.98);
}

input::placeholder {
    color: var(--text-muted);
    font-style: italic;
}

input:focus {
    outline: none;
}

.hint-text {
    text-align: center;
    color: var(--text-muted);
    font-size: 1rem;
    margin-top: 1rem;
}

/* Settings Modal */
.settings-modal {
    position: fixed;
    z-index: 1000;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    transition: opacity 0.3s ease;
}

.settings-window {
    width: 90%;
    max-width: 600px;
    background: #2a2a2a;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    position: relative;
}

.settings-content {
    padding: 2rem;
}

.settings-topbar {
    margin-bottom: 1.5rem;
    text-align: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 1rem;
}

.settings-topbar h2 {
    margin: 0;
    font-size: 1.8rem;
    color: #ffffff;
    font-weight: 600;
}

.settings-list {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
}

.setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--border-color);
}

.setting-label {
    font-size: 1.1rem;
    color: var(--text-color);
}

.toggle-button {
    background-color: #333;
    opacity: 0.7;
    color: #ffffff;
    border: none;
    border-radius: 20px;
    padding: 0.5rem 1.2rem;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    min-width: 80px;
    text-align: center;
}

.toggle-button:hover {
    /*opacity: 0.9;*/
    transform: scale(1.05);
}

.toggle-button:active {
    transform: scale(0.98);
    opacity: 0.8;
}

.toggle-button.toggle-on {
    background-color: #444;
}

.close-window-btn {
    position: absolute;
    right: 1rem;
    top: 1rem;
    width: 36px;
    height: 36px;
    background: rgba(255, 255, 255, 0.1);
    border: none;
    border-radius: 50%;
    color: #ffffff;
    font-size: 1.2rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.close-window-btn:hover {
    background: rgba(124, 75, 73, 0.8);
}

/* Footer */
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 1.5rem;
    z-index: 1002;
    pointer-events: none;
    /* Default:  Clicks pass through */
}

.settings-gear-btn {
    pointer-events: auto;
    background: rgba(30, 30, 30, 0.7);
    border: none;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0.4;
    transition: all 0.3s ease;
}

.settings-gear-btn:hover {
    opacity: 1;
    transform: rotate(60deg);
}

.settings-gear-btn:active {
    transition: opacity none;
    opacity: 40%;
}

.nav-links {
    display: flex;
    gap: 1.5rem;
    position: absolute;
    right: 2rem;
}

.nav-link {
    color: var(--text-muted);
    text-decoration: none;
    font-size: 1rem;
    transition: color 0.2s ease;
}

.nav-link:hover {
    color: #ffffff;
}

/* Fade animation */
.fade-enter-active,
.fade-leave-active {
    transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
    transform: scale(1.1);
}

/* Pure CSS Loader */

.lds-spinner {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    margin-top: 8%;
}

.lds-spinner,
.lds-spinner div,
.lds-spinner div:after {
    box-sizing: border-box;
}

.lds-spinner {
    color: currentColor;
    display: inline-block;
    position: relative;
    width: 80px;
    height: 80px;
}

.lds-spinner div {
    transform-origin: 40px 40px;
    animation: lds-spinner 1.2s linear infinite;
}

.lds-spinner div:after {
    content: " ";
    display: block;
    position: absolute;
    top: 3.2px;
    left: 36.8px;
    width: 6.4px;
    height: 17.6px;
    border-radius: 20%;
    background: currentColor;
}

.lds-spinner div:nth-child(1) {
    transform: rotate(0deg);
    animation-delay: -1.1s;
}

.lds-spinner div:nth-child(2) {
    transform: rotate(30deg);
    animation-delay: -1s;
}

.lds-spinner div:nth-child(3) {
    transform: rotate(60deg);
    animation-delay: -0.9s;
}

.lds-spinner div:nth-child(4) {
    transform: rotate(90deg);
    animation-delay: -0.8s;
}

.lds-spinner div:nth-child(5) {
    transform: rotate(120deg);
    animation-delay: -0.7s;
}

.lds-spinner div:nth-child(6) {
    transform: rotate(150deg);
    animation-delay: -0.6s;
}

.lds-spinner div:nth-child(7) {
    transform: rotate(180deg);
    animation-delay: -0.5s;
}

.lds-spinner div:nth-child(8) {
    transform: rotate(210deg);
    animation-delay: -0.4s;
}

.lds-spinner div:nth-child(9) {
    transform: rotate(240deg);
    animation-delay: -0.3s;
}

.lds-spinner div:nth-child(10) {
    transform: rotate(270deg);
    animation-delay: -0.2s;
}

.lds-spinner div:nth-child(11) {
    transform: rotate(300deg);
    animation-delay: -0.1s;
}

.lds-spinner div:nth-child(12) {
    transform: rotate(330deg);
    animation-delay: 0s;
}

@keyframes lds-spinner {
    0% {
        opacity: 1;
    }

    100% {
        opacity: 0;
    }
}

/* Responsive styles */
@media (max-width: 768px) {
    .tagline {
        font-size: 1rem;
    }

    .card {
        max-width: 100%;
    }

    .difficulty-cards {
        flex-direction: column;
        align-items: center;
    }

    .divider::before,
    .divider::after {
        width: 30%;
    }

    form input {
        font-size: 1.1rem;
        padding: 0.6rem 1rem;
    }

    .submit-button img {
        width: 36px;
        height: 36px;
    }

    .setting-label {
        font-size: 0.9rem;
        max-width: 70%;
    }

    .toggle-button {
        font-size: 0.9rem;
        padding: 0.4rem 1rem;
    }

    .nav-links {
        right: 1rem;
    }
}
</style>
