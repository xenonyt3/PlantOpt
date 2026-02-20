from typing import Dict, Tuple
from core.layout_engine import LayoutEngine

def calculate_total_cost(
    centroids: Dict[str, Tuple[float, float]],
    flow_matrix: Dict[Tuple[str, str], float],
    unit_cost_matrix: Dict[Tuple[str, str], float]
) -> float:
    """
    Calculates the total material handling cost of the layout.
    Objective Function = Sum( Flow(i,j) * UnitCost(i,j) * Distance(i,j) ) 
    for all pairs (i, j).
    """
    total_cost = 0.0
    
    for (i, j), flow in flow_matrix.items():
        if flow <= 0:
            continue
            
        if i not in centroids or j not in centroids:
            continue
            
        distance = LayoutEngine.calculate_distance(centroids[i], centroids[j])
        unit_cost = unit_cost_matrix.get((i, j), 0.0)
        
        total_cost += flow * unit_cost * distance
        
    return total_cost
