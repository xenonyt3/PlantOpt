import numpy as np
from core.craft import CRAFT
from core.layout_engine import LayoutEngine

def test_craft():
    grid = np.array([
        ['A', 'A', 'B'],
        ['A', 'C', 'B'],
        ['D', 'C', 'D']
    ], dtype=object)
    
    flow_matrix = {
        ('A', 'B'): 10, ('B', 'A'): 10,
        ('A', 'C'): 0,  ('C', 'A'): 0,
        ('A', 'D'): 50, ('D', 'A'): 50,
        ('B', 'C'): 20, ('C', 'B'): 20,
        ('B', 'D'): 0,  ('D', 'B'): 0,
        ('C', 'D'): 30, ('D', 'C'): 30
    }
    
    # Unit cost is 1.0 for all pair flows
    cost_matrix = {k: 1.0 for k in flow_matrix.keys()}
    
    craft = CRAFT(grid, flow_matrix, cost_matrix)
    initial_cost = craft.evaluate_grid(grid)
    print("Initial Cost:", initial_cost)
    
    best_grid, final_cost = craft.optimize(max_iter=10)
    print("Final Cost:", final_cost)
    print("Cost History:", craft.cost_history)
    print("Optimized Grid:\n", best_grid)
    
    assert final_cost <= initial_cost
    print("Test passed successfully!")

if __name__ == "__main__":
    test_craft()
