from copy import deepcopy
from datetime import timedelta


class SubtreeArchiveManager:
    def __init__(self, tree):
        # Operate on the active AVL owned by Scenario.
        self.tree = tree

    def _is_old_enough(self, event, archive_age_hours):
        age = self.tree.simulation_clock - event.get_datetime()
        return age > timedelta(hours=archive_age_hours)

    def _eligible_subtree(self, node, archive_age_hours):
        if node is None:
            return True

        event = node.value
        if event.get_priority() != 1:
            return False
        if not self._is_old_enough(event, archive_age_hours):
            return False
        return (
            self._eligible_subtree(node.left, archive_age_hours)
            and self._eligible_subtree(node.right, archive_age_hours)
        )

    def _collect_events(self, node):
        if node is None:
            return []
        return (
            self._collect_events(node.left)
            + [node.value]
            + self._collect_events(node.right)
        )

    def _candidate_rows(self, node, depth, archive_age_hours, rows):
        if node is None:
            return

        if self._eligible_subtree(node, archive_age_hours):
            events = self._collect_events(node)
            rows.append(
                {
                    "root_id": node.value.get_id(),
                    "size": len(events),
                    "depth": depth,
                    "ids": [event.get_id() for event in events],
                    "events": events,
                }
            )

        self._candidate_rows(node.left, depth + 1, archive_age_hours, rows)
        self._candidate_rows(node.right, depth + 1, archive_age_hours, rows)

    def find_candidate(self, archive_age_hours=None):
        threshold = (
            self.tree.archive_age_hours
            if archive_age_hours is None
            else archive_age_hours
        )
        if threshold <= 0:
            raise ValueError("La antigüedad mínima debe ser positiva.")

        candidates = []
        self._candidate_rows(self.tree.root, 0, threshold, candidates)
        if not candidates:
            return None

        return max(
            candidates,
            key=lambda candidate: (
                candidate["size"],
                candidate["depth"],
                candidate["root_id"],
            ),
        )

    def _find_node_by_id(self, node, event_id):
        if node is None:
            return None
        if node.value.get_id() == event_id:
            return node
        return (
            self._find_node_by_id(node.left, event_id)
            or self._find_node_by_id(node.right, event_id)
        )

    def _detach(self, node, target):
        if node is None:
            return None, None
        if node is target:
            return None, node

        node.left, detached = self._detach(node.left, target)
        if detached is not None:
            return node, detached

        node.right, detached = self._detach(node.right, target)
        return node, detached

    def _snapshot(self):
        return {
            "root": deepcopy(self.tree.root),
            "list_historic": deepcopy(self.tree.list_historic),
            "retired_ids": set(self.tree.retired_ids),
            "associations": deepcopy(self.tree.associations),
            "metrics": self.tree.metrics.snapshot(),
            "list_deleted": list(self.tree.list_deleted),
        }

    def _restore(self, snapshot):
        self.tree.root = snapshot["root"]
        self.tree.list_historic = snapshot["list_historic"]
        self.tree.retired_ids = set(snapshot["retired_ids"])
        self.tree.associations = snapshot["associations"]
        self.tree.metrics.restore(snapshot["metrics"])
        self.tree.list_deleted = list(snapshot["list_deleted"])

    def archive_subtree(self, undo_stack, archive_age_hours=None):
        # Detach one eligible subtree and preserve its operation snapshot.
        candidate = self.find_candidate(archive_age_hours)
        if candidate is None:
            return None

        target = self._find_node_by_id(self.tree.root, candidate["root_id"])
        if target is None:
            return None

        snapshot = self._snapshot()
        self.tree.root, detached = self._detach(self.tree.root, target)
        if detached is None:
            return None

        events = self._collect_events(detached)
        self.tree.list_historic.extend(events)
        self.tree.metrics.increment("mass_archives")
        self.tree.metrics.increment("archived_events", len(events))
        if not self.tree.stress:
            self.tree.balance()

        operation = {
            "type": "archivar_subarbol",
            "root_id": candidate["root_id"],
            "ids": [event.get_id() for event in events],
            "size": len(events),
            "depth": candidate["depth"],
            "snapshot": snapshot,
        }
        undo_stack.push_undo(operation)
        return operation

    def undo_last(self, undo_stack):
        operation = undo_stack.peek_undo()
        if not operation or operation.get("type") != "archivar_subarbol":
            return False

        self._restore(operation["snapshot"])
        undo_stack.pop_undo()
        return True
