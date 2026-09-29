from collections import deque
from typing import Optional
from scr.models.Node import Node
from scr.models.Metrics import Metrics


class BST:
    def __init__(self):
        self.root = None
        self.list_deleted=[]
        self.list_historic = []
        self.retired_ids = set()
        self.associations = {}
        self.metrics = Metrics()
        self.simulation_clock = None
        self.archive_age_hours = 72

    def insert(self, value) -> None:
        for i in range (len(self.list_deleted)):
            if (self.list_deleted[i]== value.get_id()):
                return None
        self.root = self._insert(self.root, value)

    def _insert(self, node: Optional[Node], value) -> Node:

        if node is None:
            return Node(value)
        value_key = value.get_code()
        node_key = node.value.get_code()
        
        if value_key[0] != node_key[0]:
            if value_key[0] < node_key[0]:
                node.left = self._insert(node.left, value)

            elif value_key[0] > node_key[0]:
                node.right = self._insert(node.right, value)

        elif value_key[1] != node_key[1]:
            if value_key[1] < node_key[1]:
                node.left = self._insert(node.left, value)

            elif value_key[1] > node_key[1]:
                node.right = self._insert(node.right, value)

        elif value_key[2] != node_key[2]:
            if value_key[2] < node_key[2]:
                node.left = self._insert(node.left, value)

            elif value_key[2] > node_key[2]:
                node.right = self._insert(node.right, value)

        else:
            return node

        return node
        

    def pre_order(self) -> None:
        if self.root is None:
            return
        items = []
        items = self._pre_order(self.root, items)
        return items

    def _pre_order(self, root: Node, items) -> None:
        if root is None:
            return items
        items.append(root.value)
        items = self._pre_order(root.left, items)
        items = self._pre_order(root.right, items)
        return items

    def in_order(self)->None:
        if self.root is None:
            return
        items = []
        self._in_order(self.root, items)
        return items

    def _in_order(self, root: Node, items) -> None:
        if root is None:
            return items
        items = self._in_order(root.left, items)
        items.append(root.value)
        items = self._in_order(root.right, items)
        return items

    def post_order(self)->None:
        if self.root is None:
            return
        items = []
        self._post_order(self.root, items)
        return items

    def _post_order(self, root: Node, items) -> None:
        if root is None:
            return items
        items = self._post_order(root.left, items)
        items = self._post_order(root.right, items)
        items.append(root.value)
        return items
    
    def breadth_first(self) -> None:
        if self.root is None:
            return
        items = []
        return self._breadth_first(self.root, items)

    def _breadth_first(self, root: Node, items) -> None:
        queue = deque([root])
        while queue:
            node = queue.popleft()
            items.append(node.value)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        return items

    def _find_minimum(self, root: Node) -> Node:
        current = root
        while current.left is not None:
            current = current.left
        print(" ")
        return current


    def research(self, id,) -> None:
        return  self._research(self.root, id)
    
    def _research(self, node: Optional[Node], id) -> Node:

        if node is None:
            return None

        value_key = id
        node_key = node.value.get_code()

        if value_key == node_key[2]:
            return node

        else:
            result = self._research(node.left, id)

            if result is not None:
                return result

            return self._research(node.right, id)

    def delete(self, id):
        earthquake = self.research(id)
        if earthquake is None or id in self.retired_ids:
            return None

        deleted_event = earthquake.value
        self.root = self._delete(self.root, earthquake.value.get_code())
        self.list_deleted.append(id)
        self.retired_ids.add(id)
        return Node(deleted_event)

    def _delete(self, root: Optional[Node], key) -> Optional[Node]:
        if root is None:
            return None

        root_key = root.value.get_code()
        if key < root_key:
            root.left = self._delete(root.left, key)
        elif key > root_key:
            root.right = self._delete(root.right, key)
        else:
            if root.left is None:
                return root.right
            if root.right is None:
                return root.left

            successor = self._find_minimum(root.right)
            root.value = successor.value
            root.right = self._delete(root.right, successor.value.get_code())

        return root
                

    def height(self) -> int:
        if self.root is None:
            return -1
        return self._height(self.root)

    def _height(self, node: Optional[Node]) -> int:
        if node is None:
            return -1
        return 1 + max(self._height(node.left), self._height(node.right))

    def size(self) -> int:
        if self.root is None:
            return 0
        return self._size(self.root)

    def _size(self, node: Optional[Node]) -> int:
        if node is None:
            return 0
        return 1 + self._size(node.left) + self._size(node.right)

    def branch_traversal(self) -> None:
        if self.root is None:
            return
        self._branch_traversal(self.root, [])

    def _branch_traversal(self, node: Node, path: list) -> None:
        path.append(node.value)
        if node.is_leaf():
            print(" -> ".join(map(str, path)))
        else:
            if node.left is not None:
                self._branch_traversal(node.left, path.copy())
            if node.right is not None:
                self._branch_traversal(node.right, path.copy())

    def node_level(self, value: int) -> int:
        if self.root is None:
            return -1
        return self._node_level(self.root, value, 0)

    def _node_level(self, node: Optional[Node], value: int, current_level: int) -> int:
        if node is None:
            return -1
        if node.value == value:
            return current_level
        if value < node.value:
            return self._node_level(node.left, value, current_level + 1)
        else:
            return self._node_level(node.right, value, current_level + 1)

    def nodes_per_level(self) -> dict:
        """Return a dictionary mapping each level to its node count."""
        if self.root is None:
            return {}
        counts = {}
        self._nodes_per_level(self.root, 0, counts)
        return counts

    def _nodes_per_level(self, node: Optional[Node], level: int, counts: dict) -> None:
        if node is None:
            return
        counts[level] = counts.get(level, 0) + 1
        self._nodes_per_level(node.left, level + 1, counts)
        self._nodes_per_level(node.right, level + 1, counts)

