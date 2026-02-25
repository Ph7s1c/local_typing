<script setup>
import { useGameState } from '@/stores/gameState'
import { onMounted, inject } from 'vue';

const props = defineProps(['data'])

const gameData = props.data.lyrics;

const gameState = useGameState();

const lines = gameData;
var activeLineIndex = 0;
var activeLetterIndex = 0;

const globalSkipLine = inject('drill');

gameData.forEach(line => {
    line.state = 'future';
    line.letters = [];
    line.content.split('').forEach(char => {
        line.letters.push({ char: char, state: 'normal', counted: false, });
    });
    if (line.content.length === 0) {
        line.letters.push({ char: '●', state: 'spacer', counted: false });
        line.letters.push({ char: '●', state: 'spacer', counted: false });
        line.letters.push({ char: '●', state: 'spacer', counted: false });
    }
});

var activeLine = lines[activeLineIndex];
var activeLetter = activeLine.letters[activeLetterIndex];

const updateLines = () => {
    lines.forEach((line, index) => {
        if (index <= activeLineIndex - 2) {
            line.state = 'past';
        } else if (index === activeLineIndex - 1) {
            line.state = 'previous';
        } else if (index === activeLineIndex) {
            line.state = 'current';
        } else if (index === activeLineIndex + 1) {
            line.state = 'up-next';
        } else {
            line.state = 'future';
        }
    });
}
updateLines();

const advance = () => {
    if (activeLineIndex >= lines.length - 1) {
        return;
    }
    activeLineIndex++;
    activeLine = lines[activeLineIndex];
    updateLines();
    activeLetterIndex = 0;
    activeLetter = activeLine.letters[activeLetterIndex];
    gameState.currentLineIndex = activeLineIndex;
    if (activeLine.content.length === 0) {
        gameState.skippableSection = true;
    } else {
        gameState.skippableSection = false;
    }
    setTimeout(() => { try { updateCaret() } catch (error) { } }, 50);
    setTimeout(() => { try { updateCaret() } catch (error) { } }, 150);
    setTimeout(() => { try { updateCaret() } catch (error) { } }, 300);
};

const skipLine = () => {
    for (let i = activeLetterIndex; i < activeLine.letters.length; i++) {
        if (activeLine.letters[i].state != 'spacer') {
            activeLine.letters[i].state = 'incomplete';
        }
    }
    if (activeLineIndex >= lines.length - 1) {
        //gameState.finished = true;
        return;
    }
    advance();
};
globalSkipLine.value = skipLine;

const reverse = () => {
    if (activeLineIndex <= 0) {
        return;
    }
    clearLetters();
    activeLineIndex--;
    activeLine = lines[activeLineIndex];
    updateLines();
    clearLetters();
    activeLetterIndex = 0;
    activeLetter = activeLine.letters[activeLetterIndex];
    setTimeout(() => { try { updatecaret() } catch (error) { } }, 50);
    setTimeout(() => { try { updatecaret() } catch (error) { } }, 150);
    setTimeout(() => { try { updatecaret() } catch (error) { } }, 300);
};

const clearLetters = () => {
    // Wipe the letters array and repopulate it
    activeLine.letters.length = 0;
    activeLine.content.split('').forEach(char => {
        activeLine.letters.push(
            { char: char, state: 'normal' });
    });
};

onMounted(() => {
    const typingDiv = document.getElementById('typing-area');
    const typingInput = document.getElementById('typingInput');

    typingDiv.addEventListener('click', () => {
        typingInput.focus();
    });

    const getCaretOffset = (lineIndex, charIndex, onRight) => {
        const caret = document.getElementById('anchor-caret');
        const lineElement = document.querySelectorAll('.lyrics-line')[lineIndex];
        if (lineElement && caret) {
            const characterElements = lineElement.querySelectorAll('.letter');
            const charElement = characterElements[charIndex];

            if (charElement) {
                // Get the character's position relative to the line
                const charRect = charElement.getBoundingClientRect();
                const caretRect = caret.getBoundingClientRect();
                if (onRight) {
                    return {
                        deltaX: charRect.right - caretRect.left,
                        deltaY: charRect.top - caretRect.top,
                    };
                } else {
                    return {
                        deltaX: charRect.left - caretRect.left,
                        deltaY: charRect.top - caretRect.top,
                    };
                }
            }
        }

        return { deltaX: 0, deltaY: 0 }; // Default position if something goes wrong
    };

    const updateCaret = async () => {
        const caret = document.getElementById('caret');
        if (!caret) {
            return;
        }
        await new Promise(resolve => {
            // Use requestAnimationFrame to schedule the update after the DOM has rendered
            requestAnimationFrame(() => {
                if (activeLetterIndex < activeLine.letters.length) {
                    let offsets = getCaretOffset(activeLineIndex, activeLetterIndex, false);
                    caret.style.transform = `translateX(${offsets.deltaX}px) translateY(${offsets.deltaY}px)`;
                } else {
                    let offsets = getCaretOffset(activeLineIndex, activeLetterIndex - 1, true);
                    caret.style.transform = `translateX(${offsets.deltaX}px) translateY(${offsets.deltaY}px)`;
                }
                // Reset the blink animation
                caret.style.animation = 'none';
                caret.offsetHeight; // Trigger a reflow
                caret.style.animation = 'blink 1.2s step-end infinite';

                resolve();  // Resolve the promise once the DOM update is complete
            });
        });
    };

    const insertExtraChar = (character) => {
        activeLine.letters.splice(activeLetterIndex, 0, { char: character, state: 'extra' });
        activeLetterIndex++;
        activeLetter = activeLine.letters[activeLetterIndex];
        gameState.totalErrors++;
        updateCaret();
    };

    const backspaceExtraChar = () => {
        activeLine.letters.splice(activeLetterIndex - 1, 1);
        activeLetterIndex--;
        activeLetter = activeLine.letters[activeLetterIndex];
        updateCaret();
    };

    const scoreKey = (keyInput) => {
        if (keyInput === activeLetter.char) {
            activeLetter.state = 'correct';
            if (!activeLetter.counted) {
                gameState.totalCorrect++;
                activeLetter.counted = true;
            }
        } else {
            activeLetter.state = 'incorrect';
            gameState.totalErrors++;
        }
    };

    const clearIncomplete = () => {
        while (activeLetterIndex >= 1) {
            var prevLetter = activeLine.letters[activeLetterIndex - 1];
            if (prevLetter.state == 'incomplete') {
                activeLetterIndex--;
                activeLetter = activeLine.letters[activeLetterIndex];
                activeLetter.state = 'normal';
            } else {
                return;
            }
        }
        updateCaret();
    };

    const advanceKey = () => {
        activeLetterIndex++;
        activeLetter = activeLine.letters[activeLetterIndex];
        updateCaret();
    };

    const reverseKey = () => {
        if (activeLetterIndex >= 1) {
            let prevLetter = activeLine.letters[activeLetterIndex - 1];
            if (prevLetter.state == 'extra') {
                backspaceExtraChar();
                updateCaret();
                return;
            }
            if (prevLetter.state == 'incomplete') {
                clearIncomplete();
                updateCaret();
                return;
            }
        }
        if (activeLetterIndex <= 0) {
            return;
        }
        activeLetterIndex--;
        activeLetter = activeLine.letters[activeLetterIndex];
        activeLetter.state = 'normal';
        updateCaret();
    };

    const nextWordExists = () => {
        var hitSpace = false;
        var hitWord = false;
        for (let i = activeLetterIndex + 1; i < activeLine.letters.length; i++) {
            if (activeLine.letters[i].char === '\u0020') {
                hitSpace = true;
            }
            if (hitSpace && (activeLine.letters[i].char === '\u0020')) {
                hitWord = true;
            }
        }
        return hitWord;
    };

    const skipWord = () => {
        for (let i = activeLetterIndex; i < activeLine.letters.length; i++) {
            activeLetter.state = 'incomplete';
            advanceKey();
            if (activeLine.letters[i].char === '\u0020') {
                break;
            }
        }
        updateCaret();
    };

    const reverseWord = () => {
        reverseKey();
        for (let i = activeLetterIndex - 1; i >= 0; i--) {
            if (activeLine.letters[i].char === '\u0020') {
                break;
            }
            reverseKey();
        }
        updateCaret();
    };

    document.onblur = () => {
        gameState.playing = false;
    }

    typingInput.onblur = () => {
        focusCountdown();
        //gameState.playing = false;
    }

    typingInput.onfocus = () => {
        try {
            abortCountdown();
        } catch (error) {
            // nah xd
        }
    }

    let countdownTimeouts = [];

    const focusCountdown = () => {
        countdownTimeouts.push(setTimeout(() => {
            gameState.playing = false;
        }, 1000));
    };

    const abortCountdown = () => {
        countdownTimeouts.forEach(timeout => clearTimeout(timeout));
        countdownTimeouts = [];
    };

    typingInput.addEventListener('keydown', (event) => {
        const key = event.key;

        if (!gameState.playing || gameState.finished) {
            return;
        }

        event.preventDefault();

        if (activeLine.content.length === 0) {
            if (event.key === ' ') {
                if (activeLineIndex === lines.length - 1) {
                    skipLine();
                    gameState.finished = true;
                    return;
                }
                if (gameState.canAdvance) {
                    //skipLine();
                }
            }
            return;
        }

        switch (key) {
            case 'Backspace':
                if (event.ctrlKey || event.altKey) {
                    reverseWord();
                } else {
                    reverseKey();
                }
                break;
            case ' ':
                if (event.ctrlKey || event.altKey) {
                    gameState.playing = false;
                }
                if (activeLetterIndex >= activeLine.letters.length - 1) {
                    if (activeLine.content.length > 0) {
                        let diff = gameState.getDiff();
                        gameState.timeSpentTyping += parseFloat(diff.toFixed(2));

                        gameState.videoPlaying = true;
                        skipLine();
                        gameState.startStopwatch();
                    }
                    break;
                }
                if (activeLetter.char === '\u0020') {
                    scoreKey('\u0020');
                    advanceKey();
                } else {
                    if (nextWordExists()) {
                        if (activeLetterIndex >= 1) {
                            var prevLetter = activeLine.letters[activeLetterIndex - 1];
                            if (prevLetter.char !== '\u0020') {
                                gameState.totalErrors++;
                                skipWord();
                            }
                        }
                    }
                    else {
                        //skipLine();
                        break;
                    }
                }
                break;
            case 'Enter':
                if ((activeLetterIndex + 1) / activeLine.letters.length >= 0.4) {
                    if (activeLineIndex === lines.length - 1) {
                        skipLine();
                        gameState.startStopwatch();
                        gameState.finished = true;
                        break;
                    }

                    if (activeLine.letters.length > 0) {
                        let diff = gameState.getDiff();
                        gameState.timeSpentTyping += parseFloat(diff.toFixed(2));
                    }

                    if (activeLineIndex === lines.length - 1) {
                        skipLine();
                        gameState.finished = true;
                        break;
                    }

                    gameState.videoPlaying = true;
                    skipLine();
                    gameState.startStopwatch();
                }
                if (gameState.canAdvance) {
                    //skipLine();
                }
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
            case 'AudioVolumeUp':
            case 'AudioVolumeDown':
            case 'AudioVolumeMute':
            case 'Escape':
                break;
            default:
                if (activeLetterIndex >= activeLine.letters.length) {
                    insertExtraChar(key);
                } else {
                    if (activeLetter.char === '\u0020') {
                        insertExtraChar(key);
                    }
                    else {
                        scoreKey(key);
                        advanceKey();
                    }
                }
        }
    });
});

</script>

<template>
    <div id="typing-area">
        <input id="typingInput" autofocus>
        <div v-for="(line, lineIndex) in gameData" :class="[line.state]" class="lyrics-line">
            <span v-if="lineIndex === activeLineIndex" id="anchor-caret">|</span>
            <span v-if="lineIndex === activeLineIndex" :class="(line.content.length !== 0) ? 'visible' : 'invisible'"
                id="caret">|</span>
            <div v-for="(letter, charIndex) in line.letters" :key="charIndex" class="letter"
                :class="line.letters[charIndex].state">
                {{ letter.char === ' ' ? '\u00A0' : letter.char }}
            </div>
        </div>
    </div>
</template>

<style scoped>
div {
    text-align: center;
    font-family: "Source Code Pro", monospace;
    font-weight: 500;
}

#typing-area {
    outline: none;
    margin: 0 auto;
    padding: 10px;
    width: 80%;
    height: 15rem;
    overflow-y: hidden;
}

#typingInput {
    cursor: none;
    opacity: 0;
    pointer-events: none;
}

.lyrics-line {
    margin: 1rem;
    transition: all 0.3s ease;
}

.lyrics-line.past {
    opacity: 0%;
    transform: scale(0, 0);
    margin: 0rem;
    font-size: 0%;
}

.lyrics-line.previous {
    opacity: 50%;
}

.lyrics-line.current {
    font-size: 200%;
}

.lyrics-line.up-next {
    opacity: 70%;
    font-size: 150%;
}

.lyrics-line.future {
    opacity: 30%;
    font-size: 80%;
}

.letter {
    display: inline-block;
    /* Allows letters to be displayed inline */
}

.letter.correct {
    color: green;
}

.letter.incorrect {
    color: red;
}

.letter.extra {
    color: Salmon;
    opacity: 50%;
}

.letter.incorrect-space {
    background: red;
    opacity: 20%;
}

.letter.incomplete {
    color: gray;
}

.letter.spacer {
    color: gray;
    margin-left: 3px;
    margin-right: 3px;
}

#caret {
    display: inline-block;
    width: 0;
    height: 0.8rem;
    position: relative;
    left: -8px;
    top: -4px;
    transition: all 0.1s ease-out;
    animation: blink 1.2s step-end infinite;
}

.invisible {
    opacity: 0;
}

#anchor-caret {
    display: inline-block;
    opacity: 0;
    width: 0;
    height: 0.8rem;
    position: relative;
}

@keyframes blink {
    50% {
        opacity: 0;
    }
}
</style>

<style>
@keyframes blink {
    50% {
        opacity: 0;
    }
}
</style>
