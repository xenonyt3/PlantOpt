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
    
    unique_deps = [d for d in np.unique(grid) if str(d).strip() != "" and d is not None]
    dep_to_num = {dep: i for i, dep in enumerate(unique_deps)}
    
    numeric_grid = np.zeros(grid.shape)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            val = grid[i, j]
            if val in dep_to_num:
                numeric_grid[i, j] = dep_to_num[val]
            else:
                numeric_grid[i, j] = -1 # Background
                
    cmap = sns.color_palette("Set3", max(1, len(unique_deps))) # safeguard empty
    
    # We should mask out the background cells (-1) so they don't get colored
    mask = (numeric_grid == -1)
    
    sns.heatmap(numeric_grid, annot=grid, fmt="", cmap=cmap, cbar=False, 
                linewidths=1, linecolor='black', ax=ax,
                annot_kws={"size": 14, "weight": "bold"}, mask=mask)
    
    ax.set_title(title)
    ax.axis('off')
    return fig

def init_session_state():
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'dep_df' not in st.session_state:
        st.session_state.dep_df = pd.DataFrame({
            'ID': ['A', 'B', 'C', 'D'], 
            'Name': ['Dept A', 'Dept B', 'Dept C', 'Dept D'], 
            'Area': [2, 2, 2, 3]
        })
    if 'flow_df' not in st.session_state:
        st.session_state.flow_df = None
    if 'grid_rows' not in st.session_state:
        st.session_state.grid_rows = 3
    if 'grid_cols' not in st.session_state:
        st.session_state.grid_cols = 3
    if 'layout_df' not in st.session_state:
        st.session_state.layout_df = None
    if 'results' not in st.session_state:
        st.session_state.results = None

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()

def main():
    st.title("🏭 CRAFT Facility Layout Optimization")
    st.markdown("Computerized Relative Allocation of Facilities Technique (QS-Style Flow)")
    
    init_session_state()
    
    # Sidebar progress
    st.sidebar.title("Progress")
    steps = [
        "1️⃣ Departments & Area",
        "2️⃣ Flow Matrix",
        "3️⃣ Initial Layout",
        "4️⃣ Calculate Cost & Run CRAFT",
        "5️⃣ Results"
    ]
    
    for i, s in enumerate(steps, 1):
        if i == st.session_state.step:
            st.sidebar.markdown(f"**👉 {s}**")
        elif i < st.session_state.step:
            st.sidebar.markdown(f"✅ {s}")
        else:
            st.sidebar.markdown(f"⏳ {s}")
            
    st.sidebar.markdown("---")
    if st.sidebar.button("Restart completely"):
         reset_app()
         st.rerun()

    if st.session_state.step == 1:
        st.header("Step 1: Input Departments & Areas")
        st.markdown("Define the departments in your facility and their required area (number of grid blocks).")
        
        num_deps = st.number_input("Number of Departments", min_value=2, max_value=20, value=len(st.session_state.dep_df))
        
        # Adjust dataframe size
        current_len = len(st.session_state.dep_df)
        if num_deps > current_len:
            new_rows = pd.DataFrame({
                'ID': [chr(65 + i) for i in range(current_len, num_deps)], 
                'Name': [f'Dept {chr(65 + i)}' for i in range(current_len, num_deps)], 
                'Area': [1] * (num_deps - current_len)
            })
            st.session_state.dep_df = pd.concat([st.session_state.dep_df, new_rows], ignore_index=True)
        elif num_deps < current_len:
            st.session_state.dep_df = st.session_state.dep_df.iloc[:num_deps]
            
        st.session_state.dep_df = st.data_editor(st.session_state.dep_df, use_container_width=True, hide_index=True)
        
        # Validation
        if len(st.session_state.dep_df['ID'].unique()) != len(st.session_state.dep_df):
            st.error("Department IDs must be unique!")
        elif st.session_state.dep_df['Area'].min() <= 0:
            st.error("Areas must be greater than 0!")
        else:
            if st.button("Next: Flow Matrix ➡️", type="primary"):
                # Initialize flow matrix if not set or size changed
                ids = st.session_state.dep_df['ID'].tolist()
                
                # Check if we need to rebuild flow df
                rebuild = True
                if st.session_state.flow_df is not None:
                    if list(st.session_state.flow_df.columns) == ids and list(st.session_state.flow_df.index) == ids:
                        rebuild = False
                        
                if rebuild:
                    # Create empty matrix
                    st.session_state.flow_df = pd.DataFrame(0.0, index=ids, columns=ids)
                    
                    # Try to preserve toy problem defaults if it matches
                    if set(ids) == {'A', 'B', 'C', 'D'}:
                        default_flows = {
                            ('A', 'B'): 10, ('A', 'D'): 50,
                            ('B', 'C'): 20, ('C', 'D'): 30
                        }
                        for (f, t), val in default_flows.items():
                            st.session_state.flow_df.at[f, t] = val
                            st.session_state.flow_df.at[t, f] = val # symmetric
                            
                next_step()
                st.rerun()

    elif st.session_state.step == 2:
        st.header("Step 2: Input From-To Flow Matrix")
        st.markdown("Enter the material flow or frequency between departments.")
        if st.button("⬅️ Back"):
            prev_step()
            st.rerun()
            
        st.session_state.flow_df = st.data_editor(st.session_state.flow_df, use_container_width=True)
        
        if st.button("Next: Initial Layout ➡️", type="primary"):
            next_step()
            st.rerun()
            
    elif st.session_state.step == 3:
        st.header("Step 3: Generate / Input Initial Layout")
        if st.button("⬅️ Back"):
            prev_step()
            st.rerun()
            
        total_area = st.session_state.dep_df['Area'].sum()
        st.info(f"Total required area: {total_area} blocks.")
        
        col1, col2 = st.columns(2)
        with col1:
            rows = int(st.number_input("Grid Rows", min_value=1, max_value=50, value=int(st.session_state.grid_rows)))
        with col2:
            cols = int(st.number_input("Grid Columns", min_value=1, max_value=50, value=int(st.session_state.grid_cols)))
            
        st.session_state.grid_rows = rows
        st.session_state.grid_cols = cols
        
        if rows * cols < total_area:
            st.error(f"Grid size ({rows*cols}) is smaller than total required area ({total_area}). Please increase dimensions.")
        else:
            # Generate initial grid if needed
            rebuild_layout = False
            if st.session_state.layout_df is None or st.session_state.layout_df.shape != (rows, cols):
                rebuild_layout = True
                
            if st.button("Generate Default Grid Layout", help="Fills the grid sequentially with department IDs"):
                rebuild_layout = True
                
            if rebuild_layout:
                flat_grid = []
                for _, row in st.session_state.dep_df.iterrows():
                    flat_grid.extend([row['ID']] * int(row['Area']))
                
                # pad with empty
                flat_grid.extend([""] * (rows * cols - len(flat_grid)))
                
                grid_arr = np.array(flat_grid).reshape((rows, cols))
                st.session_state.layout_df = pd.DataFrame(grid_arr, columns=[str(i) for i in range(cols)])
            
            st.markdown("### Edit Grid")
            st.markdown("Ensure every department has the correct total blocks. Empty cells should be left blank.")
            st.session_state.layout_df = st.data_editor(st.session_state.layout_df, use_container_width=True)
            
            # Validation
            flat_current = st.session_state.layout_df.values.flatten()
            counts = {d: 0 for d in st.session_state.dep_df['ID']}
            for v in flat_current:
                if v in counts:
                    counts[v] += 1
            
            error_msgs = []
            for _, row in st.session_state.dep_df.iterrows():
                expected = int(row['Area'])
                actual = counts[row['ID']]
                if expected != actual:
                    error_msgs.append(f"{row['ID']} (Expected: {expected}, Actual: {actual})")
                    
            if error_msgs:
                st.error("Area mismatch for departments: " + ", ".join(error_msgs))
            else:
                if st.button("Next: Calculate & Optimize ➡️", type="primary"):
                    next_step()
                    st.rerun()

    elif st.session_state.step == 4:
        st.header("Step 4 & 5: Calculate Cost & Run CRAFT")
        st.markdown("We are ready to calculate the initial layout cost and run the CRAFT algorithm to minimize material handling.")
        
        if st.button("⬅️ Back"):
            prev_step()
            st.rerun()
            
        max_iter = st.number_input("Max Iterations", min_value=1, max_value=200, value=50)
        
        if st.button("🚀 Run CRAFT Algorithm", type="primary"):
            with st.spinner("Optimizing..."):
                # Prepare data for CRAFT
                grid = st.session_state.layout_df.values.astype(object)
                
                # CRAFT core expects empty to be empty string
                grid[pd.isna(grid)] = ""
                
                flow_matrix = {}
                flow_df = st.session_state.flow_df
                for f in flow_df.index:
                    for t in flow_df.columns:
                        try:
                            val = float(flow_df.at[f, t])
                        except:
                            val = 0.0
                        if val > 0:
                            flow_matrix[(f, t)] = val
                        
                cost_matrix = {k: 1.0 for k in flow_matrix.keys()}
                
                craft = CRAFT(grid, flow_matrix, cost_matrix)
                initial_cost = craft.evaluate_grid(craft.grid)
                
                best_grid, final_cost = craft.optimize(max_iter=int(max_iter))
                
                st.session_state.results = {
                    'initial_cost': initial_cost,
                    'final_cost': final_cost,
                    'initial_grid': grid,
                    'optimized_grid': best_grid,
                    'cost_history': craft.cost_history
                }
                
                st.success("Optimization Complete!")
                next_step()
                time.sleep(0.5)
                st.rerun()

    elif st.session_state.step == 5:
        st.header("Step 6: Results")
        
        if st.button("⬅️ Restart Configuration"):
            st.session_state.step = 1
            st.rerun()
            
        res = st.session_state.results
        if not res:
            st.error("No results found. Please go back and run the optimization.")
            return
            
        initial_cost = res['initial_cost']
        final_cost = res['final_cost']
        improvement = 0 if initial_cost == 0 else (initial_cost - final_cost) / initial_cost * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Initial Cost", f"{initial_cost:.2f}")
        col2.metric("Final Cost", f"{final_cost:.2f}")
        col3.metric("Improvement", f"{improvement:.1f}%", f"{initial_cost - final_cost:.2f}")
        
        # Heatmaps
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.subheader("Initial Layout")
            fig1 = plot_grid(res['initial_grid'], "Before CRAFT")
            st.pyplot(fig1)
            
        with col_m2:
            st.subheader("Optimized Layout")
            fig2 = plot_grid(res['optimized_grid'], "After CRAFT")
            st.pyplot(fig2)
            
        # Cost History
        st.subheader("Iteration History")
        fig_hist, ax_hist = plt.subplots(figsize=(8, 4))
        ax_hist.plot(res['cost_history'], marker='o', linestyle='-', color='b')
        ax_hist.set_xlabel("Iteration")
        ax_hist.set_ylabel("Total Material Handling Cost")
        ax_hist.set_title("Objective Function Value over CRAFT Iterations")
        ax_hist.grid(True)
        st.pyplot(fig_hist)


if __name__ == "__main__":
    main()
