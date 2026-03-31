import time
from typing import List, Tuple, Dict, Any


class UnionFind:
    """Union-Find (Disjoint Set Union) data structure with path compression and union by rank."""
    
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x: int) -> int:
        """Find with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
        """Union by rank. Returns True if union was performed (different sets)."""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True


def kruskal(vertices: int, edges: List[Tuple[int, int, float]]) -> Dict[str, Any]:
    """
    Kruskal's MST Algorithm
    
    Args:
        vertices: Number of vertices (0 to vertices-1)
        edges: List of (u, v, weight) tuples
    
    Returns:
        Dictionary containing:
        - mst_edges: List of edges in the MST
        - total_weight: Total weight of MST
        - steps: Visualization steps for animation
        - time_ms: Execution time in milliseconds
    """
    start_time = time.perf_counter()
    
    # Sort edges by weight
    sorted_edges = sorted(edges, key=lambda x: x[2])
    
    uf = UnionFind(vertices)
    mst_edges = []
    steps = []
    total_weight = 0
    
    # Record initial state
    steps.append({
        'action': 'init',
        'message': 'Starting Kruskal\'s Algorithm - Edges sorted by weight',
        'sorted_edges': [(u, v, w) for u, v, w in sorted_edges],
        'mst_edges': [],
        'current_edge': None,
        'rejected': False
    })
    
    for u, v, weight in sorted_edges:
        # Check if adding this edge creates a cycle
        if uf.union(u, v):
            # Edge accepted - doesn't create cycle
            mst_edges.append((u, v, weight))
            total_weight += weight
            steps.append({
                'action': 'accept',
                'message': f'Edge ({u}, {v}) with weight {weight} ACCEPTED - No cycle formed',
                'current_edge': (u, v, weight),
                'mst_edges': list(mst_edges),
                'rejected': False
            })
            
            # Check if MST is complete
            if len(mst_edges) == vertices - 1:
                break
        else:
            # Edge rejected - would create cycle
            steps.append({
                'action': 'reject',
                'message': f'Edge ({u}, {v}) with weight {weight} REJECTED - Would create cycle',
                'current_edge': (u, v, weight),
                'mst_edges': list(mst_edges),
                'rejected': True
            })
    
    end_time = time.perf_counter()
    time_ms = (end_time - start_time) * 1000
    
    # Final step
    steps.append({
        'action': 'complete',
        'message': f'MST Complete! Total weight: {total_weight}',
        'mst_edges': list(mst_edges),
        'current_edge': None,
        'rejected': False
    })
    
    return {
        'algorithm': 'Kruskal',
        'mst_edges': mst_edges,
        'total_weight': total_weight,
        'steps': steps,
        'time_ms': time_ms,
        'edge_count': len(mst_edges)
    }


def kruskal_benchmark(vertices: int, edges: List[Tuple[int, int, float]], iterations: int = 10) -> Dict[str, Any]:
    """Run Kruskal's algorithm multiple times for accurate benchmarking."""
    times = []
    result = None
    
    for _ in range(iterations):
        start = time.perf_counter()
        
        sorted_edges = sorted(edges, key=lambda x: x[2])
        uf = UnionFind(vertices)
        mst_edges = []
        total_weight = 0
        
        for u, v, weight in sorted_edges:
            if uf.union(u, v):
                mst_edges.append((u, v, weight))
                total_weight += weight
                if len(mst_edges) == vertices - 1:
                    break
        
        end = time.perf_counter()
        times.append((end - start) * 1000)
        
        if result is None:
            result = {
                'mst_edges': mst_edges,
                'total_weight': total_weight
            }
    
    return {
        'algorithm': 'Kruskal',
        'mst_edges': result['mst_edges'],
        'total_weight': result['total_weight'],
        'avg_time_ms': sum(times) / len(times),
        'min_time_ms': min(times),
        'max_time_ms': max(times),
        'iterations': iterations
    }
