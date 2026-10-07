from datetime import datetime

from scr.models.AVL import AVL
from scr.models.BST import BST
from scr.models.Node import Node
from scr.models.Operation import Operation
from scr.models.ReportQueue import ReportQueue
from scr.models.SubtreeArchive import SubtreeArchiveManager
from scr.models.UndoStack import UndoStack


class Scenario:
	# Scenario coordinates the system; the interface calls it instead of
	# modifying the AVL or report queue directly.
	def __init__(
		self,
		simulation_clock=None,
		archive_age_hours=72,
		stress_mode=False,
	):
		self.tree = AVL(
			simulation_clock=simulation_clock,
			archive_age_hours=archive_age_hours,
			stress_mode=stress_mode,
		)
		self.bst = BST()
		self.report_queue = ReportQueue()
		self.undo_stack = UndoStack()
		self.archive_manager = SubtreeArchiveManager(self.tree)

		self.stations = []
		self.zones = []
		self.parameters = {
			"W": None,
			"R": None,
			"L": None,
			"T": archive_age_hours,
		}
		self.stress_mode = stress_mode
		self.versions = {}
		self._bst_insertion_order = []

	def attach_trees(self, avl, bst=None):
		"""Attach the trees already owned by the application session."""
		self.tree = avl
		self.archive_manager.tree = avl
		if bst is not None:
			self.bst = bst
		self.sync_comparison_tree()

	def sync_comparison_tree(self):
		"""Make the comparison BST contain exactly the active AVL events."""
		active_events = {
			event.get_id(): event
			for event in (self.tree.in_order() or [])
		}
		known_ids = [
			event_id
			for event_id in self._bst_insertion_order
			if event_id in active_events
		]
		known_set = set(known_ids)
		known_ids.extend(
			event_id
			for event_id in active_events
			if event_id not in known_set
		)
		self._bst_insertion_order = list(dict.fromkeys(known_ids))

		new_bst = BST()
		for event_id in self._bst_insertion_order:
			new_bst.insert(active_events[event_id])
		new_bst.list_historic = self.tree.list_historic
		new_bst.list_deleted = list(self.tree.list_deleted)
		new_bst.retired_ids = set(self.tree.retired_ids)
		new_bst.associations = self.tree.associations
		new_bst.metrics.restore(self.tree.metrics.snapshot())
		new_bst.simulation_clock = self.tree.simulation_clock
		new_bst.archive_age_hours = self.tree.archive_age_hours
		self.bst = new_bst

	def _copy_value(self, value, copied_objects):
		# Copy values explicitly to preserve shared references and cycles.
		value_id = id(value)
		if value_id in copied_objects:
			return copied_objects[value_id]

		if value is None:
			return None
		if isinstance(value, (bool, int, float, str, bytes)):
			return value
		if isinstance(value, datetime):
			return datetime.fromtimestamp(
				value.timestamp(),
				tz=value.tzinfo,
			)

		if isinstance(value, list):
			new_list = []
			copied_objects[value_id] = new_list
			for item in value:
				new_list.append(self._copy_value(item, copied_objects))
			return new_list

		if isinstance(value, tuple):
			new_tuple_items = []
			for item in value:
				new_tuple_items.append(
					self._copy_value(item, copied_objects)
				)
			new_tuple = tuple(new_tuple_items)
			copied_objects[value_id] = new_tuple
			return new_tuple

		if isinstance(value, set):
			new_set = set()
			copied_objects[value_id] = new_set
			for item in value:
				new_set.add(self._copy_value(item, copied_objects))
			return new_set

		if isinstance(value, dict):
			new_dict = {}
			copied_objects[value_id] = new_dict
			for key, item in value.items():
				new_key = self._copy_value(key, copied_objects)
				new_item = self._copy_value(item, copied_objects)
				new_dict[new_key] = new_item
			return new_dict

		if isinstance(value, Node):
			new_node = Node(None)
			copied_objects[value_id] = new_node
			new_node.value = self._copy_value(
				value.value,
				copied_objects,
			)
			new_node.left = self._copy_value(
				value.left,
				copied_objects,
			)
			new_node.right = self._copy_value(
				value.right,
				copied_objects,
			)
			new_node.height = value.height
			return new_node

		if hasattr(value, "__dict__"):
			new_object = value.__class__.__new__(value.__class__)
			copied_objects[value_id] = new_object
			for name, item in value.__dict__.items():
				setattr(
					new_object,
					name,
					self._copy_value(item, copied_objects),
				)
			return new_object

		return value

	def snapshot(self):
		# Store complete roots to preserve links, heights, and topology.
		copied_objects = {}
		state = {}
		state["root"] = self._copy_value(
			self.tree.root,
			copied_objects,
		)
		state["bst_root"] = self._copy_value(
			self.bst.root,
			copied_objects,
		)
		state["bst_insertion_order"] = self._copy_value(
			self._bst_insertion_order,
			copied_objects,
		)
		state["list_historic"] = self._copy_value(
			self.tree.list_historic,
			copied_objects,
		)
		state["list_deleted"] = self._copy_value(
			self.tree.list_deleted,
			copied_objects,
		)
		state["retired_ids"] = self._copy_value(
			self.tree.retired_ids,
			copied_objects,
		)
		state["associations"] = self._copy_value(
			self.tree.associations,
			copied_objects,
		)
		state["metrics"] = self._copy_value(
			self.tree.metrics.snapshot(),
			copied_objects,
		)
		state["simulation_clock"] = self._copy_value(
			self.tree.simulation_clock,
			copied_objects,
		)
		state["archive_age_hours"] = self.tree.archive_age_hours
		state["stress_mode"] = self.tree.stress
		state["reports"] = self._copy_value(
			self.report_queue.get_all(),
			copied_objects,
		)
		state["stations"] = self._copy_value(
			self.stations,
			copied_objects,
		)
		state["zones"] = self._copy_value(
			self.zones,
			copied_objects,
		)
		state["parameters"] = self._copy_value(
			self.parameters,
			copied_objects,
		)
		return state

	def restore_snapshot(self, state):
		# Use a new copy map so stored snapshots remain independent.
		copied_objects = {}
		self.tree.root = self._copy_value(
			state["root"],
			copied_objects,
		)
		self.bst.root = self._copy_value(
			state.get("bst_root"),
			copied_objects,
		)
		self._bst_insertion_order = self._copy_value(
			state.get("bst_insertion_order", []),
			copied_objects,
		)
		self.tree.list_historic = self._copy_value(
			state["list_historic"],
			copied_objects,
		)
		self.tree.list_deleted = self._copy_value(
			state["list_deleted"],
			copied_objects,
		)
		self.tree.retired_ids = self._copy_value(
			state["retired_ids"],
			copied_objects,
		)
		self.tree.associations = self._copy_value(
			state["associations"],
			copied_objects,
		)
		self.tree.metrics.restore(
			self._copy_value(
				state["metrics"],
				copied_objects,
			)
		)
		self.tree.simulation_clock = self._copy_value(
			state["simulation_clock"],
			copied_objects,
		)
		self.tree.archive_age_hours = state["archive_age_hours"]
		stress_mode = state.get("stress_mode", self.tree.stress)
		if not isinstance(stress_mode, bool):
			stress_mode = self.tree.stress
		self.tree.stress = stress_mode
		self.stress_mode = stress_mode

		self.report_queue = ReportQueue()
		for report in state["reports"]:
			self.report_queue.add(
				self._copy_value(report, copied_objects)
			)

		self.stations = self._copy_value(
			state["stations"],
			copied_objects,
		)
		self.zones = self._copy_value(
			state["zones"],
			copied_objects,
		)
		self.parameters = self._copy_value(
			state["parameters"],
			copied_objects,
		)
		if "T" in self.parameters:
			self.tree.archive_age_hours = self.parameters["T"]
		if "bst_root" not in state:
			self.sync_comparison_tree()
		else:
			self.bst.list_historic = self.tree.list_historic
			self.bst.list_deleted = list(self.tree.list_deleted)
			self.bst.retired_ids = set(self.tree.retired_ids)
			self.bst.associations = self.tree.associations
			self.bst.metrics.restore(self.tree.metrics.snapshot())
			self.bst.simulation_clock = self.tree.simulation_clock
			self.bst.archive_age_hours = self.tree.archive_age_hours

	def _save_operation(self, operation_type, description, before):
		# Group all internal changes from one action into one Operation.
		after = self.snapshot()
		operation = Operation(
			operation_type,
			description,
			before,
			after,
		)
		self.undo_stack.push(operation)
		return operation

	def undo(self):
		# UndoStack moves the action from undo to redo.
		operation = self.undo_stack.undo()
		if operation is None:
			return None
		self.restore_snapshot(operation.before)
		return operation

	def redo(self):
		# UndoStack moves the action from redo to undo.
		operation = self.undo_stack.redo()
		if operation is None:
			return None
		self.restore_snapshot(operation.after)
		return operation

	def create_event(self, event):
		# IDs cannot be duplicated or reused after permanent deletion.
		if self.tree.research(event.get_id()) is not None:
			return None
		if event.get_id() in self.tree.retired_ids:
			return None

		before = self.snapshot()
		self.tree.insert(event)
		if event.get_id() not in self._bst_insertion_order:
			self._bst_insertion_order.append(event.get_id())
		self.sync_comparison_tree()
		return self._save_operation(
			"crear_evento",
			"Se creó un evento.",
			before,
		)

	def correct_event(self, event_id, new_info):
		if self.tree.research(event_id) is None:
			return None

		before = self.snapshot()
		result = self.tree.data_correction(event_id, new_info)
		if result is None:
			return None
		self.sync_comparison_tree()
		return self._save_operation(
			"corregir_evento",
			"Se corrigieron los datos de un evento.",
			before,
		)

	def delete_event(self, event_id):
		if self.tree.research(event_id) is None:
			return None

		before = self.snapshot()
		event = self.tree.delete(event_id)
		if event is None:
			return None
		if event_id in self._bst_insertion_order:
			self._bst_insertion_order.remove(event_id)
		self.sync_comparison_tree()
		return self._save_operation(
			"eliminar_evento",
			"Se eliminó un evento.",
			before,
		)

	def mark_reviewed(self, event_id):
		if self.tree.research(event_id) is None:
			return None

		before = self.snapshot()
		if not self.tree.review(event_id):
			return None
		self.sync_comparison_tree()
		return self._save_operation(
			"marcar_revisado",
			"Se marcó un evento como revisado.",
			before,
		)

	def archive_subtree(self, archive_age_hours=None):
		# The manager detaches the branch; Scenario stores history and action state.
		candidate = self.archive_manager.find_candidate(
			archive_age_hours
		)
		if candidate is None:
			return None

		target = self.archive_manager._find_node_by_id(
			self.tree.root,
			candidate["root_id"],
		)
		if target is None:
			return None

		before = self.snapshot()
		self.tree.root, detached = self.archive_manager._detach(
			self.tree.root,
			target,
		)
		if detached is None:
			return None

		events = self.archive_manager._collect_events(detached)
		for event in events:
			self.tree.list_historic.append(event)
			if event.get_id() in self._bst_insertion_order:
				self._bst_insertion_order.remove(event.get_id())
		self.tree.metrics.increment("mass_archives")
		self.tree.metrics.increment(
			"archived_events",
			len(events),
		)
		if not self.tree.stress:
			self.tree.balance()
		self.sync_comparison_tree()

		operation = self._save_operation(
			"archivar_subarbol",
			"Se archivó un subárbol.",
			before,
		)
		operation.root_id = candidate["root_id"]
		operation.event_ids = [
			event.get_id()
			for event in events
		]
		return operation

	def _reactivate_archived_event(self, historic_event, active_event=None):
		"""Move one archived event back into the active AVL and comparison BST."""
		if historic_event not in self.tree.list_historic:
			return None

		event_id = historic_event.get_id()
		event_to_insert = (
			historic_event
			if active_event is None
			else active_event
		)
		if event_to_insert.get_id() != event_id:
			return None
		if self.tree.research(event_id) is not None:
			return None
		if (
			event_id in self.tree.list_deleted
			or event_id in self.tree.retired_ids
		):
			return None

		historic_index = self.tree.list_historic.index(historic_event)
		self.tree.list_historic.pop(historic_index)
		self.tree.insert(event_to_insert)
		if self.tree.research(event_id) is None:
			self.tree.list_historic.insert(historic_index, historic_event)
			return None

		if event_id not in self._bst_insertion_order:
			self._bst_insertion_order.append(event_id)
		self.tree.metrics.increment("reactivated_events")
		self.sync_comparison_tree()
		return event_to_insert

	def reactivate_event(self, event_id):
		"""Reactivate one archived event as a single undoable scenario action."""
		historic_event = next(
			(
				event
				for event in self.tree.list_historic
				if event.get_id() == event_id
			),
			None,
		)
		if historic_event is None:
			return None

		before = self.snapshot()
		reactivated_event = self._reactivate_archived_event(historic_event)
		if reactivated_event is None:
			return None

		operation = self._save_operation(
			"reactivar_evento",
			"Se reactivó un evento archivado.",
			before,
		)
		operation.event_id = event_id
		return operation

	def add_report(self, report):
		before = self.snapshot()
		self.report_queue.add(report)
		return self._save_operation(
			"agregar_reporte",
			"Se agregó un reporte a la cola.",
			before,
		)

	def process_next_report(self):
		if self.report_queue.is_empty():
			return None

		before = self.snapshot()
		report = self.report_queue.remove()
		result = self._process_report_against_tree(report)
		if hasattr(report, "finish"):
			report.finish(result["decision"], result["message"])
		operation = self._save_operation(
			"procesar_reporte",
			result["message"],
			before,
		)
		operation.report = report
		operation.result = result
		return operation

	def _process_report_against_tree(self, report):
		"""Classify and apply a report using the current AVL."""
		event_id = report.identifier
		active_node = self.tree.research(event_id)
		historic_event = next(
			(
				event
				for event in self.tree.list_historic
				if event.get_id() == event_id
			),
			None,
		)

		if event_id in self.tree.list_deleted:
			return {
				"decision": "rechazado",
				"message": (
					f"El reporte SIS-{event_id:06d} fue rechazado porque "
					"el identificador está retirado."
				),
				"changed": False,
			}

		if active_node is not None:
			existing_event = active_node.value
			current_revision = existing_event.get_revisions()

			if report.revision < current_revision:
				return {
					"decision": "antiguo",
					"message": (
						f"El reporte SIS-{event_id:06d} es antiguo. "
						f"La revisión vigente es {current_revision}."
					),
					"changed": False,
				}

			if report.revision == current_revision:
				if report.has_same_event_data(existing_event):
					self._add_station_to_event(
						existing_event,
						report.station,
					)
					existing_event.set_review(1)
					return {
						"decision": "confirmado",
						"message": (
							f"El reporte SIS-{event_id:06d} confirmó el evento "
							f"activo con la revisión {current_revision}."
						),
						"changed": True,
					}
				return {
					"decision": "conflicto",
					"message": (
						f"El reporte SIS-{event_id:06d} tiene la misma revisión "
						"pero datos diferentes."
					),
					"changed": False,
				}

			self._apply_report_to_active_event(existing_event, report)
			return {
				"decision": "correccion",
				"message": (
					f"Se aceptó la corrección del reporte SIS-{event_id:06d} "
					f"con revisión {report.revision}."
				),
				"changed": True,
			}

		if historic_event is not None:
			current_revision = historic_event.get_revisions()
			if report.revision < current_revision:
				return {
					"decision": "antiguo",
					"message": (
						f"El reporte archivado SIS-{event_id:06d} es antiguo."
					),
					"changed": False,
				}
			if report.revision == current_revision:
				if not report.has_same_event_data(historic_event):
					return {
						"decision": "conflicto",
						"message": (
							f"El reporte archivado SIS-{event_id:06d} tiene "
							"datos diferentes en la misma revisión."
						),
						"changed": False,
					}
				return {
					"decision": "confirmado",
					"message": (
						f"El reporte SIS-{event_id:06d} confirmó un evento "
						"archivado sin reactivarlo."
					),
					"changed": False,
				}

			reactivated_event = report.to_event()
			reactivated_event.set_review(0)
			if self._reactivate_archived_event(
				historic_event,
				reactivated_event,
			) is None:
				return {
					"decision": "rechazado",
					"message": (
						f"No se pudo reactivar el evento archivado "
						f"SIS-{event_id:06d}."
					),
					"changed": False,
				}
			return {
				"decision": "reactivado",
				"message": (
					f"El evento archivado SIS-{event_id:06d} fue reactivado "
					f"con la revisión {report.revision}."
				),
				"changed": True,
			}

		self.tree.insert(report.to_event())
		if event_id not in self._bst_insertion_order:
			self._bst_insertion_order.append(event_id)
		self.sync_comparison_tree()
		return {
			"decision": "nuevo",
			"message": (
				f"Se creó el evento SIS-{event_id:06d} en el AVL "
				f"con la revisión {report.revision}."
			),
			"changed": True,
		}

	def _apply_report_to_active_event(self, event, report):
		"""Update an existing event without creating a duplicate node."""
		old_key = event.get_code()
		new_event = report.to_event()
		new_key = new_event.get_code()

		if old_key != new_key:
			self.tree.delete(event.get_id())
			if event.get_id() in self.tree.list_deleted:
				self.tree.list_deleted.remove(event.get_id())

		event.set_magnitude(new_event.get_magnitude())
		event.set_depth(new_event.get_depth())
		epicenter = new_event.get_epicenter()
		event.set_epicenter(epicenter[0], epicenter[1])
		event.set_zone()
		event.set_priority()
		event.datetime = new_event.get_datetime()
		event.set_revisions(new_event.get_revisions())
		event.set_review(0)
		event.set_station(new_event.get_station())

		if old_key != new_key:
			self.tree.insert(event)
		self.sync_comparison_tree()

	def _add_station_to_event(self, event, station):
		"""Preserve accepted stations without requiring a specific container type."""
		current_station = event.get_station()
		if isinstance(current_station, set):
			current_station.add(station)
		elif current_station == station:
			return
		elif current_station:
			event.set_station({current_station, station})
		else:
			event.set_station(station)

	def advance_clock(self, simulation_clock):
		before = self.snapshot()
		self.tree.set_simulation_clock(simulation_clock)
		return self._save_operation(
			"avanzar_reloj",
			"Se actualizó el reloj de simulación.",
			before,
		)

	def change_parameters(self, parameters):
		before = self.snapshot()
		for name, value in parameters.items():
			if name in self.parameters:
				self.parameters[name] = value

		if "T" in parameters:
			self.tree.set_archive_age_hours(parameters["T"])
		return self._save_operation(
			"cambiar_parametros",
			"Se cambiaron los parámetros del escenario.",
			before,
		)

	def set_stress_mode(self, stress_mode):
		before = self.snapshot()
		self.tree.stress = stress_mode
		if not stress_mode:
			self.tree.balance()
		self.stress_mode = stress_mode
		return self._save_operation(
			"cambiar_modo",
			"Se cambió el modo de ejecución.",
			before,
		)

	def save_version(self, name):
		# A version stores operational state, not stacks or other versions.
		self.versions[name] = self.snapshot()
		return self.versions[name]

	def restore_version(self, name):
		if name not in self.versions:
			return None

		before = self.snapshot()
		self.restore_snapshot(self.versions[name])
		return self._save_operation(
			"restaurar_version",
			"Se restauró una versión guardada.",
			before,
		)
