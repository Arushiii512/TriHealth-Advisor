// Navigation Scroll Function
function scrollToAnalysis() {
    document.getElementById('analysis').scrollIntoView({ behavior: 'smooth' });
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('symptom-form');
    const input = document.getElementById('symptom-input');
    const submitBtn = document.getElementById('submit-btn');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('error-message');
    const resultsWrapper = document.getElementById('results-wrapper');
    const treatmentCards = document.getElementById('treatment-cards');

    // UI elements to update
    const predictedSymptomBadge = document.getElementById('predicted-symptom');
    const recommendedTreatmentBadge = document.getElementById('recommended-treatment');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const text = input.value.trim();
        if (!text) return;

        // Reset UI state
        errorMessage.classList.add('hidden');
        resultsWrapper.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Analyzing...';

        try {
            const preferences = {
                speed: parseInt(document.getElementById('speed-slider').value, 10),
                safety: parseInt(document.getElementById('safety-slider').value, 10),
                cost: parseInt(document.getElementById('cost-slider').value, 10),
                effectiveness: parseInt(document.getElementById('effectiveness-slider').value, 10)
            };

            // Make POST request to Flask API
            const response = await fetch('http://127.0.0.1:5000/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: text,
                    preferences: preferences
                })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();

            // Render Results
            renderResults(data);

        } catch (error) {
            console.error('Error fetching prediction:', error);
            errorMessage.textContent = error.message.startsWith('API Error:') ? error.message : 'Could not connect to the local Flask API. Make sure the backend is running on port 5000.';
            errorMessage.classList.remove('hidden');
        } finally {
            loader.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Analyze Symptoms';
        }
    });

    function renderResults(data) {
        // 1. Set Predicted Symptom and Recommendation
        predictedSymptomBadge.textContent = data.predicted_symptom;
        recommendedTreatmentBadge.textContent = data.top_scoring_example || 'Unavailable';

        // 2. Clear previous cards
        treatmentCards.innerHTML = '';

        // 3. Render Treatment Cards
        const systems = ['Allopathy', 'Ayurveda', 'Homeopathy'];

        systems.forEach(sys => {
            const description = data.treatment_details?.[sys] || 'No information available in this demo.';
            const criteria = data.detailed_criteria[sys] || {};
            const score = data.comparison_scores[sys] || 0;
            const isBest = sys === data.top_scoring_example;

            const card = document.createElement('div');
            card.className = `treatment-card ${isBest ? 'best-choice' : ''}`;

            let bestBadgeHtml = isBest ? `<div class="best-badge">Highest illustrative score</div>` : '';

            card.innerHTML = `
                ${bestBadgeHtml}
                <div class="card-title">${sys}</div>

                <ul class="metric-list">
                    <li class="metric-item">
                        <span class="metric-label">Speed</span>
                        <span class="metric-value">${criteria.Speed || 'N/A'}/10</span>
                    </li>
                    <li class="metric-item">
                        <span class="metric-label">Safety</span>
                        <span class="metric-value">${criteria.Safety || 'N/A'}/10</span>
                    </li>
                    <li class="metric-item">
                        <span class="metric-label">Cost</span>
                        <span class="metric-value">${criteria.Cost || 'N/A'}/10</span>
                    </li>
                    <li class="metric-item">
                        <span class="metric-label">Effectiveness</span>
                        <span class="metric-value">${criteria.Effectiveness || 'N/A'}/10</span>
                    </li>
                    <li class="metric-item" style="margin-top: 10px; border-top: 1px dashed #ccfbf1; padding-top: 10px;">
                        <span class="metric-label" style="color: var(--color-green-dark)">Overall Score</span>
                        <span class="metric-value" style="color: var(--color-green-dark)">${score.toFixed(2)}</span>
                    </li>
                </ul>

                <div class="medicine-box">
                    <span class="metric-label" style="font-size: 0.9rem;">Demo note</span>
                    <p class="treatment-description"></p>
                </div>
            `;

            // Insert API text with textContent to avoid interpreting it as HTML.
            card.querySelector('.treatment-description').textContent = description;
            treatmentCards.appendChild(card);
        });

        // 4. Show the results section
        resultsWrapper.classList.remove('hidden');

        // ── Chart.js: Treatment Comparison Bar Graph ──────────────────────
        const ctx = document.getElementById('comparisonChart').getContext('2d');

        // Destroy old chart instance if it exists (prevents ghost charts)
        if (window.myChart) {
            window.myChart.destroy();
        }

        const allopathyScore  = data.comparison_scores.Allopathy  || 0;
        const ayurvedaScore   = data.comparison_scores.Ayurveda   || 0;
        const homeopathyScore = data.comparison_scores.Homeopathy || 0;

        window.myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Allopathy', 'Ayurveda', 'Homeopathy'],
                datasets: [{
                    label: 'Illustrative score (out of 10)',
                    data: [allopathyScore, ayurvedaScore, homeopathyScore],
                    // Smooth gradient-style colors per bar
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.85)',   // green  — Allopathy
                        'rgba(20, 184, 166, 0.85)',   // teal   — Ayurveda
                        'rgba(14, 165, 233, 0.85)'    // blue   — Homeopathy
                    ],
                    borderColor: [
                        'rgba(16, 185, 129, 1)',
                        'rgba(20, 184, 166, 1)',
                        'rgba(14, 165, 233, 1)'
                    ],
                    borderWidth: 2,
                    borderRadius: 10,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                animation: {
                    duration: 800,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    // Display chart title
                    title: {
                        display: true,
                        text: 'Illustrative Score Comparison (Not Clinical Evidence)',
                        font: { size: 18, weight: '600', family: 'Poppins' },
                        color: '#0f766e',
                        padding: { bottom: 20 }
                    },
                    legend: {
                        display: false   // hide legend — bars are labeled on X axis
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` Score: ${ctx.parsed.y.toFixed(2)} / 10`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,  // auto-scales to actual values, no fixed max
                        grid: { color: 'rgba(0,0,0,0.05)' },
                        ticks: {
                            font: { family: 'Poppins', size: 12 },
                            callback: (val) => val.toFixed(1)
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { family: 'Poppins', size: 13, weight: '500' } }
                    }
                }
            }
        });

        // Smooth scroll to results
        resultsWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});
