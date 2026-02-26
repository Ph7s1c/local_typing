<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import pb from '@/services/pocketbase';

const router = useRouter();
const toast = useToast();
const songs = ref([]);
const isLoading = ref(true);

const fetchSongs = async () => {
    try {
        const records = await pb.collection('song_uploads').getList(1, 100);
        songs.value = records.items.map(record => {
            let songData = {};
            try {
                songData = typeof record.song_data === 'string'
                    ? JSON.parse(record.song_data)
                    : record.song_data;
            } catch (e) {
                console.error('Failed to parse song_data for record', record.id);
            }
            return {
                id: record.id,
                artist_name: songData.artist_name || 'Unknown Artist',
                song_name: songData.song_name || 'Unknown Song',
                created: record.created,
            };
        });
    } catch (error) {
        console.error('Error fetching songs:', error);
        toast.error(`Failed to load songs: ${error?.message || error}`);
    } finally {
        isLoading.value = false;
    }
};

const playGame = (id) => {
    router.push({ path: '/game', query: { id } });
};

onMounted(() => {
    fetchSongs();
});
</script>

<template>
    <main class="browse-container">
        <h1 class="browse-title">Saved Songs</h1>

        <div v-if="isLoading" class="lds-spinner">
            <div></div><div></div><div></div><div></div>
            <div></div><div></div><div></div><div></div>
            <div></div><div></div><div></div><div></div>
        </div>

        <div v-else-if="songs.length === 0" class="empty-state">
            <p>No songs saved yet.</p>
            <p>Go to <a href="/upload">Upload</a> to add your first song.</p>
        </div>

        <div v-else class="song-list">
            <div v-for="song in songs" :key="song.id" class="song-card">
                <div class="song-info">
                    <span class="artist-name">{{ song.artist_name }}</span>
                    <span class="song-name">{{ song.song_name }}</span>
                </div>
                <button class="play-button" @click="playGame(song.id)">
                    Play
                </button>
            </div>
        </div>
    </main>
</template>

<style scoped>
.browse-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

.browse-title {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 2rem;
    color: #ffffff;
}

.song-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.song-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #2d2d2d;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    border: 1px solid #3a3a3a;
}

.song-info {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}

.artist-name {
    font-size: 0.9rem;
    color: #888888;
}

.song-name {
    font-size: 1.1rem;
    color: #cccccc;
    font-weight: 500;
}

.play-button {
    background-color: #2596be;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.25rem;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.play-button:hover {
    background-color: #1d7a9e;
}

.play-button:active {
    background-color: #165f7a;
}

.empty-state {
    text-align: center;
    color: #888888;
    font-size: 1.2rem;
    margin-top: 4rem;
    line-height: 2;
}

.empty-state a {
    color: #2596be;
    text-decoration: underline;
}

/* Pure CSS Loader */
.lds-spinner {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    margin-top: 4rem;
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

.lds-spinner div:nth-child(1) { transform: rotate(0deg); animation-delay: -1.1s; }
.lds-spinner div:nth-child(2) { transform: rotate(30deg); animation-delay: -1s; }
.lds-spinner div:nth-child(3) { transform: rotate(60deg); animation-delay: -0.9s; }
.lds-spinner div:nth-child(4) { transform: rotate(90deg); animation-delay: -0.8s; }
.lds-spinner div:nth-child(5) { transform: rotate(120deg); animation-delay: -0.7s; }
.lds-spinner div:nth-child(6) { transform: rotate(150deg); animation-delay: -0.6s; }
.lds-spinner div:nth-child(7) { transform: rotate(180deg); animation-delay: -0.5s; }
.lds-spinner div:nth-child(8) { transform: rotate(210deg); animation-delay: -0.4s; }
.lds-spinner div:nth-child(9) { transform: rotate(240deg); animation-delay: -0.3s; }
.lds-spinner div:nth-child(10) { transform: rotate(270deg); animation-delay: -0.2s; }
.lds-spinner div:nth-child(11) { transform: rotate(300deg); animation-delay: -0.1s; }
.lds-spinner div:nth-child(12) { transform: rotate(330deg); animation-delay: 0s; }

@keyframes lds-spinner {
    0% { opacity: 1; }
    100% { opacity: 0; }
}
</style>
