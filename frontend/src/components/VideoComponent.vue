<script setup>
import { ref } from 'vue';
import { useGameState } from '@/stores/gameState'
import { usePlayer, PlayerState } from '@vue-youtube/core';
import { useToast } from 'vue-toastification';
import TypingComponent from '../components/TypingComponent.vue'

const props = defineProps(['data'])
const toast = useToast();

const gameData = props.data;

const gameState = useGameState();

const youtube = ref();

const { instance, onReady, onStateChange, onError } = usePlayer(gameData.video_id, youtube, {
    playerVars: {
        autoplay: 1,
        mute: 1,
    },
    cookie: false,
    width: 300,
    height: 200,
})

onError(
    (event) => {
        switch (event.data) {
            case 2:
                toast.error("Invalid video ID.");
                break;
            case 5:
                toast.error("HTML5 error, try switching browser.");
                break;
            case 100:
                toast.error("This video was removed/privated.");
                break;
            case 101:
            case 150:
                toast.error("This video can't be embedded. Sorry, can't fix this.");
                break;
        }
    },
);

onReady(
    (event) => {
        event.target.mute();
        event.target.playVideo();
        event.target.pauseVideo();
        event.target.unMute();
        gameState.totalVideoSeconds = event.target.getDuration();
        gameState.ready = true;
        //event.target.setPlaybackRate(2);
        // TODO: Remove this comment, it's for debugging
    },
);

onStateChange((event) => {
    //gameState.currentVideoSeconds = instance.value?.getCurrentTime();

    //console.log(instance.value?.getCurrentTime());
    //console.log(instance.value?.getVideoLoadedFraction());
    //console.log(event.data);
    switch (event.data) {
        case PlayerState.PLAYING:
            //console.log("I'M JUST PLAYING LIL BRO");
            if (!gameState.playing) {
                instance.value?.pauseVideo();
            }
            break;
        case PlayerState.PAUSED:
            //console.log("PAUSE, THAT'S A LIL FRUITY BRO");
            if (gameState.videoPlaying) {
                gameState.playing = false;
                gameState.videoPlaying = false;
            }
            break;
        case PlayerState.BUFFERING:
            // TODO: Calculate Remaining video loaded fraction. RN, this considers the whole video
            //if (instance.value?.getVideoLoadedFraction() < 0.03) {
            //    instance.value?.pauseVideo();
            //    gameState.playing = false;
            //    toast.warning("Video is buffering, check your connection.");
            //    console.log("IT'S BUFFERING. WHO DA HELL ON DA WIFI?");
            //}
            break;
        case PlayerState.ENDED:
            gameState.finished = true;
            //console.log("IT'S JOEVER GANG");
            break;
        case PlayerState.CUED:
            //console.log("I'M ALL CUED UP");
            break;
        case PlayerState.UNSTARTED:
            //console.log("DON'T EVEN START WITH ME");
            break;
        default:
            //console.log("Dang bro, this shouldn't happen");
            break;
    }
});

const fetchCurrentTime = () => {
    return (instance.value?.getCurrentTime());
}

const playVideo = () => {
    instance.value?.playVideo();
}

const pauseVideo = () => {
    instance.value?.pauseVideo();
}

const jumpTo = (seconds) => {
    instance.value?.seekTo(seconds);
}

defineExpose({
    fetchCurrentTime,
    playVideo,
    pauseVideo,
    jumpTo,
});
</script>

<template>
    <div ref="youtube" style="opacity: 0; position: relative; right: 100%;" id="player" />
</template>
