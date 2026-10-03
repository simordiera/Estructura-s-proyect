from dataclasses import dataclass
from typing import Optional
from scr.models.Event import Event

# Define a Node class used to store an earthquake event in the AVL tree.
@dataclass
class Node:
    #Store the earthquake event contained in this node.
    value: 'Event'

    # Store the left child of the node.
    # It is None if the node does not have a left child.
    left: Optional['Node'] = None

    # Store the right child of the node.
    # It is None if the node does not have a right child.
    right: Optional['Node'] = None
    height: int = 1

    # A node is a leaf when it has no left or right child.
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None