/**
 * MST Algorithm Comparison - Frontend Application
 */

const API_BASE = '';

// State
let currentGraph = null;
let algorithmResult = null;
let animationStep = 0;
let isAnimating = false;
let animationTimeout = null;
let benchmarkChart = null;

// DOM Elements
const elements = {
    // Tabs
    tabs: document.querySelectorAll('.tab'),
    tabContents: document.querySelectorAll('.tab-content'),
    
    // Graph settings
    graphType: document.getElementById('graphType'),
    predefinedOptions: document.getElementById('predefinedOptions'),
    predefinedGraph: document.getElementById('predefinedGraph'),
    randomOptions: document.getElementById('randomOptions'),
    gridOptions: document.getElementById('gridOptions'),
    vertices: document.getElementById('vertices'),
    verticesValue: document.getElementById('verticesValue'),
    density: document.getElementById('density'),
    densityValue: document.getElementById('densityValue'),
    gridRows: document.getElementById('gridRows'),
    gridRowsValue: document.getElementById('gridRowsValue'),
    gridCols: document.getElementById('gridCols'),
    gridColsValue: document.getElementById('gridColsValue'),
    generateGraph: document.getElementById('generateGraph'),
    
    // Algorithm
    algorithmCards: document.querySelectorAll('.radio-card'),
    animationSpeed: document.getElementById('animationSpeed'),
    runAlgorithm: document.getElementById('runAlgorithm'),
    stepAlgorithm: document.getElementById('stepAlgorithm'),
    resetVisualization: document.getElementById('resetVisualization'),
    
    // Visualization
    graphCanvas: document.getElementById('graphCanvas'),
    graphStats: document.getElementById('graphStats'),
    stepInfo: document.getElementById('stepInfo'),
    stepLog: document.getElementById('stepLog'),
    mstWeight: document.getElementById('mstWeight'),
    mstEdges: document.getElementById('mstEdges'),
    execTime: document.getElementById('execTime'),
    
    // Benchmark
    benchSizes: document.getElementById('benchSizes'),
    benchDensity: document.getElementById('benchDensity'),
    benchDensityValue: document.getElementById('benchDensityValue'),
    benchIterations: document.getElementById('benchIterations'),
    runBenchmark: document.getElementById('runBenchmark'),
    benchmarkProgress: document.getElementById('benchmarkProgress'),
    benchmarkChart: document.getElementById('benchmarkChart'),
    benchmarkTable: document.getElementById('benchmarkTable'),
    benchmarkStatus: document.getElementById('benchmarkStatus'),
    currentBenchSize: document.getElementById('currentBenchSize'),
    currentBenchAlgo: document.getElementById('currentBenchAlgo'),
    currentBenchProgress: document.getElementById('currentBenchProgress'),
    benchGraphCanvas: document.getElementById('benchGraphCanvas'),
    benchKruskalTime: document.getElementById('benchKruskalTime'),
    benchPrimTime: document.getElementById('benchPrimTime'),
    benchBoruvkaTime: document.getElementById('benchBoruvkaTime'),
    
    // Quick compare (removed)
};

// Canvas context
let ctx = elements.graphCanvas.getContext('2d');
let benchCtx = elements.benchGraphCanvas.getContext('2d');
let vertexPositions = [];
let benchVertexPositions = [];

// Initialize
document.addEventListener('DOMContentLoaded', init);

function init() {
    setupEventListeners();
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
}

function setupEventListeners() {
    // Tabs
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    // Graph type changes
    elements.graphType.addEventListener('change', updateGraphOptions);
    
    // Range sliders
    elements.vertices.addEventListener('input', () => {
        elements.verticesValue.textContent = elements.vertices.value;
    });
    elements.density.addEventListener('input', () => {
        elements.densityValue.textContent = elements.density.value + '%';
    });
    elements.gridRows.addEventListener('input', () => {
        elements.gridRowsValue.textContent = elements.gridRows.value;
    });
    elements.gridCols.addEventListener('input', () => {
        elements.gridColsValue.textContent = elements.gridCols.value;
    });
    elements.benchDensity.addEventListener('input', () => {
        elements.benchDensityValue.textContent = elements.benchDensity.value + '%';
    });
    
    // Algorithm selection
    elements.algorithmCards.forEach(card => {
        card.addEventListener('click', () => selectAlgorithm(card));
    });
    
    // Buttons
    elements.generateGraph.addEventListener('click', generateGraph);
    elements.runAlgorithm.addEventListener('click', runAlgorithm);
    elements.stepAlgorithm.addEventListener('click', stepAlgorithm);
    elements.resetVisualization.addEventListener('click', resetVisualization);
    elements.runBenchmark.addEventListener('click', runBenchmark);
}

function switchTab(tabId) {
    elements.tabs.forEach(t => t.classList.remove('active'));
    elements.tabContents.forEach(c => c.classList.remove('active'));
    
    document.querySelector(`.tab[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

function updateGraphOptions() {
    const type = elements.graphType.value;
    
    elements.predefinedOptions.classList.add('hidden');
    elements.randomOptions.classList.add('hidden');
    elements.gridOptions.classList.add('hidden');
    
    if (type === 'predefined') {
        elements.predefinedOptions.classList.remove('hidden');
    } else if (type === 'grid') {
        elements.gridOptions.classList.remove('hidden');
    } else {
        elements.randomOptions.classList.remove('hidden');
    }
}

function selectAlgorithm(card) {
    elements.algorithmCards.forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    card.querySelector('input').checked = true;
}

function getSelectedAlgorithm() {
    return document.querySelector('input[name="algorithm"]:checked').value;
}

// Canvas functions
function resizeCanvas() {
    const container = elements.graphCanvas.parentElement;
    elements.graphCanvas.width = container.clientWidth;
    elements.graphCanvas.height = 500;
    if (currentGraph) {
        drawGraph();
    }
    
    // Resize benchmark canvas too
    const benchContainer = elements.benchGraphCanvas.parentElement;
    if (benchContainer) {
        elements.benchGraphCanvas.width = benchContainer.clientWidth;
        elements.benchGraphCanvas.height = 300;
    }
}

function calculateVertexPositions(vertices) {
    const canvas = elements.graphCanvas;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) * 0.35;
    
    vertexPositions = [];
    
    // Check for grid layout
    if (currentGraph && currentGraph.grid_size) {
        const rows = currentGraph.grid_size.rows;
        const cols = currentGraph.grid_size.cols;
        const cellWidth = (canvas.width - 100) / cols;
        const cellHeight = (canvas.height - 100) / rows;
        
        for (let i = 0; i < vertices; i++) {
            const row = Math.floor(i / cols);
            const col = i % cols;
            vertexPositions.push({
                x: 50 + col * cellWidth + cellWidth / 2,
                y: 50 + row * cellHeight + cellHeight / 2
            });
        }
    } else {
        // Circular layout
        for (let i = 0; i < vertices; i++) {
            const angle = (2 * Math.PI * i) / vertices - Math.PI / 2;
            vertexPositions.push({
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle)
            });
        }
    }
}

function drawGraph(highlightEdges = [], currentEdge = null, rejected = false) {
    if (!currentGraph) return;
    
    ctx.clearRect(0, 0, elements.graphCanvas.width, elements.graphCanvas.height);
    
    const { vertices, edges } = currentGraph;
    
    // Draw all edges first (gray)
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 2;
    
    edges.forEach(([u, v, weight]) => {
        const isHighlighted = highlightEdges.some(e => 
            (e[0] === u && e[1] === v) || (e[0] === v && e[1] === u)
        );
        const isCurrent = currentEdge && 
            ((currentEdge[0] === u && currentEdge[1] === v) || 
             (currentEdge[0] === v && currentEdge[1] === u));
        
        if (!isHighlighted && !isCurrent) {
            drawEdge(u, v, weight, '#d1d5db', 2);
        }
    });
    
    // Draw MST edges (green)
    highlightEdges.forEach(([u, v, weight]) => {
        drawEdge(u, v, weight, '#10b981', 4);
    });
    
    // Draw current edge
    if (currentEdge) {
        const color = rejected ? '#ef4444' : '#f59e0b';
        drawEdge(currentEdge[0], currentEdge[1], currentEdge[2], color, 4);
    }
    
    // Draw vertices
    for (let i = 0; i < vertices; i++) {
        drawVertex(i);
    }
}

function drawEdge(u, v, weight, color, lineWidth) {
    const p1 = vertexPositions[u];
    const p2 = vertexPositions[v];
    
    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.stroke();
    
    // Draw weight label
    const midX = (p1.x + p2.x) / 2;
    const midY = (p1.y + p2.y) / 2;
    
    ctx.fillStyle = 'white';
    ctx.fillRect(midX - 15, midY - 10, 30, 20);
    
    ctx.fillStyle = '#374151';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(weight.toString(), midX, midY);
}

function drawVertex(index) {
    const pos = vertexPositions[index];
    const radius = 20;
    
    // Shadow
    ctx.beginPath();
    ctx.arc(pos.x + 2, pos.y + 2, radius, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fill();
    
    // Circle
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
    ctx.fillStyle = '#4f46e5';
    ctx.fill();
    ctx.strokeStyle = '#4338ca';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Label
    ctx.fillStyle = 'white';
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(index.toString(), pos.x, pos.y);
}

// API Functions
async function generateGraph() {
    const type = elements.graphType.value;
    let body = { type };
    
    if (type === 'predefined') {
        body.name = elements.predefinedGraph.value;
    } else if (type === 'grid') {
        body.rows = parseInt(elements.gridRows.value);
        body.cols = parseInt(elements.gridCols.value);
    } else {
        body.vertices = parseInt(elements.vertices.value);
        body.density = parseInt(elements.density.value) / 100;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/generate-graph`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        
        currentGraph = await response.json();
        calculateVertexPositions(currentGraph.vertices);
        drawGraph();
        
        elements.graphStats.textContent = 
            `${currentGraph.vertices} vertices, ${currentGraph.edge_count} edges (${(currentGraph.density * 100).toFixed(0)}% density)`;
        
        resetVisualization();
    } catch (error) {
        console.error('Error generating graph:', error);
        alert('Error generating graph. Make sure the backend is running.');
    }
}

async function runAlgorithm() {
    if (!currentGraph) {
        alert('Please generate a graph first.');
        return;
    }
    
    if (isAnimating) {
        stopAnimation();
        return;
    }
    
    const algorithm = getSelectedAlgorithm();
    
    try {
        const response = await fetch(`${API_BASE}/api/run-algorithm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                algorithm,
                vertices: currentGraph.vertices,
                edges: currentGraph.edges
            })
        });
        
        algorithmResult = await response.json();
        animationStep = 0;
        
        // Start animation
        isAnimating = true;
        elements.runAlgorithm.textContent = '⏹ Stop';
        animateSteps();
        
    } catch (error) {
        console.error('Error running algorithm:', error);
        alert('Error running algorithm.');
    }
}

function animateSteps() {
    if (!isAnimating || !algorithmResult || animationStep >= algorithmResult.steps.length) {
        stopAnimation();
        return;
    }
    
    const step = algorithmResult.steps[animationStep];
    renderStep(step);
    animationStep++;
    
    const speed = parseInt(elements.animationSpeed.value);
    animationTimeout = setTimeout(animateSteps, 2100 - speed);
}

function stopAnimation() {
    isAnimating = false;
    clearTimeout(animationTimeout);
    elements.runAlgorithm.textContent = '▶ Run';
    
    // Show final result
    if (algorithmResult) {
        updateResults();
    }
}

function stepAlgorithm() {
    if (!algorithmResult) {
        runAlgorithm();
        return;
    }
    
    if (animationStep < algorithmResult.steps.length) {
        const step = algorithmResult.steps[animationStep];
        renderStep(step);
        animationStep++;
    }
}

function renderStep(step) {
    // Update visualization
    const mstEdges = step.mst_edges || [];
    const currentEdge = step.current_edge || null;
    const rejected = step.rejected || false;
    
    drawGraph(mstEdges, currentEdge, rejected);
    
    // Update step info
    elements.stepInfo.innerHTML = `
        <p class="current-step">${step.message}</p>
    `;
    
    // Add to log
    const logItem = document.createElement('div');
    logItem.className = `step-log-item ${step.action}`;
    
    let icon = '*';
    if (step.action === 'accept') icon = '+';
    else if (step.action === 'reject') icon = 'x';
    else if (step.action === 'complete') icon = '!';
    else if (step.action === 'init') icon = '>';
    
    logItem.innerHTML = `<span class="step-icon">${icon}</span><span>${step.message}</span>`;
    elements.stepLog.insertBefore(logItem, elements.stepLog.firstChild);
    
    // Update results if complete
    if (step.action === 'complete') {
        updateResults();
    }
}

function updateResults() {
    if (!algorithmResult) return;
    
    elements.mstWeight.textContent = algorithmResult.total_weight.toFixed(2);
    elements.mstEdges.textContent = algorithmResult.edge_count;
    elements.execTime.textContent = algorithmResult.time_ms.toFixed(3) + ' ms';
}

function resetVisualization() {
    isAnimating = false;
    clearTimeout(animationTimeout);
    algorithmResult = null;
    animationStep = 0;
    
    elements.runAlgorithm.textContent = '▶ Run';
    elements.stepInfo.innerHTML = '<p class="placeholder">Generate a graph and run an algorithm to see the steps here.</p>';
    elements.stepLog.innerHTML = '';
    elements.mstWeight.textContent = '-';
    elements.mstEdges.textContent = '-';
    elements.execTime.textContent = '-';
    
    if (currentGraph) {
        drawGraph();
    }
}

// Benchmark functions
async function runBenchmark() {
    const sizes = elements.benchSizes.value.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
    const density = parseInt(elements.benchDensity.value) / 100;
    const iterations = parseInt(elements.benchIterations.value);
    
    if (sizes.length === 0) {
        alert('Please enter valid graph sizes.');
        return;
    }
    
    elements.runBenchmark.disabled = true;
    elements.benchmarkProgress.classList.remove('hidden');
    elements.benchmarkStatus.classList.remove('hidden');
    
    // Reset time displays
    elements.benchKruskalTime.textContent = '-';
    elements.benchPrimTime.textContent = '-';
    elements.benchBoruvkaTime.textContent = '-';
    resetAlgoTimeCards();
    
    const allResults = [];
    const totalSteps = sizes.length;
    
    try {
        for (let i = 0; i < sizes.length; i++) {
            const size = sizes[i];
            
            // Update progress
            const progress = ((i + 1) / totalSteps) * 100;
            elements.benchmarkProgress.querySelector('.progress-bar').style.width = progress + '%';
            elements.benchmarkProgress.querySelector('.progress-text').textContent = 
                `Testing size ${size}... (${i + 1}/${totalSteps})`;
            elements.currentBenchSize.textContent = `${size} vertices`;
            elements.currentBenchProgress.textContent = `${i + 1} / ${totalSteps}`;
            
            // Generate graph for this size
            const graphResponse = await fetch(`${API_BASE}/api/generate-graph`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'random', vertices: size, density })
            });
            const graph = await graphResponse.json();
            
            // Draw the graph on benchmark canvas
            drawBenchmarkGraph(graph);
            
            // Reset time cards
            resetAlgoTimeCards();
            elements.benchKruskalTime.textContent = '-';
            elements.benchPrimTime.textContent = '-';
            elements.benchBoruvkaTime.textContent = '-';
            
            // Run each algorithm with visualization
            const result = { vertices: size, edges: graph.edge_count };
            
            // Kruskal
            elements.currentBenchAlgo.textContent = "Kruskal's";
            setActiveAlgoCard('kruskal');
            const kruskalResult = await runSingleBenchmark(graph, 'kruskal', iterations);
            result.kruskal = kruskalResult.avg_time_ms;
            elements.benchKruskalTime.textContent = kruskalResult.avg_time_ms.toFixed(3) + ' ms';
            drawBenchmarkGraph(graph, kruskalResult.mst_edges);
            await sleep(300);
            
            // Prim
            elements.currentBenchAlgo.textContent = "Prim's";
            setActiveAlgoCard('prim');
            const primResult = await runSingleBenchmark(graph, 'prim', iterations);
            result.prim = primResult.avg_time_ms;
            elements.benchPrimTime.textContent = primResult.avg_time_ms.toFixed(3) + ' ms';
            drawBenchmarkGraph(graph, primResult.mst_edges);
            await sleep(300);
            
            // Boruvka
            elements.currentBenchAlgo.textContent = "Boruvka's";
            setActiveAlgoCard('boruvka');
            const boruvkaResult = await runSingleBenchmark(graph, 'boruvka', iterations);
            result.boruvka = boruvkaResult.avg_time_ms;
            elements.benchBoruvkaTime.textContent = boruvkaResult.avg_time_ms.toFixed(3) + ' ms';
            drawBenchmarkGraph(graph, boruvkaResult.mst_edges);
            await sleep(300);
            
            // Highlight winner for this size
            highlightWinner(result);
            
            allResults.push(result);
            
            // Update chart progressively
            displayBenchmarkResults({ benchmarks: allResults, density, iterations });
            
            await sleep(500);
        }
        
        elements.currentBenchAlgo.textContent = 'Complete!';
        elements.benchmarkProgress.querySelector('.progress-text').textContent = 'Benchmark complete!';
        
    } catch (error) {
        console.error('Error running benchmark:', error);
        alert('Error running benchmark.');
    } finally {
        elements.runBenchmark.disabled = false;
        setTimeout(() => {
            elements.benchmarkProgress.classList.add('hidden');
        }, 2000);
    }
}

async function runSingleBenchmark(graph, algorithm, iterations) {
    const response = await fetch(`${API_BASE}/api/run-algorithm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            algorithm,
            vertices: graph.vertices,
            edges: graph.edges
        })
    });
    const result = await response.json();
    
    // Run multiple iterations for timing
    let totalTime = result.time_ms;
    for (let i = 1; i < iterations; i++) {
        const r = await fetch(`${API_BASE}/api/run-algorithm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                algorithm,
                vertices: graph.vertices,
                edges: graph.edges
            })
        });
        const res = await r.json();
        totalTime += res.time_ms;
    }
    
    return {
        avg_time_ms: totalTime / iterations,
        mst_edges: result.mst_edges
    };
}

function drawBenchmarkGraph(graph, mstEdges = []) {
    const canvas = elements.benchGraphCanvas;
    const ctx = benchCtx;
    
    // Resize if needed
    const container = canvas.parentElement;
    canvas.width = container.clientWidth;
    canvas.height = 300;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const { vertices, edges } = graph;
    
    // Calculate positions
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) * 0.45;
    
    benchVertexPositions = [];
    for (let i = 0; i < vertices; i++) {
        const angle = (2 * Math.PI * i) / vertices - Math.PI / 2;
        benchVertexPositions.push({
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle)
        });
    }
    
    // Draw all edges (gray, thin)
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    
    edges.forEach(([u, v, weight]) => {
        const isMST = mstEdges.some(e => 
            (e[0] === u && e[1] === v) || (e[0] === v && e[1] === u)
        );
        if (!isMST) {
            const p1 = benchVertexPositions[u];
            const p2 = benchVertexPositions[v];
            if (p1 && p2) {
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
            }
        }
    });
    
    // Draw MST edges (green, thick)
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 3;
    
    mstEdges.forEach(([u, v, weight]) => {
        const p1 = benchVertexPositions[u];
        const p2 = benchVertexPositions[v];
        if (p1 && p2) {
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
        }
    });
    
    // Draw vertices (smaller for benchmark view)
    const vertexRadius = Math.max(4, Math.min(10, 100 / vertices));
    for (let i = 0; i < vertices; i++) {
        const pos = benchVertexPositions[i];
        if (pos) {
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, vertexRadius, 0, Math.PI * 2);
            ctx.fillStyle = '#4f46e5';
            ctx.fill();
        }
    }
}

function setActiveAlgoCard(algo) {
    document.querySelectorAll('.algo-time-card').forEach(card => {
        card.classList.remove('active', 'winner');
    });
    document.querySelector(`.algo-time-card.${algo}`).classList.add('active');
}

function resetAlgoTimeCards() {
    document.querySelectorAll('.algo-time-card').forEach(card => {
        card.classList.remove('active', 'winner');
    });
}

function highlightWinner(result) {
    resetAlgoTimeCards();
    const times = { kruskal: result.kruskal, prim: result.prim, boruvka: result.boruvka };
    const winner = Object.keys(times).reduce((a, b) => times[a] < times[b] ? a : b);
    document.querySelector(`.algo-time-card.${winner}`).classList.add('winner');
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function displayBenchmarkResults(results) {
    // Create chart
    const ctx = elements.benchmarkChart.getContext('2d');
    
    if (benchmarkChart) {
        benchmarkChart.destroy();
    }
    
    benchmarkChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: results.benchmarks.map(b => b.vertices + ' vertices'),
            datasets: [
                {
                    label: "Kruskal's",
                    data: results.benchmarks.map(b => b.kruskal),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: "Prim's",
                    data: results.benchmarks.map(b => b.prim),
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: "Borůvka's",
                    data: results.benchmarks.map(b => b.boruvka),
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Performance Comparison (${(results.density * 100).toFixed(0)}% edge density, ${results.iterations} iterations)`
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Time (ms)'
                    },
                    beginAtZero: true
                }
            }
        }
    });
    
    // Create table
    let tableHTML = `
        <table>
            <thead>
                <tr>
                    <th>Vertices</th>
                    <th>Edges</th>
                    <th>Kruskal's</th>
                    <th>Prim's</th>
                    <th>Borůvka's</th>
                    <th>Fastest</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    results.benchmarks.forEach(b => {
        const times = { kruskal: b.kruskal, prim: b.prim, boruvka: b.boruvka };
        const fastest = Object.keys(times).reduce((a, b) => times[a] < times[b] ? a : b);
        
        tableHTML += `
            <tr>
                <td>${b.vertices}</td>
                <td>${b.edges}</td>
                <td class="${fastest === 'kruskal' ? 'fastest' : ''}">${b.kruskal.toFixed(3)} ms</td>
                <td class="${fastest === 'prim' ? 'fastest' : ''}">${b.prim.toFixed(3)} ms</td>
                <td class="${fastest === 'boruvka' ? 'fastest' : ''}">${b.boruvka.toFixed(3)} ms</td>
                <td class="fastest">${fastest.charAt(0).toUpperCase() + fastest.slice(1)}'s</td>
            </tr>
        `;
    });
    
    tableHTML += '</tbody></table>';
    elements.benchmarkTable.innerHTML = tableHTML;
}
