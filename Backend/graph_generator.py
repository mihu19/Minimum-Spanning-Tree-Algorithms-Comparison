import random
import math
from typing import List, Tuple, Dict, Any


def generate_random_graph(vertices: int, edge_density: float = 0.5, 
                          min_weight: float = 1, max_weight: float = 100,
                          seed: int = None) -> Dict[str, Any]:
                            
    if seed is not None:
        random.seed(seed)
    
    edges = []
    edge_set = set()
    
    # First, ensure connectivity with a spanning tree
    vertices_list = list(range(vertices))
    random.shuffle(vertices_list)
    
    for i in range(1, vertices):
        u = vertices_list[i]
        v = vertices_list[random.randint(0, i - 1)]
        weight = round(random.uniform(min_weight, max_weight), 2)
        edges.append((min(u, v), max(u, v), weight))
        edge_set.add((min(u, v), max(u, v)))
    
    # Add additional random edges based on density
    max_edges = vertices * (vertices - 1) // 2
    target_edges = int(max_edges * edge_density)
    
    attempts = 0
    while len(edges) < target_edges and attempts < max_edges * 2:
        u = random.randint(0, vertices - 1)
        v = random.randint(0, vertices - 1)
        if u != v:
            edge = (min(u, v), max(u, v))
            if edge not in edge_set:
                weight = round(random.uniform(min_weight, max_weight), 2)
                edges.append((edge[0], edge[1], weight))
                edge_set.add(edge)
        attempts += 1
    
    return {
        'vertices': vertices,
        'edges': edges,
        'edge_count': len(edges),
        'density': len(edges) / max_edges if max_edges > 0 else 0
    }


def generate_complete_graph(vertices: int, min_weight: float = 1, 
                            max_weight: float = 100, seed: int = None) -> Dict[str, Any]:
    if seed is not None:
        random.seed(seed)
    
    edges = []
    for i in range(vertices):
        for j in range(i + 1, vertices):
            weight = round(random.uniform(min_weight, max_weight), 2)
            edges.append((i, j, weight))
    
    return {
        'vertices': vertices,
        'edges': edges,
        'edge_count': len(edges),
        'density': 1.0
    }


def generate_sparse_graph(vertices: int, edges_per_vertex: int = 3,
                          min_weight: float = 1, max_weight: float = 100,
                          seed: int = None) -> Dict[str, Any]:
    if seed is not None:
        random.seed(seed)
    
    edges = []
    edge_set = set()
    
    # Ensure connectivity first
    for i in range(1, vertices):
        v = random.randint(0, i - 1)
        weight = round(random.uniform(min_weight, max_weight), 2)
        edge = (min(i, v), max(i, v))
        edges.append((edge[0], edge[1], weight))
        edge_set.add(edge)
    
    # Add more edges up to the limit
    target_edges = min(vertices * edges_per_vertex // 2, vertices * (vertices - 1) // 2)
    
    attempts = 0
    while len(edges) < target_edges and attempts < target_edges * 3:
        u = random.randint(0, vertices - 1)
        v = random.randint(0, vertices - 1)
        if u != v:
            edge = (min(u, v), max(u, v))
            if edge not in edge_set:
                weight = round(random.uniform(min_weight, max_weight), 2)
                edges.append((edge[0], edge[1], weight))
                edge_set.add(edge)
        attempts += 1
    
    max_edges = vertices * (vertices - 1) // 2
    return {
        'vertices': vertices,
        'edges': edges,
        'edge_count': len(edges),
        'density': len(edges) / max_edges if max_edges > 0 else 0
    }


def generate_grid_graph(rows: int, cols: int, min_weight: float = 1,
                        max_weight: float = 100, seed: int = None) -> Dict[str, Any]:
    """Generate a grid-shaped graph."""
    if seed is not None:
        random.seed(seed)
    
    vertices = rows * cols
    edges = []
    
    def vertex_id(r, c):
        return r * cols + c
    
    for r in range(rows):
        for c in range(cols):
            v = vertex_id(r, c)
            # Right neighbor
            if c + 1 < cols:
                weight = round(random.uniform(min_weight, max_weight), 2)
                edges.append((v, vertex_id(r, c + 1), weight))
            # Bottom neighbor
            if r + 1 < rows:
                weight = round(random.uniform(min_weight, max_weight), 2)
                edges.append((v, vertex_id(r + 1, c), weight))
    
    max_edges = vertices * (vertices - 1) // 2
    return {
        'vertices': vertices,
        'edges': edges,
        'edge_count': len(edges),
        'density': len(edges) / max_edges if max_edges > 0 else 0,
        'grid_size': {'rows': rows, 'cols': cols}
    }


def generate_euclidean_graph(vertices: int, width: float = 100, height: float = 100,
                             connection_radius: float = None, seed: int = None) -> Dict[str, Any]:

    if seed is not None:
        random.seed(seed)
    
    # Generate random points
    points = [(random.uniform(0, width), random.uniform(0, height)) for _ in range(vertices)]
    
    if connection_radius is None:
        # Default: connect points within ~30% of diagonal
        connection_radius = math.sqrt(width**2 + height**2) * 0.3
    
    edges = []
    edge_set = set()
    
    # Ensure connectivity first with MST-like approach
    connected = {0}
    remaining = set(range(1, vertices))
    
    while remaining:
        best_dist = float('inf')
        best_edge = None
        
        for u in connected:
            for v in remaining:
                dist = math.sqrt((points[u][0] - points[v][0])**2 + 
                               (points[u][1] - points[v][1])**2)
                if dist < best_dist:
                    best_dist = dist
                    best_edge = (min(u, v), max(u, v), round(dist, 2))
        
        if best_edge:
            edges.append(best_edge)
            edge_set.add((best_edge[0], best_edge[1]))
            remaining.remove(best_edge[1] if best_edge[0] in connected else best_edge[0])
            connected.add(best_edge[1] if best_edge[0] in connected else best_edge[0])
    
    # Add edges within connection radius
    for i in range(vertices):
        for j in range(i + 1, vertices):
            if (i, j) not in edge_set:
                dist = math.sqrt((points[i][0] - points[j][0])**2 + 
                               (points[i][1] - points[j][1])**2)
                if dist <= connection_radius:
                    edges.append((i, j, round(dist, 2)))
                    edge_set.add((i, j))
    
    max_edges = vertices * (vertices - 1) // 2
    return {
        'vertices': vertices,
        'edges': edges,
        'edge_count': len(edges),
        'density': len(edges) / max_edges if max_edges > 0 else 0,
        'points': points  # For visualization
    }


def generate_predefined_graph(graph_name: str) -> Dict[str, Any]:
    graphs = {
        'simple': {
            'vertices': 6,
            'edges': [
                (0, 1, 4), (0, 2, 3), (1, 2, 1), (1, 3, 2),
                (2, 3, 4), (2, 4, 3), (3, 4, 2), (3, 5, 1), (4, 5, 6)
            ]
        },
        'medium': {
            'vertices': 9,
            'edges': [
                (0, 1, 4), (0, 7, 8), (1, 2, 8), (1, 7, 11),
                (2, 3, 7), (2, 5, 4), (2, 8, 2), (3, 4, 9),
                (3, 5, 14), (4, 5, 10), (5, 6, 2), (6, 7, 1),
                (6, 8, 6), (7, 8, 7)
            ]
        },
        'triangle': {
            'vertices': 3,
            'edges': [(0, 1, 5), (1, 2, 3), (0, 2, 7)]
        },
        'diamond': {
            'vertices': 4,
            'edges': [(0, 1, 1), (0, 2, 2), (1, 2, 3), (1, 3, 4), (2, 3, 5)]
        }
    }
    
    if graph_name not in graphs:
        graph_name = 'simple'
    
    graph = graphs[graph_name]
    max_edges = graph['vertices'] * (graph['vertices'] - 1) // 2
    
    return {
        'vertices': graph['vertices'],
        'edges': graph['edges'],
        'edge_count': len(graph['edges']),
        'density': len(graph['edges']) / max_edges if max_edges > 0 else 0,
        'name': graph_name
    }
