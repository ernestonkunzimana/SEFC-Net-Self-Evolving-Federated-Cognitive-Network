import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from typing import List, Dict

class NetworkVisualizer:
    def __init__(self):
        self.G = nx.Graph()
        
    def update_topology(self, clients: List[Dict]):
        """Update network topology"""
        self.G.clear()
        
        # Add server node
        self.G.add_node("Server", role="server")
        
        # Add client nodes
        for client in clients:
            self.G.add_node(
                client["id"],
                role="client",
                status=client["status"],
                accuracy=client["accuracy"]
            )
            self.G.add_edge("Server", client["id"])
            
    def render_topology(self, tab):
        """Render network topology visualization"""
        with tab:
            st.markdown("### Network Topology")
            
            # Generate positions
            pos = nx.spring_layout(self.G)
            
            # Create edges trace
            edge_x = []
            edge_y = []
            for edge in self.G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                
            edges_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Create nodes trace
            node_x = []
            node_y = []
            node_text = []
            node_color = []
            
            for node in self.G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                role = self.G.nodes[node].get('role', 'unknown')
                status = self.G.nodes[node].get('status', 'unknown')
                accuracy = self.G.nodes[node].get('accuracy', 0)
                
                node_text.append(
                    f"Node: {node}<br>"
                    f"Role: {role}<br>"
                    f"Status: {status}<br>"
                    f"Accuracy: {accuracy:.2f}%"
                )
                
                node_color.append(
                    '#00ff00' if status == 'active' else '#ff0000'
                )
                
            nodes_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                marker=dict(
                    size=20,
                    color=node_color,
                    line_width=2
                )
            )
            
            # Create figure
            fig = go.Figure(
                data=[edges_trace, nodes_trace],
                layout=go.Layout(
                    title='Federation Network Topology',
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)