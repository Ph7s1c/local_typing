import { defineStore } from 'pinia'

export const useUploadState = defineStore('uploadState', {
    state: () => ({ 
        ready: false,
        playing: false,
        currentLineIndex: 0,
        currentSeconds: 0,
        totalVideoSeconds: 0,
        playbackRate: 1,
    }),
    actions: {
    },
})
