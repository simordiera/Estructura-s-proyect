from collections import deque
from typing import Optional
from Node import Node


class AVL:

    def __init__(self):
        self.root = None


    def _get_height(self, node: Optional[Node]) -> int:
        if node is None:
            return 0
        return node.height

    def _update_height(self, node: Node) -> None:
        node.height = 1 + max(
            self._get_height(node.left),
            self._get_height(node.right)
        )


    def _balance_factor(self, node: Optional[Node]):
        if node is None:
            return 0

        return (
            self._get_height(node.left)
            - self._get_height(node.right) )

        

    def _rotate_right(self, y: Node) -> Node:

        x = y.left
        temporary = x.right

        x.right = y
        y.left = temporary

        self._update_height(y)
        self._update_height(x)

        return x

    def _rotate_left(self, x: Node) -> Node:

        y = x.right
        temporary = y.left

        y.left = x
        x.right = temporary

        self._update_height(x)
        self._update_height(y)

        return y


    def insert(self, value) -> None:
        self.historic (value, "insert")
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

        
    def balance (self) -> None:
        
        self.historic (None, "balance")
        self.root = self._balance(self.root)

    def _balance(self, node: Optional[Node]) -> Node:
        if node is None:
            return None

    
        node.left = self._balance(node.left)

        node.right = self._balance(node.right)

        
        self._update_height(node)
        balance = self._balance_factor(node)


        if balance > 1:

            if self._balance_factor(node.left) >= 0:
                return self._rotate_right(node)

            else:
                node.left = self._rotate_left(
                    node.left
                )

                return self._rotate_right(node)

        if balance < -1:

            if self._balance_factor(node.right) <= 0:
                return self._rotate_left(node)
            else:
                node.right = self._rotate_right(
                    node.right
                )

                return self._rotate_left(node)

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



    def post_order(self) -> None:

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

        return current


    def delete(self, id):

        earthquake=self.research(id)
        if (earthquake is None):
            return None
        else:
            self.root = self._delete(self.root, earthquake)
            self.historic(earthquake, "delete")
            return earthquake

    def _delete(self, root: Optional[Node], earthquake ) -> Optional[Node]:

        if root is None:
            return None
        
        value_key = earthquake.value.get_code()
        root_key = root.value.get_code()
        
        if value_key[0] != root_key[0]:
            if value_key[0] < root_key[0]:
                root.left = self._delete(root.left, earthquake)
            elif value_key[0] > root_key[0]:
                root.right = self._delete(root.right, earthquake)

        elif value_key[1] != root_key[1]:
            if value_key[1] < root_key[1]:
                root.left = self._delete(root.left,earthquake )
            elif value_key[1] > root_key[1]:
                root.right = self._delete(root.right, earthquake)

        elif value_key[2] != root_key[2]:
            if value_key[2] < root_key[2]:
                root.left = self._delete(root.left, earthquake)
            elif value_key[2] > root_key[2]:
                root.right = self._delete(root.right, earthquake)

        else:
            if root.is_leaf():
                return None
            if root.left is None:
                return root.right
            if root.right is None:
                return root.left
            successor = self._find_minimum(root.right)
            root.value = successor.value
            root.right = self._delete(root.right, successor)

        return root
        
    def height(self) -> int:

        if self.root is None:
            return -1

        return self._height(self.root)

    def _height(
        self,
        node: Optional[Node]
    ) -> int:

        if node is None:
            return -1

        return 1 + max(
            self._height(node.left),
            self._height(node.right)
        )


    def size(self) -> int:

        if self.root is None:
            return 0

        return self._size(self.root)

    def _size(
        self,
        node: Optional[Node]
    ) -> int:

        if node is None:
            return 0

        return (
            1
            + self._size(node.left)
            + self._size(node.right)
        )


    def node_level(
        self,
        value: int
    ) -> int:

        if self.root is None:
            return -1

        return self._node_level(
            self.root,
            value,
            0
        )

    def _node_level(
        self,
        node: Optional[Node],
        value: int,
        current_level: int
    ) -> int:

        if node is None:
            return -1

        if node.value == value:
            return current_level

        if value < node.value:

            return self._node_level(
                node.left,
                value,
                current_level + 1
            )

        else:

            return self._node_level(
                node.right,
                value,
                current_level + 1
            )


    def nodes_per_level(self) -> dict:

        if self.root is None:
            return {}

        counts = {}

        self._nodes_per_level(
            self.root,
            0,
            counts
        )

        return counts

    def _nodes_per_level(
        self,
        node: Optional[Node],
        level: int,
        counts: dict
    ) -> None:

        if node is None:
            return

        counts[level] = (
            counts.get(level, 0) + 1
        )

        self._nodes_per_level(
            node.left,
            level + 1,
            counts
        )

        self._nodes_per_level(
            node.right,
            level + 1,
            counts
        )

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

        self.historic (node, "research")

    def compare(self, id) -> None:

        list_similitude=[]
        value_key = self.research(id)

        if value_key is None:
            return list_similitude
        
        self._compare(self.root, value_key, list_similitude)
        self.historic ("compare")
        return list_similitude

    
    def _compare(self, node: Optional[Node], value_key, list_similitude) -> Node:

        if node is None:
            return None
        
        node_key_epicenter = node.value.get_epicenter()
        node_key_time = node.value.get_datetime()
        node_key_magnitude= node.value.get_magnitude()

        value_key_epicenter=value_key.value.get_epicenter()
        value_key_time = value_key.value.get_datetime()
        value_key_magnitude=value_key.value.get_magnitude()

        if (value_key_magnitude> node_key_magnitude):
            if ( 0< (((node_key_time)-(value_key_time)).total_seconds() / 3600) <= 48):
                if (( ((((value_key_epicenter[0])-(node_key_epicenter[0]))**2) + (((value_key_epicenter[1])-(node_key_epicenter[1]))**2))**(1/2)) <= 40):

                    list_similitude.append(node)

        self._compare(node.left, value_key, list_similitude)    
        self._compare(node.right, value_key, list_similitude)

        return list_similitude


    def historic (self, node: Optional[Node], text):
        list_historic= []
        if (text):
            self._historic(text, list_historic)
            return list_historic
        else:
            return list_historic

    def _historic(self, texto, list_historic):
        if (texto == "insert"):
            list_historic.append("se inserto un nodo")
        elif (texto == "delete"):
            list_historic.append("se elimino un nodo")
        elif (texto == "balance"):
            list_historic.append("se balanceo el arbol")
        elif (texto == "research"):
            list_historic.append("se busco un nodo")
        elif (texto == "compare"):
            list_historic.append("se comparo un nodo")

        return list_historic
        