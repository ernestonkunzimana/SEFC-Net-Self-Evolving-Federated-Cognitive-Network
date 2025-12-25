"""Network graph visualization component for the dashboard."""
import plotly.graph_objects as go
import networkx as nx
from typing import Dict, List

class NetworkGraph:
    def __init__(self):
        self.G = nx.Graph()
        
    def create_graph(self, history: Dict) -> go.Figure:
        """Create an interactive network graph showing client-server communication."""
        # Create nodes
        self.G.add_node("Server", role="server")
        client_metrics = history.get("metrics_distributed_fit", {}).get("train_accuracy", [])
        if client_metrics:
            num_clients = len(client_metrics[-1])  # Get number of clients from last round
            for i in range(num_clients):
                self.G.add_node(f"Client_{i}", role="client")
                self.G.add_edge("Server", f"Client_{i}")

        # Create the visualization
        pos = nx.spring_layout(self.G)
        
        # Create edges trace
        edge_x = []
        edge_y = []
        for edge in self.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        # Create nodes trace
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        for node in self.G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            node_color.append('#00CC96' if self.G.nodes[node]['role'] == 'server' else '#636EFA')

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="bottom center",
            marker=dict(
                showscale=False,
                size=30,
                color=node_color,
                line_width=2))

        # Create the figure
        fig = go.Figure(data=[edge_trace, node_trace],
                     layout=go.Layout(
                         title='Network Topology',
                         titlefont_size=16,
                         showlegend=False,
                         hovermode='closest',
                         margin=dict(b=20,l=5,r=5,t=40),
                         annotations=[dict(
                             text="",
                             showarrow=False,
                             xref="paper", yref="paper",
                             x=0.005, y=-0.002)],
                         xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                         yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                         template="plotly_dark"
                     ))
        
        return fig