from dataclasses import dataclass
from typing import Optional

@dataclass
class Node:
    value: 'Event'
    left: Optional['Node'] = None
    right: Optional['Node'] = None
    height: int = 1

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None