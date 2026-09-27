from collections import deque
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Optional
from Node import Node
from Metrics import Metrics


class AVL:

    # Estado del catalogo activo, historico y parametros del escenario.
    def __init__(self, simulation_clock=None, archive_age_hours=72, stress_mode=False):
        self.root = None
        self.list_historic = []
        self.retired_ids = set()
        self.simulation_clock = simulation_clock or datetime.now()
        self.archive_age_hours = archive_age_hours
        self.stress_mode = stress_mode
        self.associations = {}
        self.metrics = Metrics()


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
        self.root = self._insert(self.root, value)

    def _insert(self, node: Optional[Node], value) -> Node:

        if node is None:
            return Node(value)
        value_key = value.get_code()
        node_key = node.value.get_code()

        if value_key == node_key:
            return node

        # Insercion lexicografica por prioridad, magnitud e identificador.
        if value_key < node_key:
            node.left = self._insert(node.left, value)
        else:
            node.right = self._insert(node.right, value)

        self._update_height(node)
        if self.stress_mode:
            return node

        # Rotaciones AVL durante el retorno de la recursion.
        balance = self._balance_factor(node)
        if balance > 1:
            if value_key < node.left.value.get_code():
                return self._rotate_right(node)
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1:
            if value_key > node.right.value.get_code():
                return self._rotate_left(node)
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

        
    def balance (self) -> None:
        self.root = self._balance(self.root)

    # Configuracion del reloj y del modo de ejecucion.
    def set_simulation_clock(self, simulation_clock):
        self.simulation_clock = simulation_clock

    def set_archive_age_hours(self, archive_age_hours):
        if archive_age_hours <= 0:
            raise ValueError("T debe ser mayor que cero")
        self.archive_age_hours = archive_age_hours

    # Recorridos auxiliares para seleccionar y congelar un subarbol.
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

        left_candidate = self._archive_candidate(node.left, depth + 1)
        right_candidate = self._archive_candidate(node.right, depth + 1)
        if left_candidate is not None:
            candidates.append(left_candidate)
        if right_candidate is not None:
            candidates.append(right_candidate)
        return max(candidates, key=lambda item: (item[0], item[1], item[2])) if candidates else None

    def find_archive_candidate(self):
        """Devuelve la seleccion automatica sin modificar el AVL."""
        candidate = self._archive_candidate(self.root, 0)
        if candidate is None:
            return None
        size, depth, root_id, nodes = candidate
        return {
            "root_id": root_id,
            "depth": depth,
            "size": size,
            "ids": {node.value.get_id() for node in nodes},
            "root_event": nodes[0].value,
            "events": [node.value for node in nodes],
        }

    # Copia completa del estado para que archivar sea una sola accion de undo.
    def _archive_snapshot(self):
        return {
            "root": deepcopy(self.root),
            "historic": deepcopy(self.list_historic),
            "retired_ids": deepcopy(self.retired_ids),
            "associations": deepcopy(self.associations),
            "metrics": self.metrics.snapshot(),
            "simulation_clock": self.simulation_clock,
            "archive_age_hours": self.archive_age_hours,
            "stress_mode": self.stress_mode,
        }

    def _restore_archive_snapshot(self, snapshot):
        self.root = deepcopy(snapshot["root"])
        self.list_historic = deepcopy(snapshot["historic"])
        self.retired_ids = deepcopy(snapshot["retired_ids"])
        self.associations = deepcopy(snapshot["associations"])
        self.metrics.restore(snapshot["metrics"])
        self.simulation_clock = snapshot["simulation_clock"]
        self.archive_age_hours = snapshot["archive_age_hours"]
        self.stress_mode = snapshot["stress_mode"]

    def archive_subtree(self, undo_stack=None):
        """Traslada el subarbol elegible mas grande al historico."""
        candidate = self.find_archive_candidate()
        if candidate is None:
            return None

        # Este conjunto se congela antes de tocar el AVL.
        frozen_ids = set(candidate["ids"])
        root_id = candidate["root_id"]
        if root_id not in frozen_ids:
            raise RuntimeError("La raiz seleccionada debe pertenecer al subarbol archivado")
        snapshot = self._archive_snapshot()
        archived_events = list(candidate["events"])

        for event_id in frozen_ids:
            self.delete(event_id)
        if not self.stress_mode:
            self.balance()

        self.list_historic.extend(archived_events)
        self.metrics.increment("mass_archives")
        self.metrics.increment("archived_events", len(archived_events))

        operation = {
            "type": "archivar_subarbol",
            "ids": frozen_ids,
            "root_id": root_id,
            "snapshot": snapshot,
        }
        if undo_stack is not None:
            undo_stack.push_undo(operation)
        return operation

    def undo_archive(self, undo_stack):
        """Deshace la ultima accion de archivado como una unidad."""
        operation = undo_stack.peek_undo()
        if not operation or operation.get("type") != "archivar_subarbol":
            return False
        undo_stack.pop_undo()
        self._restore_archive_snapshot(operation["snapshot"])
        return True

    # Reactivacion de un evento historico mediante su identidad.
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
        if not self.stress_mode:
            self.balance()
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
        """Restaura la ultima operacion compatible registrada en la pila."""
        operation = undo_stack.peek_undo()
        if not operation or "snapshot" not in operation:
            return False
        undo_stack.pop_undo()
        self._restore_archive_snapshot(operation["snapshot"])
        return True

    def delete_active(self, event_id, undo_stack=None):
        """Elimina un solo evento, sin enviarlo al historico."""
        if self.research(event_id) is None:
            return None
        snapshot = self._archive_snapshot()
        deleted_event = self.delete(event_id)
        self.retired_ids.add(event_id)
        operation = {
            "type": "eliminar_evento",
            "event_id": event_id,
            "snapshot": snapshot,
        }
        if undo_stack is not None:
            undo_stack.push_undo(operation)
        return deleted_event

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
            if not self.stress_mode:
                self.balance()
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

        self._update_height(root)
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


    """
    def edit_event(self, id, info_new):
        earthquake=self.research(id)
        if earthquake is None:
            return None
        self._edit_event(self, earthquake, info_new)
    
    def _edit_event (self, earthquake, info_new):
        earthquakee=earthquake.value
        earthquake_old=earthquake.value


    #def historic ()
    """

    def review(self, id):
        if self.research(id):
            return 1
        else:
            return 0