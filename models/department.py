from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Department:
    """
    Represents a facility department in the layout grid.
    """
    id: str
    name: str
    area: int
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, Department):
            return False
        return self.id == other.id
