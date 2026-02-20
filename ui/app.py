import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import sys
import os

# Add parent directory to path to allow imports from core module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.craft import CRAFT

st.set_page_config(page_title="CRAFT Layout Optimizer", layout="wide")

def plot_grid(grid: np.ndarray, title: str):
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Create a numeric mapping for colors
    unique_deps = [d for d in np.unique(grid) if str(d).strip() != "" and d is not None]
    dep_to_num = {dep: i for i, dep in enumerate(unique_deps)}
    
    # Map the grid to numeric
    numeric_grid = np.zeros(grid.shape)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            val = grid[i, j]
            if val in dep_to_num:
                numeric_grid[i, j] = dep_to_num[val]
            else:
                numeric_grid[i, j] = -1 # Background
                
    cmap = sns.color_palette("Set3", len(unique_deps))
    # Add a white color for background if needed, but we assume all cells are filled in toy problem
    
    sns.heatmap(numeric_grid, annot=grid, fmt="", cmap=cmap, cbar=False, 
                linewidths=1, linecolor='black', ax=ax,
                annot_kws={"size": 14, "weight": "bold"})
    
    ax.set_title(title)
    ax.axis('off')
    return fig

def main():
    st.title("🏭 CRAFT Facility Layout Optimization")
    st.markdown("Computerized Relative Allocation of Facilities Technique")
    
    # Dummy data setup
    st.sidebar.header("Configuration")
    
    data_source = st.sidebar.radio("Data Source", ["Toy Problem", "Upload Custom CSVs"])
    
    if data_source == "Toy Problem":
        st.session_state.initial_grid = np.array([
            ['A', 'A', 'B'],
            ['A', 'C', 'B'],
            ['D', 'C', 'D']
        ], dtype=object)
        
        st.session_state.flow_matrix = {
            ('A', 'B'): 10, ('B', 'A'): 10,
            ('A', 'C'): 0,  ('C', 'A'): 0,
            ('A', 'D'): 50, ('D', 'A'): 50,
            ('B', 'C'): 20, ('C', 'B'): 20,
            ('B', 'D'): 0,  ('D', 'B'): 0,
            ('C', 'D'): 30, ('D', 'C'): 30
        }
    else:
        st.sidebar.markdown("### Upload Files")
        layout_file = st.sidebar.file_uploader("Upload Initial Layout (CSV)", type=['csv'])
        flow_file = st.sidebar.file_uploader("Upload Flow/Cost Matrix (CSV)", type=['csv'])
        
        if layout_file is not None and flow_file is not None:
            try:
                # Read layout (no header expected if it's just a grid of department IDs)
                df_layout = pd.read_csv(layout_file, header=None)
                st.session_state.initial_grid = df_layout.values.astype(object)
                
                # Flow matrix is uploaded as an adjacency list or matrix. 
                # For simplicity, let's assume it's a list: From, To, Flow, (optional Cost)
                df_flow = pd.read_csv(flow_file)
                st.session_state.flow_matrix = {}
                
                # Check columns to allow generic flow data
                cols = [c.strip().lower() for c in df_flow.columns]
                
                if 'from' in cols and 'to' in cols and 'flow' in cols:
                    for _, row in df_flow.iterrows():
                        f = str(row.iloc[cols.index('from')]).strip()
                        t = str(row.iloc[cols.index('to')]).strip()
                        flow_val = float(row.iloc[cols.index('flow')])
                        st.session_state.flow_matrix[(f, t)] = flow_val
                        # Ensure bidirectional existence if not provided
                        if (t, f) not in st.session_state.flow_matrix:
                            st.session_state.flow_matrix[(t, f)] = flow_val
                else:
                    st.sidebar.error("Flow CSV must contain columns: 'From', 'To', 'Flow'")
            except Exception as e:
                st.sidebar.error(f"Error parsing files: {e}")
                
    # Initialize state variables
    if 'initial_grid' not in st.session_state:
        st.session_state.initial_grid = None
    if 'flow_matrix' not in st.session_state:
        st.session_state.flow_matrix = {}
        
    st.session_state.cost_matrix = {
        k: 1.0 for k in st.session_state.flow_matrix.keys()
    }
    
    if 'craft_runner' not in st.session_state:
        st.session_state.craft_runner = None
        st.session_state.optimized = False
        st.session_state.optimized_grid = None
        st.session_state.cost_history = []
        
    if st.session_state.initial_grid is None or not st.session_state.flow_matrix:
        st.warning("Please select the Toy Problem or upload valid CSV files to proceed.")
        return
        
    st.sidebar.subheader("Initial Layout")
    st.sidebar.dataframe(pd.DataFrame(st.session_state.initial_grid))
    
    # We display a simplified table of nonzero flows
    flows = []
    for k, v in st.session_state.flow_matrix.items():
        if k[0] < k[1]:  # Just show one direction for symmetry if applicable
            flows.append({'From': k[0], 'To': k[1], 'Flow': v})
    st.sidebar.subheader("Flow Matrix")
    st.sidebar.dataframe(pd.DataFrame(flows))

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Layout")
        if not st.session_state.optimized:
            fig = plot_grid(st.session_state.initial_grid, "Initial Layout")
            st.pyplot(fig)
        else:
            fig = plot_grid(st.session_state.optimized_grid, "Optimized Layout")
            st.pyplot(fig)
            
    with col2:
        st.subheader("Optimization Controls")
        
        if st.button("Run CRAFT Optimization", type="primary"):
            with st.spinner("Optimizing layout..."):
                craft = CRAFT(
                    st.session_state.initial_grid,
                    st.session_state.flow_matrix,
                    st.session_state.cost_matrix
                )
                
                initial_cost = craft.evaluate_grid(craft.grid)
                
                # Perform full optimization
                best_grid, final_cost = craft.optimize(max_iter=50)
                
                st.session_state.optimized_grid = best_grid
                st.session_state.cost_history = craft.cost_history
                st.session_state.optimized = True
                st.success("Optimization Complete!")
                
                st.metric("Initial Cost", f"{initial_cost:.2f}")
                st.metric("Final Cost", f"{final_cost:.2f}")
                st.metric("Cost Reduction", f"{initial_cost - final_cost:.2f} ({(initial_cost - final_cost)/initial_cost*100:.1f}%)")

        if st.session_state.optimized:
            st.subheader("Cost History")
            fig_hist, ax_hist = plt.subplots(figsize=(6, 4))
            ax_hist.plot(st.session_state.cost_history, marker='o', linestyle='-', color='b')
            ax_hist.set_xlabel("Iteration")
            ax_hist.set_ylabel("Total Cost")
            ax_hist.set_title("Objective Function Value over Iterations")
            ax_hist.grid(True)
            st.pyplot(fig_hist)
            
            if st.button("Reset"):
                st.session_state.optimized = False
                st.rerun()

if __name__ == "__main__":
    main()
