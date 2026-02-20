import numpy as np
from typing import Dict, Tuple, List, Optional
from core.layout_engine import LayoutEngine
from core.cost import calculate_total_cost

class CRAFT:
    """
    Implements the CRAFT heuristic algorithm.
    """
    def __init__(self, 
                 initial_grid: np.ndarray,
                 flow_matrix: Dict[Tuple[str, str], float],
                 unit_cost_matrix: Dict[Tuple[str, str], float]):
        self.grid = initial_grid.copy()
        self.flow_matrix = flow_matrix
        self.unit_cost_matrix = unit_cost_matrix
        self.cost_history = []
        
    def evaluate_grid(self, grid: np.ndarray) -> float:
        centroids = LayoutEngine.calculate_centroids(grid)
        return calculate_total_cost(centroids, self.flow_matrix, self.unit_cost_matrix)

    def optimize_step(self) -> Tuple[bool, np.ndarray, float, Optional[Tuple[str, str]]]:
        """
        Performs one iteration of the CRAFT algorithm.
        Returns:
            (improvement_found, new_grid, new_cost, best_swap_pair)
        """
        current_cost = self.evaluate_grid(self.grid)
        if len(self.cost_history) == 0:
            self.cost_history.append(current_cost)
            
        departments = [str(d) for d in np.unique(self.grid) if str(d).strip() != "" and d is not None]
        areas = LayoutEngine.get_areas(self.grid)
        
        best_cost = current_cost
        best_grid = self.grid.copy()
        best_swap = None
        
        # Evaluate all valid pairs
        for i in range(len(departments)):
            for j in range(i + 1, len(departments)):
                dep1 = departments[i]
                dep2 = departments[j]
                
                # CRAFT validity condition: same area or adjacent
                valid_swap = False
                if areas[dep1] == areas[dep2]:
                    valid_swap = True
                elif LayoutEngine.are_adjacent(self.grid, dep1, dep2):
                    valid_swap = True
                    
                if valid_swap:
                    # Try swapping
                    test_grid = LayoutEngine.swap_departments(self.grid, dep1, dep2)
                    test_cost = self.evaluate_grid(test_grid)
                    
                    if test_cost < best_cost:
                        best_cost = test_cost
                        best_grid = test_grid
                        best_swap = (dep1, dep2)
                        
        if best_swap is not None and best_cost < current_cost:
            self.grid = best_grid
            self.cost_history.append(best_cost)
            return True, best_grid, best_cost, best_swap
            
        return False, self.grid, current_cost, None

    def optimize(self, max_iter: int = 50) -> Tuple[np.ndarray, float]:
        """
        Runs the full optimization until no further improvements can be found
        or max_iter is reached.
        """
        for _ in range(max_iter):
            improved, grid, cost, swap = self.optimize_step()
            if not improved:
                break
        return self.grid, self.evaluate_grid(self.grid)
