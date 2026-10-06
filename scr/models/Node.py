from dataclasses import dataclass
from typing import Optional
from scr.models.Event import Event

# Store one event and its links in a tree node.
@dataclass
class Node:
    # Event stored in the node.
    value: 'Event'

    # Left child, or None when absent.
    left: Optional['Node'] = None

    # Right child, or None when absent.
    right: Optional['Node'] = None
    height: int = 1

    # A node is a leaf when both children are absent.
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None