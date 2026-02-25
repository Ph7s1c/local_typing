<script setup>
import { ref, provide, onMounted } from 'vue';
import { useGameState } from '@/stores/gameState'
import { useSettingState } from '@/stores/settingState'
import { useToast } from 'vue-toastification';
import TypingComponent from '../components/TypingComponent.vue'
import VideoComponent from '../components/VideoComponent.vue'
const props = defineProps(['data', 'upload_id'])
const toast = useToast();

const gameData = props.data;

const gameState = useGameState();
const settingState = useSettingState();
const isSubmitting = ref(false);
const isSubmitted = ref(false);
const settingsShown = ref(false);

const video = ref(null);
const globalSkipLine = ref(() => {
    console.log("Default skipLine, overridden by TypingComponent");
});
provide('drill', globalSkipLine);

let blurStatus = ref("blur");
let controller;

const saveResultLocally = () => {
    const result = {
        wpm: parseFloat(gameState.finalWPM.toFixed(1)),
        accuracy: parseFloat(gameState.finalAccuracy.toFixed(3)),
        date: new Date().toISOString(),
        songName: gameData.artist_name && gameData.song_name
            ? `${gameData.artist_name} - ${gameData.song_name}`
            : gameData.video_id,
    };
    localStorage.setItem('lastResult', JSON.stringify(result));
}

const debugSoftware = () => {
    console.log("Debug here");
}

const toggleSettings = async () => {
    settingsShown.value = !settingsShown.value;
    gameState.playing = false;
}

const closeSettings = async () => {
    settingsShown.value = false;
    gameState.playing = false;
}

const skipSection = () => {
    const typingInput = document.getElementById('typingInput');
    typingInput.focus();
    let endTime = gameData.lyrics[gameState.currentLineIndex].timestampEnd;
    if (endTime === "end") {
        gameState.finished = true;
    } else {
        video.value.jumpTo(endTime);
    }
    gameState.skippableSection = false;
}

const endSong = () => {
    gameState.finished = true;
}

// Houses the setInterval()
var started = null;

const startGameLoop = () => {
    if (started) return;

    // Update Line countdown
    let endTime = gameData.lyrics[gameState.currentLineIndex].timestampEnd;
    gameState.lineCountdown = Math.max(parseFloat((endTime - gameState.currentVideoSeconds).toFixed(2)), 0);

    gameState.playing = true;
    blurStatus.value = "unblur";
    video.value.playVideo();
    gameState.startStopwatch();
    const typingInput = document.getElementById('typingInput');
    typingInput.focus();

    started = setInterval(gameTick, 100);
}

const stopGameLoop = () => {
    blurStatus.value = "blur";
    let diff = gameState.getDiff();
    if (gameData.lyrics[gameState.currentLineIndex].content != "") {
        gameState.timeSpentTyping += diff;
    }
    clearInterval(started);
    started = null;
}

const gameTick = () => {
    if (gameState.finished) {
        blurStatus.value = "blur";
        gameState.skippableSection = false;
        video.value.pauseVideo();
        stopGameLoop();

        saveResultLocally();
        return;
    }

    // Update Line countdown
    let endTime = gameData.lyrics[gameState.currentLineIndex].timestampEnd
    gameState.lineCountdown = Math.max(parseFloat((endTime - gameState.currentVideoSeconds).toFixed(2)), 0);

    gameState.currentVideoSeconds = video.value.fetchCurrentTime();

    // Check if 15s from first timestampEnd have elapsed
    const firstEndTime = gameData.lyrics[0].timestampEnd;
    if (gameState.currentVideoSeconds >= firstEndTime + 15) {
        gameState.songEndable = true;
    } else {
        gameState.songEndable = false;
    }

    if (!gameState.playing) {
        blurStatus.value = "blur";
        video.value.pauseVideo();
        stopGameLoop();
        return;
    }

    if (gameState.videoPlaying) {
        video.value.playVideo();
    }

    if (gameState.currentLineIndex === gameData.lyrics.length - 1) {
        return;
    }


    switch (settingState.currentMode) {
        case "Line Stop":
            if (gameData.lyrics[gameState.currentLineIndex].timestampEnd <= gameState.currentVideoSeconds) {
                if (gameData.lyrics[gameState.currentLineIndex].content === "") {
                    globalSkipLine.value();
                    gameState.startStopwatch();
                    break;
                }
                video.value.pauseVideo();
                gameState.videoPlaying = false;
                gameState.canAdvance = true;
            }
            break;
        case "Line Skip":
            if (gameData.lyrics[gameState.currentLineIndex].timestampEnd <= gameState.currentVideoSeconds) {
                let diff = gameState.getDiff();
                if (gameData.lyrics[gameState.currentLineIndex].content != "") {
                    gameState.timeSpentTyping += diff;
                }
                globalSkipLine.value();
                gameState.startStopwatch();
                //video.value.pauseVideo();
            }
            break;
        case "No Sync":
            if (gameData.lyrics[gameState.currentLineIndex].timestampEnd <= gameState.currentVideoSeconds) {
                if (gameData.lyrics[gameState.currentLineIndex].content === "") {
                    globalSkipLine.value();
                    gameState.startStopwatch();
                    break;
                }
            }
            break;
        default:
            settingState.currentMode = "Line Skip";
    }
};

onMounted(() => {
    let wrapper = document.getElementById('wrapper');
    wrapper.focus();
    wrapper.addEventListener('keydown', (event) => {
        const key = event.key;

        if (!gameState.playing) {
            if (key === ' ') {
                startGameLoop();
            }
        }
    });
});
</script>

<template>
    <div id="wrapper">
        <div id="banner" class="overlay" tabindex="-1">
            <div v-if="!gameState.playing && !gameState.finished">
                <div v-if="gameState.ready">
                    <div>
                        <button class="start-button" @click="startGameLoop"></button>
                    </div>
                </div>
                <div v-else class="lds-spinner">
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
        </div>
        <!-- <div id="banner" class="overlay" tabindex="-1">
            <div v-if="gameState.playing" id="line-countdown">
                Next Line in {{ gameState.lineCountdown }}
            </div>
        </div> 
        -->
        <transition name="skip-thing">
            <div v-if="gameState.skippableSection && gameState.playing" class="overlay">
                <button @click.prevent="skipSection" id="skip-btn">
                    {{ (gameState.currentLineIndex === 0) ? 'Skip intro section?' : 'Skip this section?' }}
                    <img src="@/assets/fast-forward.svg" width="30" height="30">
                </button>
            </div>
        </transition>
        <transition name="skip-thing" class="overlay">
            <div v-if="!gameState.skippableSection && gameState.songEndable && gameState.playing">
                <button @click.prevent="endSong" id="skip-btn">
                    End song early?
                    <img src="@/assets/fast-forward.svg" width="30" height="30">
                </button>
            </div>
        </transition>
        <div v-if="!gameState.finished">
            <div id="main-typing" :class="[blurStatus]">
                <TypingComponent :data="gameData" />
            </div>

            <div>
                <transition name="fade">
                    <div v-if="settingsShown" class="settings-modal" @click="closeSettings">
                        <div class="settings-window" @click.stop>
                            <div class="settings-content">
                                <div class="settings-topbar">
                                    Game Settings
                                </div>
                                <div class="settings-rows">
                                    <div class="row1">
                                        <span class="toggle-mode">
                                            <button @click="settingState.cycleMode">
                                                Current Mode:
                                                {{ settingState.currentMode }}
                                            </button>
                                        </span>
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
            </div>
        </div>
        <div v-else class="results-overlay">
            <div class="results-banner">
                <div v-if="gameData.artist_name && gameData.song_name" id="song-title">
                    {{ gameData.artist_name }} - {{ gameData.song_name }}
                </div>
                <div class="stats-row">
                    <div class="stat-item">
                        <span class="stat-value">{{ gameState.finalWPM.toFixed(1) }}</span>
                        <span class="stat-label">WPM</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{{ (gameState.finalAccuracy * 100).toFixed(1) }}%</span>
                        <span class="stat-label">Accuracy</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{{ gameState.totalKeystrokes }}</span>
                        <span class="stat-label">Characters</span>
                    </div>
                </div>
            </div>
        </div>
        <VideoComponent ref="video" :data="gameData" />
    </div>

    <button @click.prevent="debugSoftware" id="debug-btn" style="display: none;">
        DEBUG BUTTON
    </button>
</template>

<style scoped>
#banner {
    position: absolute;
    top: 130px;
}

.start-button {
    background: none;
    border: none;
    cursor: pointer;
    border-left: 60px solid white;
    border-top: 35px solid transparent;
    border-bottom: 35px solid transparent;
    transform: translateX(10%);
}

.overlay {
    position: absolute;
    top: 0%;
    left: 50%;
    transform: translateX(-50%);
    z-index: 2;
}

.overlay:focus {
    outline: none;
}

#line-countdown {
    opacity: 50%;
    color: #2596be;
}

.results-overlay {
    position: absolute;
    top: 120px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
    pointer-events: none;
}

.results-banner {
    background-color: #2d2d2d;
    border-radius: 12px;
    padding: 24px 36px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    pointer-events: auto;
}

#song-title {
    font-size: 1.5em;
    color: #cccccc;
    margin-bottom: 18px;
    font-weight: 400;
}

.stats-row {
    display: flex;
    justify-content: center;
    gap: 60px;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-value {
    font-size: 2.1em;
    color: #ffffff;
    font-weight: 500;
    line-height: 1;
}

.stat-label {
    font-size: 1.125em;
    color: #888888;
    margin-top: 6px;
    font-weight: 400;
}

.submit-section {
    margin-top: 20px;
    display: flex;
    justify-content: center;
}

#main-typing {
    transition: filter 0.4s ease;
}

.blur {
    filter: blur(3px);
}

.unblur {
    filter: blur(0px);
}

#submit-btn {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 1em;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

#submit-btn:hover {
    background-color: #3a3a3a;
    border-color: #4a4a4a;
    transform: translateY(-1px);
}

#submit-btn:active {
    background-color: #252525;
    transform: translateY(0);
}

/* Skip button */
#skip-btn {
    background-color: transparent;
    color: #aaa;
    border: none;
    padding: 10px;
    cursor: pointer;
    position: relative;
    top: 100px;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* Old End button */
/* TODO: REMOVE */
/*#end-song {*/
/*    margin: 0 auto;*/
/*    background-color: transparent;*/
/*    color: #aaa;*/
/*    border: none;*/
/*    padding: 10px;*/
/*    cursor: pointer;*/
/*    display: flex;*/
/*    align-items: center;*/
/*    gap: 5px;*/
/*}*/

/* Settings Bar */

.settings-modal {
    color: white;
    position: fixed;
    z-index: 1000;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    transition: opacity 0.3s ease;
}

.settings-window {
    color: white;
    position: absolute;
    left: 50%;
    top: 20%;
    transform: translate(-50%);
    width: 50%;
    height: 30%;
    background: #555555;
    opacity: 100%;
    border-radius: 12px;
}

.settings-content {
    max-height: 30%;
    overflow: auto;
    scroll-behavior: smooth;
    scrollbar-width: none;
    padding: 10px;
}

.settings-topbar {
    font-size: 150%;
    display: flex;
    justify-content: center;
}

.settings-rows {
    display: grid;
    grid-template-columns: 1fr 100px 50px 5px;
    gap: 10px;
    margin-top: 10px;
}

.close-window-btn {
    position: absolute;
    right: 10px;
    top: 10px;
    padding: 6px;
    width: 30px;
    height: 30px;
    background: #7C4B49;
    border: none;
    border-radius: 4px;
    color: coral;
    cursor: pointer;
}

.close-window-btn:hover {
    opacity: 80%;
}

.close-window-btn:active {
    opacity: 60%;
}

.toggle-mode button {
    color: white;
    font-size: 120%;
    background: none;
    border: none;
    cursor: pointer;
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

/* TODO: Maybe experiment with this later */

/*.settings-gear-btn:hover::after {*/
/*    content: "Game Settings";*/
/*    font-weight: bold;*/
/*    color: #888888;*/
/*}*/

.settings-gear-btn:active {
    transition: opacity none;
    opacity: 40%;
    /*transform: rotate(60deg) scale(1.2);*/
}

/* Fade for modal */

.fade-enter-active,
.fade-leave-active {
    transition: all 0.5s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
    transform: scale(1.1);
}

/* Fade for skip-btn */

.skip-thing-enter-active {
    transition: all 0.5s;
}

.skip-thing-leave-active {
    transition: all 0.2s;
}

.skip-thing-enter-from,
.skip-thing-leave-to {
    opacity: 0;
}

/* Pure CSS Loader */

.lds-spinner {
    position: absolute;
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
</style>
