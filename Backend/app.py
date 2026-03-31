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

if __name__ == '__main__':
    print("Starting MST Comparison Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=True)
