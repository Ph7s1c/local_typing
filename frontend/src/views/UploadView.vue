<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import pb from '@/services/pocketbase';

const router = useRouter();
const toast = useToast();
const inputRef = ref(null);
const isLoading = ref(false);

const fetchData = async (song_id) => {
    isLoading.value = true;

    try {
        const unlabeledSongs = await pb.collection('unlabeled_songs').getFullList({
            filter: `song_id = "${song_id}"`,
        });
        return unlabeledSongs;
    } catch (error) {
        console.error('Error fetching song lyrics:', error);
        toast.error('Database query failed!');
        isLoading.value = false;
    }
}

const createData = async (song_id) => {
    try {
        const response = await fetch(
            `${import.meta.env.VITE_LYRICS_API_URL}/plain/?video_id=${song_id}`
        );
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.log("Network / database error");
        throw error;
    }
};

const displayData = async (data, video_id) => {
    const resolvedData = await data;
    if (resolvedData === undefined) {
        isLoading.value = false;
        return
    }

    const numEntries = resolvedData.length;
    if (numEntries === 0) {
        try {
            const response = await createData(video_id);
            router.push({ path: '/upload_song', query: { lyric_id: response.upload_id, song_id: video_id } });
        } catch (error) {
            toast.warning('Failed to fetch lyrics! Try uploading your custom ones.');
            router.push({ path: '/upload_song', query: { song_id: video_id } });
        }
        return
    } else if (numEntries === 1) {
        const entryId = resolvedData[0].id;
        router.push({ path: '/upload_song', query: { lyric_id: entryId, song_id: video_id } });
    } else {
        //TODO: List possible lyrics versions
        const entryId = resolvedData[numEntries - 1].id;
        router.push({ path: '/upload_song', query: { lyric_id: entryId, song_id: video_id } });
    }
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
</script>

<template>
    <main>
        <div class="informational">
            Use the Uploader tool if we can't find your song
            <br/>
            <br/>
            Go to
            <a href="https://youtube.com/" target="_blank">
                 youtube.com 
            </a>
            to search for a song
            <br/>
            <br/>
            with the format (artist name) - (song name) 
            <br/>
            <br/>
            Right click and copy the link address

        </div>
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
        <div v-else>
            <div class="linkBox">
                <form @submit.prevent="handleSubmit">
                    <input ref="inputRef" type="text" name="link" placeholder="Upload a YouTube link" autocorrect="off"
                        autocapitalize="none">
                    <button type="submit">
                        <img src="@/assets/right_arrow.svg" width="48" height="48" alt="Play">
                    </button>
                </form>
            </div>
        </div>
    </main>
</template>

<style scoped>
.informational {
    position: relative;
    left: 50%;
    transform: translateX(-50%);
    font-size: 150%;
    text-align: center;
    max-width: 80%;
}

.linkBox {
    position: absolute;
    /* Position it absolutely within the container */
    left: 50%;
    transform: translateX(-50%);
}

form {
    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: 0;
    margin-top: 100px;
}

form button {
    background-color: transparent;
    border: none;
    padding: 10px;
    cursor: pointer;
}

form input {
    border: none;
    background-color: #2d2d2d;
    font-size: 2.5rem;
    padding: 10px;
    color: #cccccc;
    height: 3rem;
    margin: auto 0;
    width: 550px;
}

input::placeholder {
    color: gray;
    font-style: italic;
}

input:focus {
    outline: none;
}

.redirect {
    text-align: center;
    font-size: 200%;
    margin-top: 7%;
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
