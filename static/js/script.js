// Complete Advanced JavaScript with Sliders, Insights & PDF Export

let chartsInstance = {};
let darkMode = localStorage.getItem('darkMode') === 'true';
let predictions = [];
let currentPredictionData = null;

// Wait for Chart.js to load
function waitForChart() {
    return new Promise((resolve) => {
        if (typeof Chart !== 'undefined') {
            resolve();
        } else {
            setTimeout(() => waitForChart().then(resolve), 100);
        }
    });
}

// Initialize when Chart is ready
document.addEventListener('DOMContentLoaded', function() {
    waitForChart().then(() => {
        console.log('✓ Chart.js loaded successfully');
        initializeApp();
    });
});

// Main Initialization
function initializeApp() {
    setupEventListeners();
    setupSliders();
    loadHistory();
    loadModelInfo();
    initTabs();
}

// Setup Sliders
function setupSliders() {
    const sliders = ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude'];
    
    sliders.forEach(id => {
        const slider = document.getElementById(id);
        if (slider) {
            slider.addEventListener('input', function() {
                let displayValue = this.value;
                if (id === 'MedInc') displayValue = parseFloat(this.value).toFixed(1);
                if (id === 'HouseAge') displayValue = parseInt(this.value);
                if (id === 'AveRooms') displayValue = parseFloat(this.value).toFixed(2);
                if (id === 'AveBedrms') displayValue = parseFloat(this.value).toFixed(2);
                if (id === 'Population') displayValue = parseInt(this.value);
                if (id === 'AveOccup') displayValue = parseFloat(this.value).toFixed(2);
                if (id === 'Latitude') displayValue = parseFloat(this.value).toFixed(2);
                if (id === 'Longitude') displayValue = parseFloat(this.value).toFixed(2);
                
                document.getElementById(`${id}_val`).textContent = displayValue;
            });
        }
    });
}

// Initialize Tabs
function initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            switchTab(tabName);
        });
    });
}

// Switch Tabs
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.add('hidden');
    });
    
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('active');
    });
    
    document.getElementById(tabName).classList.remove('hidden');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

// Setup Event Listeners
function setupEventListeners() {
    document.getElementById('predictionForm').addEventListener('submit', function(e) {
        e.preventDefault();
        makePrediction();
    });
    
    document.getElementById('exportBtn').addEventListener('click', function() {
        window.location.href = '/api/export';
    });

    document.getElementById('exportCSVBtn').addEventListener('click', function() {
        window.location.href = '/api/export';
    });
    
    document.getElementById('darkModeToggle').addEventListener('click', function() {
        darkMode = !darkMode;
        localStorage.setItem('darkMode', darkMode);
    });
}

// Single Prediction
async function makePrediction() {
    const formData = new FormData(document.getElementById('predictionForm'));
    const data = Object.fromEntries(formData);
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentPredictionData = result;
            displayResultWithInsights(result);
            predictions.push(result);
            updateAnalytics();
        } else {
            alert('Error: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Connection error: ' + error);
    }
}

// Display Result with Insights
function displayResultWithInsights(data) {
    const price = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(data.prediction);
    
    document.getElementById('predictedPrice').textContent = price;
    document.getElementById('predictionTime').textContent = `${data.timestamp}`;
    document.getElementById('resultCard').classList.remove('hidden');
    document.getElementById('exportCard').classList.remove('hidden');
    
    if (data.insights && data.insights.length > 0) {
        displayInsights(data.insights);
    }
    
    if (data.top_features && data.top_features.length > 0) {
        updateFeaturesChart(data.top_features);
    }
    
    document.getElementById('resultCard').scrollIntoView({ behavior: 'smooth' });
    loadHistory();
}

// Display Insights
function displayInsights(insights) {
    let html = '<div class="space-y-3">';
    insights.forEach(insight => {
        html += `
            <div class="bg-gradient-to-r from-green-900/30 to-yellow-900/30 p-4 rounded-xl border border-yellow-900/20">
                <p class="text-slate-200">${insight}</p>
            </div>
        `;
    });
    html += '</div>';
    document.getElementById('insightsContent').innerHTML = html;
}

// Update Features Chart
function updateFeaturesChart(topFeatures) {
    const canvas = document.getElementById('featuresChart');
    const ctx = canvas.getContext('2d');
    
    if (chartsInstance.features) {
        chartsInstance.features.destroy();
    }
    
    document.getElementById('featuresCard').classList.remove('hidden');
    
    chartsInstance.features = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topFeatures.map(f => f.name),
            datasets: [{
                label: 'Importance',
                data: topFeatures.map(f => f.importance),
                backgroundColor: ['#0B4F3C', '#0F6B52', '#B8860B'],
                borderColor: ['#DAA520', '#DAA520', '#DAA520'],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#e2e8f0', font: { size: 12, weight: '600' } }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 1,
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(184, 134, 11, 0.1)' }
                },
                y: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(184, 134, 11, 0.1)' }
                }
            }
        }
    });
}

// Update Analytics
function updateAnalytics() {
    if (predictions.length === 0) return;
    
    const prices = predictions.map(p => p.prediction);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    
    document.getElementById('minPred').textContent = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(minPrice);
    
    document.getElementById('maxPred').textContent = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(maxPrice);
    
    const canvas = document.getElementById('analyticsChart');
    const ctx = canvas.getContext('2d');
    
    if (chartsInstance.analytics) {
        chartsInstance.analytics.destroy();
    }
    
    chartsInstance.analytics = new Chart(ctx, {
        type: 'line',
        data: {
            labels: prices.map((_, i) => `#${i + 1}`),
            datasets: [{
                label: 'Prices',
                data: prices,
                borderColor: '#B8860B',
                backgroundColor: 'rgba(11, 79, 60, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#DAA520',
                pointBorderColor: '#B8860B',
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#e2e8f0', font: { size: 12, weight: '600' } }
                }
            },
            scales: {
                y: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(184, 134, 11, 0.1)' }
                },
                x: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(184, 134, 11, 0.1)' }
                }
            }
        }
    });
}

// Batch Predictions
async function batchPredict() {
    const input = document.getElementById('batchInput').value;
    
    try {
        const houses = JSON.parse(input);
        
        const response = await fetch('/api/batch-predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ houses })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayBatchResults(result.results);
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Invalid JSON: ' + error.message);
    }
}

// Display Batch Results
function displayBatchResults(results) {
    let html = '<div class="space-y-2">';
    
    results.forEach(r => {
        if (r.status === 'success') {
            const price = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(r.prediction);
            html += `
                <div class="history-item">
                    <span class="text-green-400">✓</span> House ${r.house_id}: <strong>${price}</strong>
                </div>
            `;
        } else {
            html += `
                <div class="history-item">
                    <span class="text-red-400">✗</span> House ${r.house_id}: ${r.error}
                </div>
            `;
        }
    });
    
    html += '</div>';
    document.getElementById('batchResults').innerHTML = html;
}

// Load History
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('totalPreds').textContent = data.total_predictions;
            
            if (data.average_price > 0) {
                document.getElementById('avgPrice').textContent = new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD'
                }).format(data.average_price);
            }
            
            let historyHtml = '';
            if (data.predictions.length > 0) {
                data.predictions.forEach((p, idx) => {
                    const price = new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD'
                    }).format(p.prediction);
                    historyHtml += `
                        <div class="history-item">
                            <div class="flex justify-between items-center">
                                <span class="text-yellow-400 font-bold">#${data.total_predictions - idx}</span>
                                <span class="text-green-400 font-bold">${price}</span>
                            </div>
                            <small class="text-slate-500 text-xs">${p.timestamp}</small>
                        </div>
                    `;
                });
            } else {
                historyHtml = '<p class="text-slate-500 text-center py-4">No predictions yet</p>';
            }
            document.getElementById('historyContent').innerHTML = historyHtml;
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Load Model Info
async function loadModelInfo() {
    try {
        const response = await fetch('/api/model-info');
        const data = await response.json();
        
        let html = `
            <div class="space-y-4">
                <div class="bg-gradient-to-r from-green-900/30 to-yellow-900/30 p-4 rounded-xl border border-yellow-900/20">
                    <div class="text-slate-400 text-xs uppercase">Model</div>
                    <div class="text-xl font-bold text-green-400">${data.model}</div>
                </div>
                
                <div class="bg-gradient-to-r from-green-900/30 to-yellow-900/30 p-4 rounded-xl border border-yellow-900/20">
                    <div class="text-slate-400 text-xs uppercase">Dataset</div>
                    <div class="text-xl font-bold text-yellow-400">${data.dataset}</div>
                </div>
                
                <div>
                    <div class="text-slate-400 text-xs uppercase mb-3 font-bold">Features</div>
                    <div class="flex flex-wrap gap-2">
                        ${data.features.map(f => `<span class="px-3 py-1 bg-green-900/50 border border-green-700 rounded-full text-sm text-green-400 font-bold">${f}</span>`).join('')}
                    </div>
                </div>
                
                <div>
                    <div class="text-slate-400 text-xs uppercase mb-3 font-bold">Importance</div>
                    <div class="space-y-3">
                        ${Object.entries(data.feature_importance).map(([k, v]) => `
                            <div>
                                <div class="flex justify-between mb-1">
                                    <span class="text-sm font-bold text-slate-300">${k}</span>
                                    <span class="text-yellow-400 font-bold">${(v * 100).toFixed(1)}%</span>
                                </div>
                                <div class="w-full bg-green-900/30 rounded-full h-2">
                                    <div class="bg-gradient-to-r from-green-600 to-yellow-600 h-2 rounded-full" style="width: ${v * 100}%"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        document.getElementById('modelInfoContent').innerHTML = html;
    } catch (error) {
        console.error('Error loading model info:', error);
    }
}

// Fill Sample Data
function fillSampleData() {
    document.getElementById('MedInc').value = 8.3252;
    document.getElementById('HouseAge').value = 41;
    document.getElementById('AveRooms').value = 6.98;
    document.getElementById('AveBedrms').value = 1.02;
    document.getElementById('Population').value = 322;
    document.getElementById('AveOccup').value = 2.56;
    document.getElementById('Latitude').value = 37.88;
    document.getElementById('Longitude').value = -122.23;
    
    // Update slider displays
    setupSliders();
}

// Export PDF
async function exportPDF() {
    if (!currentPredictionData) {
        alert('No prediction data to export');
        return;
    }

    try {
        const pdfData = {
            prediction: currentPredictionData.prediction,
            input: currentPredictionData.input || {},
            top_features: currentPredictionData.top_features || []
        };
        
        const pdfResponse = await fetch('/api/export-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pdfData)
        });
        
        const blob = await pdfResponse.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `house_prediction_${new Date().getTime()}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        alert('Error exporting PDF: ' + error);
    }
}

// Modal Functions
function openHistoryModal() {
    document.getElementById('historyModal').classList.remove('hidden');
    loadHistory();
}

function openAPIModal() {
    document.getElementById('apiModal').classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// Clear History
function clearHistory() {
    if (confirm('Clear all prediction history?')) {
        fetch('/api/clear-history', { method: 'POST' })
            .then(() => {
                predictions = [];
                loadHistory();
                alert('✓ History cleared!');
            })
            .catch(error => alert('Error: ' + error));
    }
}

// Close modals on outside click
window.addEventListener('click', function(e) {
    const historyModal = document.getElementById('historyModal');
    const apiModal = document.getElementById('apiModal');
    
    if (e.target === historyModal) historyModal.classList.add('hidden');
    if (e.target === apiModal) apiModal.classList.add('hidden');
});
         