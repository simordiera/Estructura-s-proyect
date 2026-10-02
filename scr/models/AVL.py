from collections import deque
from copy import deepcopy
from datetime import datetime
from typing import Optional
from scr.models.Node import Node
from scr.models.Metrics import Metrics


class AVL:

    def __init__(self, simulation_clock=None, archive_age_hours=72, stress_mode=False):
        self.root = None
        self.list_deleted=[]
        self.list_historic = []
        self.retired_ids = set()
        self.associations = {}
        self.metrics = Metrics()
        self.simulation_clock = simulation_clock or datetime.now()
        self.archive_age_hours = archive_age_hours
        self.stress_mode = stress_mode

    def set_simulation_clock(self, simulation_clock):
        self.simulation_clock = simulation_clock

    def set_archive_age_hours(self, archive_age_hours):
        self.archive_age_hours = archive_age_hours

    def find_archive_candidate(self):
        return None


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
        for i in range (len(self.list_deleted)):
            if (self.list_deleted[i]== value.get_id()):
                return None
        self.root = self._insert(self.root, value)

    def _insert(self, node: Optional[Node], value) -> Node:

        if node is None:
            return Node(value)
        value_key = value.get_code()
        node_key = node.value.get_code()

        if (value_key[2] != node_key[2]):
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

            return node

        else:
            self.same_earthquake(value, node)

        return node
        
        
    def balance (self) -> None:
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
        earthquake = self.research(id)
        if earthquake is None or id in self.retired_ids:
            return None
        else:
            self.root = self._delete(self.root, earthquake, self.list_deleted, register_deleted=True)
            return earthquake

    def _delete(self, root: Optional[Node], earthquake, list_deleted, register_deleted: bool) -> Optional[Node]:

        if root is None:
            return None

        root_key = root.value.get_code()
        value_key = earthquake.value.get_code()
        
        if value_key[0] != root_key[0]:
            if value_key[0] < root_key[0]:
                root.left = self._delete(root.left, earthquake, list_deleted, register_deleted)
            elif value_key[0] > root_key[0]:
                root.right = self._delete(root.right, earthquake, list_deleted, register_deleted)

        elif value_key[1] != root_key[1]:
            if value_key[1] < root_key[1]:
                root.left = self._delete(root.left,earthquake, list_deleted, register_deleted)
            elif value_key[1] > root_key[1]:
                root.right = self._delete(root.right, earthquake, list_deleted, register_deleted)

        elif value_key[2] != root_key[2]:
            if value_key[2] < root_key[2]:
                root.left = self._delete(root.left, earthquake, list_deleted, register_deleted)
            elif value_key[2] > root_key[2]:
                root.right = self._delete(root.right, earthquake, list_deleted, register_deleted)

        else:
            if register_deleted:
                list_deleted.append(earthquake.value.get_id())
            if root.is_leaf():
                return None
            if root.left is None:
                return root.right
            if root.right is None:
                return root.left

            successor = self._find_minimum(root.right)
            root.value = successor.value
            root.right = self._delete(root.right, successor, list_deleted, False)

        self._update_height(root)
        if self.stress_mode:
            return root

        balance = self._balance_factor(root)
        if balance > 1:
            if self._balance_factor(root.left) < 0:
                root.left = self._rotate_left(root.left)
            return self._rotate_right(root)
        if balance < -1:
            if self._balance_factor(root.right) > 0:
                root.right = self._rotate_right(root.right)
            return self._rotate_left(root)
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

    def compare(self, id) -> None:
    
        list_similitude=[]
        value_key = self.research(id)

        if value_key is None:
            return list_similitude
        
        self._compare(self.root, value_key, list_similitude)
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

    def data_correction(self, id, new_info):
        earthquake=self.research(id)
        if earthquake is None:
            return None
        return self._data_correction(earthquake, new_info)
    
    def _data_correction (self, earthquake, new_info):
        event = earthquake.value
        old_key = event.get_code()

        if "magnitud" in new_info:
            event.set_magnitude(new_info["magnitud"])
            event.set_priority()

        elif "profundidad" in new_info:
            event.set_depth(new_info["profundidad"])
            event.set_priority()

        elif "epicentro" in new_info:
            event.set_epicenter(new_info["epicentro"][0], new_info["epicentro"][1])
            event.set_zone()
            event.set_priority()

        elif "fecha y hora" in new_info:
            event.set_datetime(new_info["fecha y hora"])

        elif "estacion" in new_info:
            event.set_stations(new_info["estacion"])

        new_key=event.get_code()

        if (old_key == new_key):
            return "Datos corregidos. El sismo esta en el mismo lugar."
        else:
            event.set_review(0)
            self.delete(event.get_id())
            if self.list_deleted:
                self.list_deleted.pop(-1)
            self.insert(event)
            return("datos corregidos. se reubico el sismo")



    def review(self, id):
        earthquake = self.research(id)
        if earthquake is None:
            return None

        earthquake.value.set_review(1)
        earthquake.value.set_revisions(earthquake.value.get_revisions() + 1)
        return True
        
    def same_earthquake(self, event, existing_node):
        return self._same_earthquake(event, existing_node)

    def _same_earthquake(self, event, existing_node):
        existing_event = existing_node.value
        new_event = event
        old_key = existing_event.get_code()
        
        if (new_event.get_id() == existing_event.get_id() and
            new_event.get_magnitude() == existing_event.get_magnitude() and
            new_event.get_depth() == existing_event.get_depth() and
            new_event.get_epicenter() == existing_event.get_epicenter() and
            new_event.get_datetime() == existing_event.get_datetime() and
            new_event.get_station() == existing_event.get_station()):

            existing_event.set_review(1)
            existing_event.set_revisions(existing_event.get_revisions() + 1)
            return True

        elif new_event.get_revisions() > existing_event.get_revisions():
            existing_event.set_magnitude(new_event.get_magnitude())
            existing_event.set_depth(new_event.get_depth())
            epicenter=new_event.get_epicenter()
            existing_event.set_epicenter(epicenter[0], epicenter[1])
            existing_event.set_zone()
            existing_event.datetime = new_event.get_datetime()
            existing_event.set_station(new_event.get_station())
            existing_event.set_priority()
            existing_event.set_review(0)
            existing_event.set_revisions(new_event.get_revisions())
            
            if (existing_event.get_code() == old_key):
                return True
            else:
                self.delete(existing_event.get_id())
                if self.list_deleted:
                    self.list_deleted.pop(-1)
                self.insert(existing_event)
                return True
        
        else:
            return False