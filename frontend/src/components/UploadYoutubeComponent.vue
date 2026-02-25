<script setup>
import { ref, onUnmounted } from 'vue';
import { useUploadState } from '@/stores/uploadState'
import { usePlayer, PlayerState } from '@vue-youtube/core';
import { useToast } from 'vue-toastification';
import TypingComponent from '../components/TypingComponent.vue'

const props = defineProps(['video_id'])
const toast = useToast();

const uploadState = useUploadState();

const youtube = ref();

const { instance, onReady, onStateChange, onError, onPlaybackRateChange } = usePlayer(props.video_id, youtube, {
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
        console.log("READY");
        event.target.mute();
        event.target.playVideo();
        event.target.pauseVideo();
        event.target.unMute();
        uploadState.totalVideoSeconds = event.target.getDuration();
        uploadState.ready = true;
    },
);

onStateChange((event) => {
    uploadState.currentSeconds = instance.value?.getCurrentTime();

    console.log(instance.value?.getCurrentTime());
    console.log(instance.value?.getVideoLoadedFraction());
    console.log(event.data);
    switch (event.data) {
        case PlayerState.PLAYING:
            //console.log("I'M JUST PLAYING LIL BRO");
            break;
        case PlayerState.PAUSED:
            //console.log("PAUSE, THAT'S A LIL FRUITY BRO");
            break;
        case PlayerState.BUFFERING:
            //console.log("IT'S BUFFERING. WHO DA HELL ON DA WIFI?");
            break;
        case PlayerState.ENDED:
            //console.log("IT'S JOEVER GANG");
            uploadState.playing = false;
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

onPlaybackRateChange((event) => {
    uploadState.playbackRate = event.data;
});

const unsubscribe = uploadState.$subscribe((mutation, state) => {
    //console.log('State changed:', state);
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

const setPlaybackRate = (speed) => {
    instance.value?.setPlaybackRate(speed);
}

defineExpose({
    fetchCurrentTime,
    playVideo,
    pauseVideo,
    jumpTo,
    setPlaybackRate,
});

onUnmounted(() => {
    unsubscribe();
});
</script>

<template>
    <div ref="youtube" style="opacity: 0; position: relative; right: 100%;" id="player" />
</template>
