import { defineStore } from 'pinia'

export const useGameState = defineStore('gameState', {
    state: () => ({
        // Game state toggles
        ready: false,
        playing: false,
        videoPlaying: false,
        finished: false,

        // Nate's line countdown
        lineCountdown: 0,

        // Game options
        canAdvance: true,
        skippableSection: true,
        songEndable: false,

        // Game Cursor 
        currentLineIndex: 0,

        // Game Progress
        currentVideoSeconds: 0,

        // Game Statistics
        totalVideoSeconds: 0,
        totalCorrect: 0,
        totalErrors: 0,
        timeSpentTyping: 0,

        // Timer for tracking WPM
        startTime: null,
    }),
    getters: {
        totalKeystrokes: (state) => state.totalErrors + state.totalCorrect,
        finalWPM: (state) => state.totalCorrect * 80 / (5 * state.timeSpentTyping),
        finalAccuracy: (state) => state.totalCorrect / state.totalKeystrokes,
    },
    actions: {
        resetState() {
            this.ready = false;
            this.playing = false;
            this.videoPlaying = false;
            this.finished = false;
            this.canAdvance = true;
            this.skippableSection = true;
            this.songEndable = false;
            this.currentLineIndex = 0;
            this.currentVideoSeconds = 0;
            this.totalVideoSeconds = 0;
            this.totalCorrect = 0;
            this.totalErrors = 0;
            this.timeSpentTyping = 0;
            this.startTime = null;
        },

        fetchClockSeconds() {
            return parseFloat((performance.now() / 1000).toFixed(2));
        },

        startStopwatch() {
            this.startTime = this.fetchClockSeconds();
        },

        getDiff() {
            if (!this.startTime) {
                this.startTime = this.fetchClockSeconds();
            }
            let endTime = this.fetchClockSeconds();
            //console.log(`Start ${this.startTime}, End ${endTime}, Diff ${(endTime - this.startTime).toFixed(2)}`);
            return parseFloat((endTime - this.startTime).toFixed(2));
        },
    },
})
