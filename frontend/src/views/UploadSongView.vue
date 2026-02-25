<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { useUploadState } from '@/stores/uploadState'
import EditorComponent from '@/components/EditorComponent.vue'
import pb from '@/services/pocketbase';

const route = useRoute();
const router = useRouter();
const songId = ref(route.query.song_id);
const lyricId = ref(route.query.lyric_id);
const lyricData = ref(null);
let formShown = ref(false);
const toast = useToast();
const uploadState = useUploadState();

// Form data
const songName = ref('');
const artistName = ref('');
const lyrics = ref('');

const redirectToUpload = () => {
    router.push('/upload');
};

const fetchUnlabeledLyrics = async (id) => {
    try {
        const lyricDetails = await pb.collection('unlabeled_songs').getOne(id, { fields: 'song_data' });
        lyricData.value = lyricDetails.song_data;
    } catch (error) {
        if (error.response) {
            switch (error.response.status) {
                case 404:
                    toast.error('No data was found for that ID');
                    redirectToUpload();
                    break;
                case 400:
                    toast.error('Bad request. Please check your input.');
                    break;
                case 401:
                case 403:
                    toast.error('You are not authorized to access this data.');
                    break;
                case 422:
                    toast.error('The request could not be processed due to invalid data.');
                    break;
                case 500:
                    toast.error('An error occurred on the server.');
                    break;
                default:
                    toast.error('An error occurred. Please try again later.');
                    break;
            }
        } else {
            toast.error('Error fetching game details, try refreshing.');
        }
        lyricData.value = null;
    }
};

if (lyricId.value) {
    console.log(`The lyric id: ${lyricId.value}`);
    fetchUnlabeledLyrics(lyricId.value);
} else {
    if (!songId.value) {
        toast.error('No song id found.');
        redirectToUpload();
    }
    formShown.value = true;
    // Create a form where users can either enter custom, query the lyric api, or go home
    //console.log("TODO: Add a form input for custom lyrics");
}

//Form scripts
const handleSubmit = () => {
    const cleanedLyrics = lyrics.value.replace(/\n{3,}/g, '\n\n').trim();

    const lyricsArray = cleanedLyrics.split('\n').map(line => ({ content: line }));

    lyricData.value = {
        video_id: songId.value,
        artist_name: artistName.value,
        song_name: songName.value,
        lyrics: lyricsArray
    };

    formShown.value = false;
}

</script>

<template>
    <div class="game-view">
        <div v-if="formShown">
            <h1>Enter Custom Lyrics</h1>

            <form @submit.prevent="handleSubmit">
                <div>
                    <input type="text" id="artistName" v-model="artistName" placeholder="Artist name" required />
                </div>
                <div>
                    <input type="text" id="songName" v-model="songName" placeholder="Song name" required />
                </div>
                <div>
                    <textarea id="lyrics" v-model="lyrics" placeholder="Enter lyrics, separate lines with newlines"
                        rows="10" cols="30"></textarea>
                </div>
                <button type="submit">Submit</button>
            </form>
        </div>
        <div v-else>
            <div v-if="lyricData">
                <EditorComponent :video_id="songId" :lyricData="lyricData" />
            </div>

            <div v-else>
                <h1>Loading lyrics...</h1>
            </div>
        </div>
    </div>
</template>

<style scoped>
h1,
form {
    text-align: center;
}

form input {
    border: none;
    background-color: #2d2d2d;
    font-size: 1.5rem;
    padding: 8px;
    color: #cccccc;
    height: 3rem;
    width: 300px;
    margin: 10px;
}

form button {
    background-color: transparent;
    border: none;
    padding: 10px;
    cursor: pointer;
    color: #cccccc;
}

textarea {
    border: none;
    background-color: #2d2d2d;
    font-size: 1rem;
    padding: 10px;
    color: #cccccc;
    height: 20rem;
    margin: auto 0;
    width: 30rem;
}

input::placeholder,
textarea::placeholder {
    color: gray;
    font-style: italic;
}

input:focus,
textarea:focus {
    outline: none;
}
</style>
