from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

from algorithms import kruskal, prim, boruvka
from algorithms import kruskal_benchmark, prim_benchmark, boruvka_benchmark
from graph_generator import (
    generate_random_graph, generate_complete_graph, generate_sparse_graph,
    generate_grid_graph, generate_euclidean_graph, generate_predefined_graph
)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)


@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'MST Comparison API is running'})


@app.route('/api/generate-graph', methods=['POST'])
def generate_graph():
    """Generate a graph based on specified parameters."""
    data = request.json
    graph_type = data.get('type', 'random')
    
    try:
        if graph_type == 'random':
            graph = generate_random_graph(
                vertices=data.get('vertices', 10),
                edge_density=data.get('density', 0.5),
                min_weight=data.get('minWeight', 1),
                max_weight=data.get('maxWeight', 100),
                seed=data.get('seed')
            )
        elif graph_type == 'complete':
            graph = generate_complete_graph(
                vertices=data.get('vertices', 10),
                min_weight=data.get('minWeight', 1),
                max_weight=data.get('maxWeight', 100),
                seed=data.get('seed')
            )
        elif graph_type == 'sparse':
            graph = generate_sparse_graph(
                vertices=data.get('vertices', 10),
                edges_per_vertex=data.get('edgesPerVertex', 3),
                min_weight=data.get('minWeight', 1),
                max_weight=data.get('maxWeight', 100),
                seed=data.get('seed')
            )
        elif graph_type == 'grid':
            rows = data.get('rows', 4)
            cols = data.get('cols', 4)
            graph = generate_grid_graph(
                rows=rows,
                cols=cols,
                min_weight=data.get('minWeight', 1),
                max_weight=data.get('maxWeight', 100),
                seed=data.get('seed')
            )
        elif graph_type == 'euclidean':
            graph = generate_euclidean_graph(
                vertices=data.get('vertices', 10),
                width=data.get('width', 100),
                height=data.get('height', 100),
                connection_radius=data.get('connectionRadius'),
                seed=data.get('seed')
            )
        elif graph_type == 'predefined':
            graph = generate_predefined_graph(data.get('name', 'simple'))
        else:
            return jsonify({'error': f'Unknown graph type: {graph_type}'}), 400
        
        return jsonify(graph)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/run-algorithm', methods=['POST'])
def run_algorithm():
    """Run a specific MST algorithm on the provided graph."""
    data = request.json
    algorithm = data.get('algorithm', 'kruskal').lower()
    vertices = data.get('vertices', 0)
    edges = [tuple(e) for e in data.get('edges', [])]
    
    if vertices < 1:
        return jsonify({'error': 'Graph must have at least 1 vertex'}), 400
    
    if not edges:
        return jsonify({'error': 'Graph must have edges'}), 400
    
    try:
        if algorithm == 'kruskal':
            result = kruskal(vertices, edges)
        elif algorithm == 'prim':
            result = prim(vertices, edges)
        elif algorithm == 'boruvka':
            result = boruvka(vertices, edges)
        else:
            return jsonify({'error': f'Unknown algorithm: {algorithm}'}), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/run-all', methods=['POST'])
def run_all_algorithms():
    """Run all three MST algorithms on the provided graph for comparison."""
    data = request.json
    vertices = data.get('vertices', 0)
    edges = [tuple(e) for e in data.get('edges', [])]
    
    if vertices < 1 or not edges:
        return jsonify({'error': 'Invalid graph'}), 400
    
    try:
        results = {
            'kruskal': kruskal(vertices, edges),
            'prim': prim(vertices, edges),
            'boruvka': boruvka(vertices, edges)
        }
        
        # Add comparison summary
        results['comparison'] = {
            'fastest': min(results.keys(), key=lambda k: results[k]['time_ms']),
            'all_same_weight': (
                results['kruskal']['total_weight'] == 
                results['prim']['total_weight'] == 
                results['boruvka']['total_weight']
            )
        }
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/benchmark', methods=['POST'])
def benchmark_algorithms():
    """Run benchmarks on all algorithms with the provided graph."""
    data = request.json
    vertices = data.get('vertices', 0)
    edges = [tuple(e) for e in data.get('edges', [])]
    iterations = data.get('iterations', 10)
    
    if vertices < 1 or not edges:
        return jsonify({'error': 'Invalid graph'}), 400
    
    try:
        results = {
            'kruskal': kruskal_benchmark(vertices, edges, iterations),
            'prim': prim_benchmark(vertices, edges, iterations),
            'boruvka': boruvka_benchmark(vertices, edges, iterations),
            'graph_info': {
                'vertices': vertices,
                'edges': len(edges),
                'density': len(edges) / (vertices * (vertices - 1) / 2) if vertices > 1 else 0
            }
        }
        
        # Calculate speedup compared to slowest
        times = {k: v['avg_time_ms'] for k, v in results.items() if 'avg_time_ms' in v}
        slowest = max(times.values())
        results['speedup'] = {k: round(slowest / v, 2) if v > 0 else 0 for k, v in times.items()}
        results['ranking'] = sorted(times.keys(), key=lambda k: times[k])
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/multi-benchmark', methods=['POST'])
def multi_benchmark():
    """Run benchmarks across multiple graph sizes for scaling analysis."""
    data = request.json
    sizes = data.get('sizes', [10, 50, 100, 200])
    density = data.get('density', 0.5)
    iterations = data.get('iterations', 5)
    
    results = []
    
    try:
        for size in sizes:
            graph = generate_random_graph(vertices=size, edge_density=density)
            vertices = graph['vertices']
            edges = graph['edges']
            
            benchmark = {
                'vertices': vertices,
                'edges': len(edges),
                'kruskal': kruskal_benchmark(vertices, edges, iterations)['avg_time_ms'],
                'prim': prim_benchmark(vertices, edges, iterations)['avg_time_ms'],
                'boruvka': boruvka_benchmark(vertices, edges, iterations)['avg_time_ms']
            }
            results.append(benchmark)
        
        return jsonify({
            'benchmarks': results,
            'density': density,
            'iterations': iterations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/algorithm-info')
def algorithm_info():
    """Get information about all MST algorithms."""
    return jsonify({
        'kruskal': {
            'name': "Kruskal's Algorithm",
            'complexity': 'O(E log E)',
            'approach': 'Edge-based, greedy',
            'description': 'Sorts all edges by weight and adds them one by one if they don\'t create a cycle.',
            'advantages': [
                'Simple implementation with Union-Find',
                'Works well on sparse graphs',
                'Can be easily parallelized (sorting)',
                'Natural handling of disconnected graphs',
                'Better cache locality'
            ],
            'disadvantages': [
                'Requires sorting all edges upfront',
                'Slower on very dense graphs'
            ]
        },
        'prim': {
            'name': "Prim's Algorithm",
            'complexity': 'O(E log V)',
            'approach': 'Vertex-based, greedy',
            'description': 'Grows the MST from a starting vertex by always adding the minimum edge to a new vertex.',
            'advantages': [
                'Good for dense graphs',
                'Uses priority queue efficiently'
            ],
            'disadvantages': [
                'Requires maintaining priority queue',
                'Must process vertices in order',
                'Harder to parallelize'
            ]
        },
        'boruvka': {
            'name': "Borůvka's Algorithm",
            'complexity': 'O(E log V)',
            'approach': 'Component-based, parallel-friendly',
            'description': 'Repeatedly finds minimum edges for all components and merges them.',
            'advantages': [
                'Can add multiple edges per iteration',
                'Good for parallel processing'
            ],
            'disadvantages': [
                'More complex implementation',
                'Multiple passes through edge list',
                'Less intuitive than Kruskal\'s'
            ]
        },
        'why_kruskal_is_better': [
            'Simpler implementation with Union-Find data structure',
            'Intuitive greedy approach - always pick the smallest edge',
            'Excellent performance on sparse graphs (common in practice)',
            'Easy to understand and teach',
            'Edge sorting can be parallelized',
            'Better cache performance due to sequential edge processing',
            'Can stop early when MST is complete',
            'Naturally handles forests (disconnected graphs)'
        ]
    })


if __name__ == '__main__':
    print("Starting MST Comparison Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=True)
