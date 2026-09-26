from collections import deque
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Optional
from Node import Node
from Metrics import Metrics


class BST:
    # El BST comparte el estado del escenario, pero nunca aplica rotaciones.
    def __init__(self, simulation_clock=None, archive_age_hours=72):
        self.root = None
        self.list_historic = []
        self.retired_ids = set()
        self.simulation_clock = simulation_clock or datetime.now()
        self.archive_age_hours = archive_age_hours
        self.associations = {}
        self.metrics = Metrics()

    def insert(self, value: tuple):
        if self.root is None:
            self.root = Node(value)
        else:
            self._insert(self.root, value)

    def _insert(self, node: Node, value):
        if node is None:
            return Node(value)

        value_key = value.get_code()
        node_key = node.value.get_code()

        if value_key[0] != node_key[0]:
            if value_key[0] < node_key[0]:
                if node.left is None:
                    node.left = Node(value)
                else:
                    self._insert(node.left, value)
            elif value_key[0] > node_key[0]:
                if node.right is None:
                    node.right = Node(value)
                else:
                    self._insert(node.right, value)
        elif value_key[1] != node_key[1]:
            if value_key[1] < node_key[1]:
                if node.left is None:
                    node.left = Node(value)
                else:
                    self._insert(node.left, value)
            elif value_key[1] > node_key[1]:
                if node.right is None:
                    node.right = Node(value)
                else:
                    self._insert(node.right, value)
        else:
            if value_key[2] < node_key[2]:
                if node.left is None:
                    node.left = Node(value)
                else:
                    self._insert(node.left, value)
            elif value_key[2] > node_key[2]:
                if node.right is None:
                    node.right = Node(value)
                else:
                    self._insert(node.right, value)

    # Configuracion del reloj y del criterio de archivado.
    def set_simulation_clock(self, simulation_clock):
        self.simulation_clock = simulation_clock

    def set_archive_age_hours(self, archive_age_hours):
        if archive_age_hours <= 0:
            raise ValueError("T debe ser mayor que cero")
        self.archive_age_hours = archive_age_hours

    # Seleccion automatica de subarboles sin alterar la topologia del BST.
    def _subtree_nodes(self, node):
        if node is None:
            return []
        return [node] + self._subtree_nodes(node.left) + self._subtree_nodes(node.right)

    def _archive_candidate(self, node, depth):
        if node is None:
            return None
        nodes = self._subtree_nodes(node)
        limit = self.simulation_clock - timedelta(hours=self.archive_age_hours)
        eligible = all(
            event.get_priority() == 1 and event.get_datetime() < limit
            for event in (candidate.value for candidate in nodes)
        )
        candidates = []
        if eligible:
            candidates.append((len(nodes), depth, node.value.get_id(), nodes))
        left = self._archive_candidate(node.left, depth + 1)
        right = self._archive_candidate(node.right, depth + 1)
        if left is not None:
            candidates.append(left)
        if right is not None:
            candidates.append(right)
        return max(candidates, key=lambda item: (item[0], item[1], item[2])) if candidates else None

    def find_archive_candidate(self):
        candidate = self._archive_candidate(self.root, 0)
        if candidate is None:
            return None
        size, depth, root_id, nodes = candidate
        return {
            "root_id": root_id,
            "depth": depth,
            "size": size,
            "ids": {node.value.get_id() for node in nodes},
            "events": [node.value for node in nodes],
        }

    # Snapshot para que el archivado y la reactivacion sean acciones unicas.
    def _archive_snapshot(self):
        return {
            "root": deepcopy(self.root),
            "historic": deepcopy(self.list_historic),
            "retired_ids": deepcopy(self.retired_ids),
            "associations": deepcopy(self.associations),
            "metrics": self.metrics.snapshot(),
            "simulation_clock": self.simulation_clock,
            "archive_age_hours": self.archive_age_hours,
        }

    def _restore_archive_snapshot(self, snapshot):
        self.root = deepcopy(snapshot["root"])
        self.list_historic = deepcopy(snapshot["historic"])
        self.retired_ids = deepcopy(snapshot["retired_ids"])
        self.associations = deepcopy(snapshot["associations"])
        self.metrics.restore(snapshot["metrics"])
        self.simulation_clock = snapshot["simulation_clock"]
        self.archive_age_hours = snapshot["archive_age_hours"]

    def archive_subtree(self, undo_stack=None):
        candidate = self.find_archive_candidate()
        if candidate is None:
            return None

        # El conjunto se congela antes de que las eliminaciones cambien enlaces.
        frozen_ids = set(candidate["ids"])
        if candidate["root_id"] not in frozen_ids:
            raise RuntimeError("La raiz seleccionada debe pertenecer al subarbol archivado")
        snapshot = self._archive_snapshot()
        archived_events = list(candidate["events"])
        for event in archived_events:
            self.delete(event)
        self.list_historic.extend(archived_events)
        self.metrics.increment("mass_archives")
        self.metrics.increment("archived_events", len(archived_events))

        operation = {
            "type": "archivar_subarbol",
            "ids": frozen_ids,
            "root_id": candidate["root_id"],
            "snapshot": snapshot,
        }
        if undo_stack is not None:
            undo_stack.push_undo(operation)
        return operation

    def reactivate_historic(self, event_id, undo_stack=None):
        if self.research(event_id) is not None:
            return None
        historic_index = next(
            (index for index, event in enumerate(self.list_historic)
             if event.get_id() == event_id),
            None,
        )
        if historic_index is None:
            return None
        snapshot = self._archive_snapshot()
        event = self.list_historic.pop(historic_index)
        self.insert(event)
        self.metrics.increment("reactivated_events")
        operation = {
            "type": "reactivar_historico",
            "event_id": event_id,
            "snapshot": snapshot,
        }
        if undo_stack is not None:
            undo_stack.push_undo(operation)
        return operation

    def undo_last(self, undo_stack):
        operation = undo_stack.peek_undo()
        if not operation or "snapshot" not in operation:
            return False
        undo_stack.pop_undo()
        self._restore_archive_snapshot(operation["snapshot"])
        return True

    def delete_active(self, event_id, undo_stack=None):
        """Elimina un solo evento, sin enviarlo al historico ni balancear."""
        node = self.research(event_id)
        if node is None:
            return None
        snapshot = self._archive_snapshot()
        deleted_event = node.value
        self.delete(deleted_event)
        self.retired_ids.add(event_id)
        operation = {
            "type": "eliminar_evento",
            "event_id": event_id,
            "snapshot": snapshot,
        }
        if undo_stack is not None:
            undo_stack.push_undo(operation)
        return deleted_event

            

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

    def delete(self, value: tuple) -> None:
        self.root = self._delete(self.root, value)

    def _delete(self, root: Optional[Node], value) -> Optional[Node]:
        if root is None:
            return None

        value_key = value.get_code()
        root_key = root.value.get_code()

        if value_key < root_key:
            root.left = self._delete(root.left, value)
        elif value_key > root_key:
            root.right = self._delete(root.right, value)
        else:
            if root.left is None:
                return root.right
            if root.right is None:
                return root.left
            successor = self._find_minimum(root.right)
            root.value = successor.value
            root.right = self._delete(root.right, successor.value)
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

    def research(self, event_id):
        """Busca un evento por ID sin confundirlo con la clave completa."""
        return self._research(self.root, event_id)

    def _research(self, node, event_id):
        if node is None:
            return None
        if node.value.get_id() == event_id:
            return node
        found = self._research(node.left, event_id)
        return found if found is not None else self._research(node.right, event_id)

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

