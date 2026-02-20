import numpy as np
from typing import Dict, Tuple, List

class LayoutEngine:
    """
    Handles operations on the 2D layout grid, such as calculating centroids 
    and rectilinear distances.
    """
    
    @staticmethod
    def calculate_centroids(grid: np.ndarray) -> Dict[str, Tuple[float, float]]:
        """
        Calculates the centroid (x, y) for each department in the grid.
        Assuming row index is Y and column index is X for Cartesian feel, 
        or standard matrix (row=Y, col=X). Let's use (row, col) as (y, x) 
        and centroid = (mean_x, mean_y).
        
        Returns:
            Dict mapping department ID to its centroid (x, y)
        """
        centroids = {}
        unique_deps = np.unique(grid)
        
        for dep in unique_deps:
            # Skip empty cells if represented by empty string or specific null value
            if dep == "" or dep == None:
                continue
                
            y_coords, x_coords = np.where(grid == dep)
            if len(x_coords) > 0 and len(y_coords) > 0:
                mean_x = np.mean(x_coords)
                mean_y = np.mean(y_coords)
                centroids[dep] = (mean_x, mean_y)
                
        return centroids
    
    @staticmethod
    def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """
        Calculates the rectilinear (Manhattan) distance between two points.
        """
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    @staticmethod
    def are_adjacent(grid: np.ndarray, dep1: str, dep2: str) -> bool:
        """
        Checks if two departments share a border (orthogonal adjacency).
        """
        rows, cols = grid.shape
        y1, x1 = np.where(grid == dep1)
        
        for y, x in zip(y1, x1):
            # Check neighbors: up, down, left, right
            neighbors = [
                (y-1, x), (y+1, x),
                (y, x-1), (y, x+1)
            ]
            for ny, nx in neighbors:
                if 0 <= ny < rows and 0 <= nx < cols:
                    if grid[ny, nx] == dep2:
                        return True
        return False
        
    @staticmethod
    def get_areas(grid: np.ndarray) -> Dict[str, int]:
        """
        Calculates the area (number of grid cells) for each department.
        """
        areas = {}
        unique_deps, counts = np.unique(grid, return_counts=True)
        for dep, count in zip(unique_deps, counts):
            if dep != "" and dep != None:
                areas[dep] = count
        return areas

    @staticmethod
    def swap_departments(grid: np.ndarray, dep1: str, dep2: str) -> np.ndarray:
        """
        Swaps two departments in the grid.
        To handle unequal sizes gracefully and preserve area:
        - We take the combined region of both departments.
        - We assign the N1 cells closest to dep2's old centroid to dep1.
        - We assign the remaining N2 cells to dep2.
        This provides a heuristic spatial swap that keeps areas constant.
        """
        new_grid = grid.copy()
        
        y1, x1 = np.where(grid == dep1)
        y2, x2 = np.where(grid == dep2)
        
        n1 = len(x1)
        n2 = len(x2)
        
        if n1 == 0 or n2 == 0:
            return new_grid
            
        c1_x, c1_y = np.mean(x1), np.mean(y1)
        c2_x, c2_y = np.mean(x2), np.mean(y2)
        
        combined_y = np.concatenate([y1, y2])
        combined_x = np.concatenate([x1, x2])
        
        # We want dep1 to be near c2, and dep2 near c1.
        # So we sort all combined cells by distance to c2
        cells = list(zip(combined_y, combined_x))
        
        # Sort by distance to c2 (dep2's original centroid)
        cells.sort(key=lambda p: abs(p[1] - c2_x) + abs(p[0] - c2_y))
        
        # The closest n1 cells go to dep1
        dep1_cells = cells[:n1]
        # The rest go to dep2
        dep2_cells = cells[n1:]
        
        for y, x in dep1_cells:
            new_grid[y, x] = dep1
            
        for y, x in dep2_cells:
            new_grid[y, x] = dep2
            
        return new_grid
