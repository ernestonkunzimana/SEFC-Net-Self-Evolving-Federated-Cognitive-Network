"""
Launch script for the enhanced dashboard
"""
import streamlit as st
from .enhanced_ui import ModernDashboard
from .monitor import RealTimeMonitor
import time

def main():
    """Main dashboard application"""
    dashboard = ModernDashboard()
    monitor = RealTimeMonitor()
    
    dashboard.render_header()
    
    # Sidebar controls
    st.sidebar.title("Controls")
    if st.sidebar.button("Start Evolution"):
        st.session_state.evolution_running = True
        monitor.start_monitoring()
    
    if st.sidebar.button("Stop Evolution"):
        st.session_state.evolution_running = False
        
    # Main content
    tab1, tab2, tab3 = st.tabs(["Overview", "Network", "Analytics"])
    
    with tab1:
        dashboard.render_metrics({
            'accuracy': 87.5,
            'accuracy_change': +2.3,
            'active_nodes': 5,
            'node_change': +1,
            'evolution_step': 42,
            'training_time': 156.7
        })
        monitor.render_metrics()
        
    with tab2:
        dashboard.plot_network_topology([
            {'id': f'Node{i}', 'x': i, 'y': i*0.5, 
             'status': 'active', 'load': 0.8, 'performance': 0.9}
            for i in range(5)
        ])
        
    with tab3:
        st.write("System Analytics")
        # Add analytics visualizations

if __name__ == "__main__":
    main()