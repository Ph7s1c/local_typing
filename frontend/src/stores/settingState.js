import { defineStore } from 'pinia'

export const useSettingState = defineStore('settingState', {
    state: () => ({
        currentMode: "Line Stop", 

    }),
    getters: {
    },
    actions: {
        cycleMode() {
            let modes = ["Line Stop", "Line Skip", "No Sync"]; //, "Line Pause (5s)", "Line Pause (3s)"];
            let currentIndex = modes.indexOf(this.currentMode);
            if (currentIndex === modes.length - 1) {
                this.currentMode = modes[0];
            } else {
                this.currentMode = modes[currentIndex + 1];
            }
        },

    },
})
