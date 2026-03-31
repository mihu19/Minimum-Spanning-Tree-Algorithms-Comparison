# MST Algorithm Comparison

A web-based tool for comparing Minimum Spanning Tree algorithms: **Kruskal's**, **Prim's**, and **Borůvka's**.

## Features

- **Interactive Visualization**: Watch each algorithm build the MST step by step
- **Benchmark Mode**: Compare performance across different graph sizes
- **Multiple Graph Types**: Random, Complete, Sparse, Grid, and Predefined examples
- **Educational Focus**: Learn why Kruskal's algorithm is often the best choice

## Project Structure

```
MST/
├── backend/
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── kruskal.py      # Kruskal's algorithm
│   │   ├── prim.py         # Prim's algorithm
│   │   └── boruvka.py      # Borůvka's algorithm
│   ├── app.py              # Flask server
│   ├── graph_generator.py  # Graph generation utilities
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── create_dirs.py
└── README.md
```

## Setup & Running

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Server

```bash
cd backend
python app.py
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

## Algorithm Comparison

### Kruskal's Algorithm (Recommended)
- **Complexity**: O(E log E)
- **Approach**: Edge-based, greedy
- **Best for**: Sparse graphs, simple implementation

### Prim's Algorithm
- **Complexity**: O(E log V)
- **Approach**: Vertex-based, greedy
- **Best for**: Dense graphs

### Borůvka's Algorithm
- **Complexity**: O(E log V)
- **Approach**: Component-based, parallel
- **Best for**: Distributed/parallel systems

## Why Kruskal's is Often Better

1. **Simple Implementation**: Uses Union-Find with path compression
2. **Intuitive**: Always pick the smallest edge that doesn't create a cycle
3. **Sparse Graph Performance**: Most real-world graphs are sparse
4. **Parallelizable**: Edge sorting can be done in parallel
5. **Early Termination**: Can stop when MST is complete

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate-graph` | POST | Generate a graph |
| `/api/run-algorithm` | POST | Run a specific MST algorithm |
| `/api/run-all` | POST | Run all three algorithms |
| `/api/benchmark` | POST | Run benchmarks |
| `/api/multi-benchmark` | POST | Run benchmarks across sizes |
| `/api/algorithm-info` | GET | Get algorithm information |

## Usage Examples

### Generate a Random Graph
```javascript
fetch('/api/generate-graph', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        type: 'random',
        vertices: 20,
        density: 0.5
    })
});
```

### Run Kruskal's Algorithm
```javascript
fetch('/api/run-algorithm', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        algorithm: 'kruskal',
        vertices: 6,
        edges: [[0,1,4], [0,2,3], [1,2,1], [1,3,2], [2,3,4]]
    })
});
```

## License

Educational purposes only.
