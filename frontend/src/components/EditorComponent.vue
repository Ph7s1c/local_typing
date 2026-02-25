<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router';
import { useUploadState } from '@/stores/uploadState'
import { useToast } from 'vue-toastification';
import UploadYoutubeComponent from '../components/UploadYoutubeComponent.vue'
import pb from '@/services/pocketbase';

const props = defineProps(['lyricData', 'video_id'])

const toast = useToast();
const router = useRouter();
const video = ref(null);
const lyricsLines = props.lyricData.lyrics;
const uploadState = useUploadState();
const isSubmitting = ref(false);

const focusKeybinds = () => {
    const keybinds = document.getElementById('toggle-btn');
    keybinds.focus();
}

const addNewLine = (index) => {
    lyricsLines.splice(index, 0, {
        content: "",
    });
    try {
        focusKeybinds();
    } catch (error) {
        console.error("Error in focusKeybinds:", error);
    }
};

const rewindTo = (index) => {
    for (let i = index + 1; i < lyricsLines.length; i++) {
        const line = lyricsLines[i];
        line.timestamp = null;
        line.timestampEnd = null;
    }

    if (!lyricsLines[index].timestamp) {
        for (let i = index; i >= 0; i--) {
            const line = lyricsLines[i];
            if (line.timestamp || i === 0) {
                index = i;
                break;
            }
        }
    }
    lyricsLines[index].timestampEnd = lyricsLines[index].timestamp;
    video.value.jumpTo(lyricsLines[index].timestamp);
    uploadState.currentSeconds = lyricsLines[index].timestamp;
    console.log(index);
    uploadState.currentLineIndex = index;
    startLoop();
    focusKeybinds();
}

const scroll = (index) => {
    const table = document.getElementById("lyrics-table");
    const element = document.getElementsByClassName("lyrics-row")[index];

    const tableRect = table.getBoundingClientRect();

    const elementRect = element.getBoundingClientRect();

    const scrollPosition = elementRect.top - tableRect.top + table.scrollTop - 100;

    table.scrollTo({
        top: scrollPosition,
        behavior: 'smooth'
    });
}

const cycleRate = () => {
    switch (uploadState.playbackRate) {
        case 1:
            video.value.setPlaybackRate(2);
            break;
        case 2:
            video.value.setPlaybackRate(1);
            break;
        default:
            video.value.setPlaybackRate(1);
    }
}

// Initialize a spacer at the beginning
//lyricsLines.splice(0, 0, {timestamp: 0});
addNewLine(0);
// Add an end spacer
lyricsLines.push({ content: "" });

const removeLine = (index) => {
    lyricsLines.splice(index, 1)
    if (lyricsLines.length === 0) {
        addNewLine(0)
    }
    focusKeybinds();
}

// Houses the setInterval()
var started = null;

const toggleLoop = () => {
    if (!uploadState.ready) {
        return;
    }
    if (started) {
        stopLoop();
    } else {
        startLoop();
    }
}

const startLoop = () => {
    if (started) return;

    if (uploadState.currentLineIndex === 0 && !(lyricsLines[0]?.timestamp)) {
        lyricsLines[0].timestamp = 0;
    }

    uploadState.playing = true;
    video.value.playVideo();
    focusKeybinds();

    started = setInterval(tick, 100);
}

const stopLoop = () => {
    uploadState.playing = false;
    video.value.pauseVideo();
    clearInterval(started);
    started = null;
}

const tick = () => {
    if (!uploadState.playing) {
        video.value.pauseVideo();
        stopGameLoop();
        return;
    }

    uploadState.currentSeconds = parseFloat(video.value.fetchCurrentTime().toFixed(2));

    lyricsLines[uploadState.currentLineIndex].timestampEnd = uploadState.currentSeconds;
};

const nextLine = () => {
    //if (!lyricsLines[uploadState.currentLineIndex].timestamp 
    //    || !lyricsLines[uploadState.currentLineIndex].timestampEnd) {
    //    return;
    //}

    if (uploadState.currentLineIndex === 0 && !(lyricsLines[0]?.timestamp)) {
        lyricsLines[0].timestamp = 0;
    }

    if (uploadState.currentLineIndex === lyricsLines.length - 1) {
        toggleLoop();
        return;
    }
    let sec = uploadState.currentSeconds;
    let roundedSec = Math.round(sec * 100) / 100;
    lyricsLines[uploadState.currentLineIndex].timestampEnd = roundedSec;
    uploadState.currentLineIndex++;
    lyricsLines[uploadState.currentLineIndex].timestamp = roundedSec;
    scroll(uploadState.currentLineIndex);
}

const computeClass = (index) => {
    if (index < uploadState.currentLineIndex) {
        return ("previous");
    } else if (index === uploadState.currentLineIndex) {
        return ("active");
    } else {
        return ("future");
    }
}

const handleSubmit = async () => {
    isSubmitting.value = true;

    try {
        const data = {
            'song_id': props.video_id,
            'song_data': props.lyricData,
            'popularity_score': 0,
        };

        const record = await pb.collection('song_uploads').create(data);
        toast.success("Successfully uploaded");
        router.push({ path: '/' });
    } catch (error) {
        isSubmitting.value = false;
        toast.error(error.message);
    }
}

onMounted(() => {
    const keybinds = document.getElementById('keybinds');
    keybinds.addEventListener('keydown', (event) => {
        const key = event.key;

        switch (key) {
            case 'Backspace':
                break;
            case ' ':
                toggleLoop();
                break;
            case 'Enter':
                nextLine();
                break;
            case 'Delete':
            case 'Tab':
            case 'Shift':
            case 'CapsLock':
            case 'Control':
            case 'Meta':
            case 'Alt':
            case 'ArrowRight':
            case 'ArrowLeft':
            case 'ArrowUp':
            case 'ArrowDown':
                break;
            default:
                console.log("TODO REMOVE HERE");
        }

        event.preventDefault();
    });
});
</script>

<template>
    <div v-if="isSubmitting">
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
    <main v-else class="upload-container">
        <div id="lyrics-table">
            <div class="table-header">
                <div><!--This is just a placeholder--></div>
                <div class="start-header">Start Time</div>
                <div class="end-header">End Time</div>
                <div class="lyrics-header">Lyrics
                    <span v-if="props.lyricData.song_name && props.lyricData.artist_name">
                        for
                        {{ props.lyricData.artist_name }} -
                        {{ props.lyricData.song_name }}
                    </span>
                </div>
            </div>

            <div class="lyrics-rows">
                <form @submit.prevent="handleSubmit">
                    <div v-for="(line, index) in lyricsLines" :key="index">
                        <button @click.prevent="addNewLine(index)" class="add-btn">
                            ✚
                        </button>
                        <div class="lyrics-row">
                            <button @click.prevent="rewindTo(index)" class="rewind-btn">
                                ᐅ
                            </button>
                            <input type="number" v-model="line.timestamp" step="0.01" class="timestamp-input"
                                @keydown.enter.prevent="focusKeybinds" required placeholder="0.00">
                            <input type="number" v-model="line.timestampEnd" step="0.01" class="timestamp-input"
                                @keydown.enter.prevent="focusKeybinds" required placeholder="0.00">
                            <input type="text" v-model="line.content" class="lyrics-input" :class="computeClass(index)"
                                @keydown.enter.prevent="focusKeybinds"
                                placeholder="●●● (Leave Blank for a no-penalty pause)">
                            <button @click.prevent="removeLine(index)" class="remove-btn">
                                ✖
                            </button>
                        </div>
                        <button v-if="index === lyricsLines.length - 1" @click.prevent="addNewLine(index + 1)"
                            class="add-btn">
                            ✚
                        </button>
                    </div>
                    <button type="submit" id="submission-btn">Submit</button>
                </form>
            </div>
        </div>

        <div class="controls" id="keybinds">
            <button @click="cycleRate()" id="rate-changer">
                <div>
                    {{ uploadState.playbackRate }}x
                </div>
            </button>

            <button @click="toggleLoop()" id="toggle-btn">
                <div v-if="uploadState.ready && !uploadState.playing">
                    <span class="icon">
                        ⏵
                    </span>
                </div>
                <div v-if="uploadState.ready && uploadState.playing">
                    <span class="icon">
                        ⏸
                    </span>
                </div>
            </button>
            <button @click="nextLine()" id="line-jump">
                <div>
                    Enter
                    <br>(sync line)
                </div>
            </button>
        </div>
        <UploadYoutubeComponent ref="video" :video_id="props.video_id" />
    </main>
</template>

<style scoped>
form {
    scrollbar-width: none;
    /* thin, auto, or none */
    scrollbar-color: #888 #f1f1f1;
    /* thumb and track colors */
}


.upload-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.upload-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

#lyrics-table {
    /*border: 1px solid #444;*/
    /*border-radius: 4px;*/
    max-height: 500px;
    overflow: auto;
    position: relative;
    scroll-behavior: smooth;
    scrollbar-width: none;
    /*scrollbar-color: #888 #f1f1f1;*/
}

.table-header {
    display: grid;
    grid-template-columns: 50px 110px 110px 1fr;
    background-color: #333;
    padding: 10px;
    font-weight: bold;
}

.start-header {
    margin-left: 5px;
}

.lyrics-row {
    display: grid;
    grid-template-columns: 40px 100px 100px 1fr 50px 5px;
    padding: 10px;
    gap: 10px;
    /*border-bottom: 1px solid #444;*/
}

.timestamp-input {
    padding: 8px;
    border: 1px solid #444;
    border-radius: 4px;
    background-color: #333;
    color: white;
}

.lyrics-input {
    padding: 8px;
    border: 1px solid #444;
    border-radius: 4px;
    background-color: #333;
    color: white;
}

.lyrics-input::placeholder {
    color: #AAA;
}

.timestamp-input {
    width: 80px;
}

.remove-btn {
    background-color: #7C4B49;
    border: none;
    border-radius: 4px;
    color: coral;
    cursor: pointer;
    padding: 4px;
    transition: opacity 0.2s ease;
    opacity: 0%;
}

.remove-btn:hover {
    opacity: 70%;
}

.controls {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}

.add-btn {
    background-color: #4F5B43;
    border: none;
    border-radius: 4px;
    color: green;
    cursor: pointer;
    padding: 4px 8px;
    opacity: 0%;
    position: absolute;
    width: 50%;
    transition: opacity 0.2s ease;
    transform: translateY(-12px);
    left: 25%;
}

.add-btn:hover {
    opacity: 70%;
}

.rewind-btn {
    background-color: #4682B4;
    border: none;
    border-radius: 4px;
    color: white;
    cursor: pointer;
    /*padding: 4px 8px;*/
    padding: 8px;
    border: 1px solid #444;
    border-radius: 4px;
    opacity: 0%;
    transition: opacity 0.2s ease;
    /*transform: translate(-60px, 15px);*/
    /*transform: translateY(20px);*/
}

.rewind-btn:hover {
    opacity: 70%;
}

#toggle-btn {
    background-color: #2a2a2a;
    border: none;
    border-radius: 15px;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    width: 40vw;
    height: 80px;
    cursor: pointer;
}

#toggle-btn:active {
    background-color: #2f2f2f;
}

#toggle-btn:focus {
    outline: none;
}

#rate-changer {
    background-color: #2a2a2a;
    color: white;
    border: none;
    border-radius: 15px;
    position: absolute;
    left: 26%;
    transform: translateX(-50%);
    width: 6vw;
    height: 80px;
    cursor: pointer;
}

#rate-changer:active {
    background-color: #2f2f2f;
}

#line-jump {
    background-color: #2a2a2a;
    color: white;
    border: none;
    border-radius: 15px;
    position: absolute;
    left: 74%;
    transform: translateX(-50%);
    width: 6vw;
    height: 80px;
    cursor: pointer;
}

#line-jump:active {
    background-color: #2f2f2f;
}

#submission-btn {
    background-color: #2a2a2a;
    color: white;
    border: none;
    border-radius: 15px;
    margin-top: 20px;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    width: 10vw;
    height: 30px;
    cursor: pointer;
}

#submission-btn:active {
    background-color: #2f2f2f;
}

.icon {
    font-size: 60px;
    color: white;
    transform: translateY(-5px);
}

.previous {
    color: grey;
    font-size: 80%;
}

.previous::placeholder {
    color: #555;
}

.active {
    font-size: 125%;
    color: white;
}

.future {
    color: #BBB;
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
</style>
