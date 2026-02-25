<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { useGameState } from '@/stores/gameState'
import GameComponent from '../components/GameComponent.vue'
import pb from '@/services/pocketbase';

const route = useRoute();
const router = useRouter();
const gameId = ref(route.query.id);
const capSetting = ref(route.query.caps);
const specialCharSetting = ref(route.query.schars);
const accentedCharSetting = ref(route.query.foreign);
const apostropheSetting = ref(route.query.apo);
const gameData = ref(null);
const toast = useToast();
const gameState = useGameState();
const settingsShown = ref(false);

const redirectToHome = () => {
    router.push('/');
};

const applyGameSettings = () => {
    if (!capSetting.value) {
        gameData.value.lyrics.forEach((element) => {
            let newContent = "";
            for (let i = 0; i < element.content.length; i++) {
                let char = element.content[i];
                if (char >= 'A' && char <= 'Z') {
                    newContent += char.toLowerCase();
                } else {
                    newContent += char;
                }
            }
            element.content = newContent;
        });
    }
    if (!specialCharSetting.value) {
        // Regex including '
        //const specialChars = /[",.+'`;~!@#$%^&*()_+{}\[\]:;<>\/?\\-]/;
        const specialChars = /[",.+;`~!@#$%^&*()_+{}\[\]:;<>\/?\\-]/;
        gameData.value.lyrics.forEach((element) => {
            let newContent = "";
            for (let i = 0; i < element.content.length; i++) {
                let char = element.content[i];
                if (!specialChars.test(char)) {
                    newContent += char;
                }
            }
            element.content = newContent;
        });
    }
    if (!accentedCharSetting.value) {
        gameData.value.lyrics.forEach(element => {
            let newContent = "";
            for (let i = 0; i < element.content.length; i++) {
                let char = element.content[i];
                char = char
                    .normalize("NFD")
                    .replace(/[\u0300-\u036f]/g, ""); // Remove accents
                newContent += char;
            }
            element.content = newContent;
        });
    }
    if (apostropheSetting.value === "off") {
        gameData.value.lyrics.forEach(element => {
            let newContent = "";
            for (let i = 0; i < element.content.length; i++) {
                let char = element.content[i];
                if (char != "'") {
                    newContent += char;
                }
            }
            element.content = newContent;
        });
    }
}

const fetchGameData = async (id) => {
    try {
        const gameDetails = await pb.collection('song_uploads').getOne(id, { fields: 'song_data' });
        gameData.value = gameDetails.song_data;
        applyGameSettings();
    } catch (error) {
        if (error.response) {
            switch (error.response.status) {
                case 404:
                    toast.error('No data was found for that ID');
                    redirectToHome();
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
        gameData.value = null;
    }
};

onMounted(() => {
    if (gameId.value) {
        console.log(`The game id: ${gameId.value}`);
        fetchGameData(gameId.value);
    } else {
        toast.error('No game ID found. Redirecting to home...');
        redirectToHome();
    }
});

watch(gameData, (newValue) => {
    if (!newValue) {
        toast.error("The game state seems to have broken, try refreshing.");
    }
});

onUnmounted(() => {
    gameState.resetState();
});
</script>

<template>
    <div class="game-view">
        <div v-if="gameData">
            <GameComponent :data="gameData" :upload_id="gameId" />
        </div>

        <div v-else>
            <h1>Loading game data...</h1>
        </div>
    </div>
</template>

<style scoped>
h1 {
    text-align: center;
}
</style>
