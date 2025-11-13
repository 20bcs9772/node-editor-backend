from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Set
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],          
    allow_headers=["*"],          
)


class Node(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]
    width: int
    height: int


class Edge(BaseModel):
    source: str
    sourceHandle: str
    target: str
    targetHandle: str
    type: str
    id: str


class PipelineData(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


def is_dag(nodes: List[Node], edges: List[Edge]) -> bool:
    """
    Check if the graph formed by nodes and edges is a Directed Acyclic Graph (DAG).
    Uses DFS-based cycle detection algorithm.
    
    Algorithm:
    1. Build adjacency list from edges
    2. Use DFS with three states: WHITE (unvisited), GRAY (visiting), BLACK (visited)
    3. If we encounter a GRAY node during DFS, we have a cycle
    4. If no cycles found, it's a DAG
    """
    # Build adjacency list
    graph: Dict[str, List[str]] = {node.id: [] for node in nodes}
    
    for edge in edges:
        if edge.source in graph:
            graph[edge.source].append(edge.target)
    
    # State tracking: WHITE = 0 (unvisited), GRAY = 1 (visiting), BLACK = 2 (visited)
    WHITE, GRAY, BLACK = 0, 1, 2
    state: Dict[str, int] = {node.id: WHITE for node in nodes}
    
    def has_cycle(node_id: str) -> bool:
        """
        DFS helper function to detect cycles.
        Returns True if a cycle is detected starting from node_id.
        """
        # Mark current node as being visited
        state[node_id] = GRAY
        
        # Visit all neighbors
        for neighbor in graph.get(node_id, []):
            # If neighbor is being visited (GRAY), we found a back edge = cycle
            if state[neighbor] == GRAY:
                return True
            
            # If neighbor is unvisited (WHITE), recursively check for cycles
            if state[neighbor] == WHITE:
                if has_cycle(neighbor):
                    return True
        
        # Mark current node as fully visited
        state[node_id] = BLACK
        return False
    
    # Check all nodes (handles disconnected components)
    for node in nodes:
        if state[node.id] == WHITE:
            if has_cycle(node.id):
                return False  # Cycle found, not a DAG
    
    return True  # No cycles found, it's a DAG


@app.get('/')
def read_root():
    return {'Ping': 'Pong'}


@app.post('/pipelines/parse')
def parse_pipeline(pipeline: str = Form(...)):
    """
    Parse the pipeline JSON and return:
    - num_nodes: Number of nodes in the pipeline
    - num_edges: Number of edges in the pipeline
    - is_dag: Whether the pipeline forms a Directed Acyclic Graph
    
    Args:
        pipeline: JSON string containing nodes and edges
        
    Returns:
        Dictionary with num_nodes, num_edges, and is_dag
    """
    try:
        # Parse the JSON string
        pipeline_data = json.loads(pipeline)
        
        # Extract nodes and edges
        nodes_data = pipeline_data.get('nodes', [])
        edges_data = pipeline_data.get('edges', [])
        
        # Validate and parse using Pydantic models
        nodes = [Node(**node) for node in nodes_data]
        edges = [Edge(**edge) for edge in edges_data]
        
        # Calculate metrics
        num_nodes = len(nodes)
        num_edges = len(edges)
        is_dag_result = is_dag(nodes, edges)
        
        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'is_dag': is_dag_result
        }
        
    except json.JSONDecodeError as e:
        return {
            'error': 'Invalid JSON format',
            'message': str(e),
            'num_nodes': 0,
            'num_edges': 0,
            'is_dag': False
        }
    except Exception as e:
        return {
            'error': 'Error parsing pipeline',
            'message': str(e),
            'num_nodes': 0,
            'num_edges': 0,
            'is_dag': False
        }


# Additional helper endpoint for testing
@app.post('/pipelines/validate')
def validate_pipeline(pipeline: str = Form(...)):
    """
    Extended validation endpoint that provides more detailed information.
    """
    try:
        pipeline_data = json.loads(pipeline)
        nodes_data = pipeline_data.get('nodes', [])
        edges_data = pipeline_data.get('edges', [])
        
        nodes = [Node(**node) for node in nodes_data]
        edges = [Edge(**edge) for edge in edges_data]
        
        # Basic metrics
        num_nodes = len(nodes)
        num_edges = len(edges)
        is_dag_result = is_dag(nodes, edges)
        
        # Additional analytics
        node_types = {}
        for node in nodes:
            node_types[node.type] = node_types.get(node.type, 0) + 1
        
        # Find source and sink nodes
        source_nodes = set(node.id for node in nodes)
        target_nodes = set()
        
        for edge in edges:
            target_nodes.add(edge.target)
        
        sources = list(source_nodes - target_nodes)
        sinks = list(target_nodes - source_nodes)
        
        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'is_dag': is_dag_result,
            'node_types': node_types,
            'source_nodes': sources,
            'sink_nodes': sinks
        }
        
    except Exception as e:
        return {
            'error': 'Error validating pipeline',
            'message': str(e)
        }