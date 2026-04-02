import time
from typing import List, Tuple, Dict, Any

class UnionFind:
    
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.component_count = n
    
    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        self.component_count -= 1
        return True
    
    def get_components(self) -> Dict[int, List[int]]:
        """Get all vertices grouped by their component."""
        components = {}
        for i in range(len(self.parent)):
            root = self.find(i)
            if root not in components:
                components[root] = []
            components[root].append(i)
        return components


def boruvka(vertices: int, edges: List[Tuple[int, int, float]]) -> Dict[str, Any]:

    start_time = time.perf_counter()
    
    uf = UnionFind(vertices)
    mst_edges = []
    total_weight = 0
    steps = []
    iteration = 0
    
    steps.append({
        'action': 'init',
        'message': f'Starting Boruvka\'s Algorithm with {vertices} components',
        'mst_edges': [],
        'components': {i: [i] for i in range(vertices)},
        'iteration': 0,
        'cheapest_edges': []
    })
    
    while uf.component_count > 1 and len(mst_edges) < vertices - 1:
        iteration += 1
        
        # Find cheapest edge for each component
        cheapest = {}  # component_root -> (weight, u, v)
        
        for u, v, weight in edges:
            comp_u = uf.find(u)
            comp_v = uf.find(v)
            
            if comp_u != comp_v:
                # Check if this is the cheapest edge for comp_u
                if comp_u not in cheapest or weight < cheapest[comp_u][0]:
                    cheapest[comp_u] = (weight, u, v)
                # Check if this is the cheapest edge for comp_v
                if comp_v not in cheapest or weight < cheapest[comp_v][0]:
                    cheapest[comp_v] = (weight, u, v)
        
        if not cheapest:
            break
        
        # Record the cheapest edges found
        cheapest_edges = [(u, v, w) for w, u, v in cheapest.values()]
        steps.append({
            'action': 'find_cheapest',
            'message': f'Iteration {iteration}: Found cheapest edges for each component',
            'iteration': iteration,
            'cheapest_edges': cheapest_edges,
            'mst_edges': list(mst_edges),
            'components': uf.get_components()
        })
        
        # Add all cheapest edges (avoiding duplicates)
        added_this_round = []
        for weight, u, v in cheapest.values():
            if uf.union(u, v):
                mst_edges.append((u, v, weight))
                total_weight += weight
                added_this_round.append((u, v, weight))
        
        if added_this_round:
            steps.append({
                'action': 'merge',
                'message': f'Iteration {iteration}: Added {len(added_this_round)} edges, {uf.component_count} components remaining',
                'iteration': iteration,
                'added_edges': added_this_round,
                'mst_edges': list(mst_edges),
                'components': uf.get_components()
            })
    
    end_time = time.perf_counter()
    time_ms = (end_time - start_time) * 1000
    
    # Final step
    steps.append({
        'action': 'complete',
        'message': f'MST Complete! Total weight: {total_weight} after {iteration} iterations',
        'mst_edges': list(mst_edges),
        'components': uf.get_components(),
        'iteration': iteration
    })
    
    return {
        'algorithm': 'Boruvka',
        'mst_edges': mst_edges,
        'total_weight': total_weight,
        'steps': steps,
        'time_ms': time_ms,
        'edge_count': len(mst_edges),
        'iterations': iteration
    }


def boruvka_benchmark(vertices: int, edges: List[Tuple[int, int, float]], iterations: int = 10) -> Dict[str, Any]:
    """Run Boruvka's algorithm multiple times for accurate benchmarking."""
    times = []
    result = None
    
    for _ in range(iterations):
        start = time.perf_counter()
        
        uf = UnionFind(vertices)
        mst_edges = []
        total_weight = 0
        
        while uf.component_count > 1 and len(mst_edges) < vertices - 1:
            cheapest = {}
            
            for u, v, weight in edges:
                comp_u = uf.find(u)
                comp_v = uf.find(v)
                
                if comp_u != comp_v:
                    if comp_u not in cheapest or weight < cheapest[comp_u][0]:
                        cheapest[comp_u] = (weight, u, v)
                    if comp_v not in cheapest or weight < cheapest[comp_v][0]:
                        cheapest[comp_v] = (weight, u, v)
            
            if not cheapest:
                break
            
            for weight, u, v in cheapest.values():
                if uf.union(u, v):
                    mst_edges.append((u, v, weight))
                    total_weight += weight
        
        end = time.perf_counter()
        times.append((end - start) * 1000)
        
        if result is None:
            result = {
                'mst_edges': mst_edges,
                'total_weight': total_weight
            }
    
    return {
        'algorithm': 'Boruvka',
        'mst_edges': result['mst_edges'],
        'total_weight': result['total_weight'],
        'avg_time_ms': sum(times) / len(times),
        'min_time_ms': min(times),
        'max_time_ms': max(times),
        'iterations': iterations
    }
