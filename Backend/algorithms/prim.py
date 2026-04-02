import time
import heapq
from typing import List, Tuple, Dict, Any
from collections import defaultdict


def prim(vertices: int, edges: List[Tuple[int, int, float]], start_vertex: int = 0) -> Dict[str, Any]:

    start_time = time.perf_counter()
    
    # Build adjacency list
    adj = defaultdict(list)
    for u, v, weight in edges:
        adj[u].append((v, weight))
        adj[v].append((u, weight))
    
    # Initialize
    visited = [False] * vertices
    mst_edges = []
    total_weight = 0
    steps = []
    
    # Priority queue: (weight, from_vertex, to_vertex)
    # Use -1 for initial vertex (no parent)
    pq = [(0, -1, start_vertex)]
    
    steps.append({
        'action': 'init',
        'message': f'Starting Prim\'s Algorithm from vertex {start_vertex}',
        'mst_edges': [],
        'current_vertex': start_vertex,
        'visited': [],
        'considering_edges': []
    })
    
    while pq and len(mst_edges) < vertices - 1:
        weight, from_v, to_v = heapq.heappop(pq)
        
        if visited[to_v]:
            continue
        
        visited[to_v] = True
        
        if from_v != -1:
            mst_edges.append((from_v, to_v, weight))
            total_weight += weight
            steps.append({
                'action': 'accept',
                'message': f'Added edge ({from_v}, {to_v}) with weight {weight}',
                'current_edge': (from_v, to_v, weight),
                'mst_edges': list(mst_edges),
                'current_vertex': to_v,
                'visited': [i for i, v in enumerate(visited) if v]
            })
        else:
            steps.append({
                'action': 'start',
                'message': f'Starting from vertex {to_v}',
                'mst_edges': [],
                'current_vertex': to_v,
                'visited': [to_v]
            })
        
        # Add all edges from current vertex to unvisited vertices
        considering = []
        for neighbor, edge_weight in adj[to_v]:
            if not visited[neighbor]:
                heapq.heappush(pq, (edge_weight, to_v, neighbor))
                considering.append((to_v, neighbor, edge_weight))
        
        if considering:
            steps.append({
                'action': 'explore',
                'message': f'Exploring edges from vertex {to_v}',
                'considering_edges': considering,
                'mst_edges': list(mst_edges),
                'current_vertex': to_v,
                'visited': [i for i, v in enumerate(visited) if v]
            })
    
    end_time = time.perf_counter()
    time_ms = (end_time - start_time) * 1000
    
    # Final step
    steps.append({
        'action': 'complete',
        'message': f'MST Complete! Total weight: {total_weight}',
        'mst_edges': list(mst_edges),
        'current_vertex': None,
        'visited': [i for i, v in enumerate(visited) if v]
    })
    
    return {
        'algorithm': 'Prim',
        'mst_edges': mst_edges,
        'total_weight': total_weight,
        'steps': steps,
        'time_ms': time_ms,
        'edge_count': len(mst_edges)
    }


def prim_benchmark(vertices: int, edges: List[Tuple[int, int, float]], iterations: int = 10) -> Dict[str, Any]:
    """Run Prim's algorithm multiple times for accurate benchmarking."""
    times = []
    result = None
    
    for _ in range(iterations):
        start = time.perf_counter()
        
        # Build adjacency list
        adj = defaultdict(list)
        for u, v, weight in edges:
            adj[u].append((v, weight))
            adj[v].append((u, weight))
        
        visited = [False] * vertices
        mst_edges = []
        total_weight = 0
        pq = [(0, -1, 0)]
        
        while pq and len(mst_edges) < vertices - 1:
            weight, from_v, to_v = heapq.heappop(pq)
            
            if visited[to_v]:
                continue
            
            visited[to_v] = True
            
            if from_v != -1:
                mst_edges.append((from_v, to_v, weight))
                total_weight += weight
            
            for neighbor, edge_weight in adj[to_v]:
                if not visited[neighbor]:
                    heapq.heappush(pq, (edge_weight, to_v, neighbor))
        
        end = time.perf_counter()
        times.append((end - start) * 1000)
        
        if result is None:
            result = {
                'mst_edges': mst_edges,
                'total_weight': total_weight
            }
    
    return {
        'algorithm': 'Prim',
        'mst_edges': result['mst_edges'],
        'total_weight': result['total_weight'],
        'avg_time_ms': sum(times) / len(times),
        'min_time_ms': min(times),
        'max_time_ms': max(times),
        'iterations': iterations
    }
