<template>
    <div class="about-container">
        <div class="about-content">
            <section class="description">
                <h2>What is MelodyType?</h2>
                <p>MelodyType is an innovative typing game that combines your love for music with typing practice. Type
                    along with the lyrics of your favorite songs and improve your typing speed while having fun!</p>
            </section>

            <section class="how-it-works">
                <h2>How It Works</h2>
                <ul>
                    <li><strong>Select a Song:</strong> Choose from our library of songs or find your own with our
                        Youtube embed feature.</li>
                    <li><strong>Type to the Rhythm:</strong> As the song plays, lyrics appear on screen for you to type.
                    </li>
                    <li><strong>Stay in Sync:</strong> The music automatically pauses if you fall behind, resuming when
                        you catch up.</li>
                    <li><strong>Track Your Progress:</strong> See your typing speed (WPM), accuracy, and performance
                        history over time.</li>
                </ul>
            </section>

            <section class="features">
                <h2>Features</h2>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>Synchronized Lyrics</h3>
                        <p>The music adjusts to your typing speed, pausing when needed.</p>
                    </div>
                    <div class="feature-card">
                        <h3>Performance Tracking</h3>
                        <p>Detailed statistics to help you monitor your improvement.</p>
                    </div>
                    <div class="feature-card">
                        <h3>Diverse Song Library</h3>
                        <p>Songs across various genres and difficulty levels.</p>
                    </div>
                </div>
            </section>

            <section class="benefits">
                <h2>Benefits of MelodyType</h2>
                <ul>
                    <li>Improve typing speed and accuracy in an engaging way</li>
                    <li>Learn lyrics to your favorite songs</li>
                    <li>Enhance rhythm and timing skills</li>
                    <li>Make typing practice enjoyable rather than tedious</li>
                </ul>
            </section>

            <section class="get-started">
                <h2>Ready to Type to the Beat?</h2>
                <p>Jump right in and start improving your typing skills while jamming to your favorite tunes!</p>
                <div class="align-btn">
                    <router-link to="/" class="cta-button">Get Started</router-link>
                </div>
            </section>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AboutView',
    metaInfo: {
        title: 'About MelodyType - Type to the Rhythm of Music'
    }
}
</script>

<style scoped>
.about-content {
    border-radius: 10px;
    padding: 0rem 2rem 2rem 2rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1 {
    font-size: 2.5rem;
    /*color: #5f27cd;*/
    margin-bottom: 1.5rem;
    text-align: center;
}

h2 {
    font-size: 1.8rem;
    /*color: #4b7bec;*/
    margin: 1.5rem 0 1rem;
    border-bottom: 2px solid #f1f2f6;
    padding-bottom: 0.5rem;
}

section {
    margin-bottom: 2.5rem;
}

p {
    font-size: 1.1rem;
    line-height: 1.6;
    /*color: #2f3542;*/
}

ul {
    padding-left: 1.5rem;
}

li {
    margin-bottom: 0.8rem;
    font-size: 1.1rem;
    line-height: 1.5;
    /*color: #2f3542;*/
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.feature-card {
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.feature-card h3 {
    font-size: 1.4rem;
    /*color: #5f27cd;*/
    margin-bottom: 0.8rem;
}

.align-btn {
    text-align: center;
}

.cta-button {
    display: inline-block;
    /*background-color: #5f27cd;*/
    color: white;
    padding: 0.8rem 1.5rem;
    border-radius: 6px;
    font-weight: bold;
    text-decoration: none;
    font-size: 1.1rem;
    transition: background-color 0.3s ease;
    margin-top: 1rem;
}

.cta-button:hover {
    background-color: #2a2a2a;
}

@media (max-width: 768px) {
    .about-container {
        padding: 1rem;
    }

    .about-content {
        padding: 0rem 1.5rem 1.5rem 1.5rem;
    }

    h1 {
        font-size: 2rem;
    }

    h2 {
        font-size: 1.5rem;
    }

    .feature-grid {
        grid-template-columns: 1fr;
    }
}
</style>
