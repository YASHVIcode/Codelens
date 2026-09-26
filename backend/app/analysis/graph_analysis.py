import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import networkx as nx
from models.db_models import SessionLocal, Node, Edge


def build_graph_from_db():
    session = SessionLocal()

    G = nx.DiGraph()

    nodes = session.query(Node).all()
    for node in nodes:
        G.add_node(
            node.id,
            name=node.name,
            type=node.type,
            start_line=node.start_line,
            end_line=node.end_line
        )

    edges = session.query(Edge).all()
    for edge in edges:
        G.add_edge(edge.source_node_id, edge.target_node_id)

    session.close()
    return G


def find_dead_code(G):
    entry_points = {"main", "__init__"}

    dead_nodes = []
    for node_id in G.nodes():
        node_data = G.nodes[node_id]
        if G.in_degree(node_id) == 0 and node_data["name"] not in entry_points:
            dead_nodes.append(node_data)

    return dead_nodes


def find_most_called_functions(G, top_n=5):
    in_degrees = []
    for node_id in G.nodes():
        node_data = G.nodes[node_id]
        in_degrees.append((node_data["name"], G.in_degree(node_id)))

    in_degrees.sort(key=lambda x: x[1], reverse=True)
    return in_degrees[:top_n]


def find_cycles(G):
    cycles = list(nx.simple_cycles(G))
    return cycles


def print_graph_summary(G):
    print(f"Total nodes: {G.number_of_nodes()}")
    print(f"Total edges: {G.number_of_edges()}")
    print()
    print("--- Dead Code (kisi ne bhi call nahi kiya) ---")
    dead = find_dead_code(G)
    if dead:
        for node in dead:
            print(f"  {node['type']}: {node['name']} (line {node['start_line']})")
    else:
        print("  Koi dead code nahi mila!")
    print()
    print("--- Most Called Functions ---")
    top_called = find_most_called_functions(G)
    for name, count in top_called:
        print(f"  {name}: called {count} times")
    print()
    print("--- Circular Dependencies ---")
    cycles = find_cycles(G)
    if cycles:
        for cycle in cycles:
            print(f"  {cycle}")
    else:
        print("  Koi circular dependency nahi mili!")


if __name__ == "__main__":
    G = build_graph_from_db()
    print_graph_summary(G)
