import random, math, networkx as nx, numpy as np
from collections import defaultdict
from cpex.constants import STATUS_PENDING
from cpex import config
from typing import Tuple

weight_key = 'weight'
min_weight, max_weight = 0.1, 1

def compute_shortest_paths(graph: nx.Graph, weighted:bool = True) -> dict:
    if weighted:
        for (src, dst) in graph.edges():
            graph[src][dst][weight_key] = random.uniform(0.1, 1)
    
    return nx.johnson(graph, weight=weight_key)

def get_all_routes(shortest_paths: dict) -> Tuple:
    routes = []
    num_providers = len(shortest_paths)
    min_hops, max_hops, total = float('inf'), float('-inf'), 0
    
    for src in range(num_providers):
        for dst in range(src+1, num_providers):
            hops = len(shortest_paths[src][dst])
            total += hops
            min_hops = min(min_hops, hops)
            max_hops = max(max_hops, hops)
            routes.append(shortest_paths[src][dst])

    return routes, (min_hops, round(total/len(routes)), max_hops)

def get_stirshaken_adopters(graph: nx.Graph, deploy_rate: float) -> dict:
    degrees = np.array([degree for node, degree in graph.degree()])
    total_degree = degrees.sum()
    adopter_nodes = np.random.choice(
        graph.nodes(),
        replace = False,
        p = degrees / total_degree,
        size = math.ceil((deploy_rate / 100) * len(degrees))
    )
    return defaultdict(lambda: 0, { int(node): 1 for node in adopter_nodes})

def create(num_providers:int, deploy_rate: float = config.SS_DEPLOY_RATE) -> Tuple[list, dict]:
    graph = nx.barabasi_albert_graph(n=num_providers, m=2)
    routes, stats = get_all_routes(compute_shortest_paths(graph=graph))
    adopters = get_stirshaken_adopters(graph=graph, deploy_rate=deploy_rate)
    data = []
    index = 1
    for i, route in enumerate(routes):
        _route = [(r, adopters[int(r)]) for r in route]
        if all([r[1] == 1 for r in _route]):
            continue
        data.append({
            '_id': index,
            'status': STATUS_PENDING,
            'route': _route
        })
        index += 1
        
    data = [{'_id': 0, 'total': len(data), 'all': len(routes)}] + data
    
    return data, stats
