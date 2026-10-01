from datetime import datetime

from scr.models.AVL import AVL
from scr.models.Node import Node
from scr.models.Operation import Operation
from scr.models.ReportQueue import ReportQueue
from scr.models.SubtreeArchive import SubtreeArchiveManager
from scr.models.UndoStack import UndoStack


class Scenario:
	# Scenario es el coordinador del sistema. La interfaz llama a esta
	# clase y no modifica directamente el AVL ni la cola de reportes.
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

	def _copy_value(self, value, copied_objects):
		# Esta copia se escribe de forma explícita para no depender de
		# copy.deepcopy. El diccionario evita copiar dos veces el mismo objeto
		# y también protege contra referencias circulares.
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
		# Se guarda la raíz completa y no únicamente el recorrido inorden.
		# Así se conservan los hijos, las alturas y la topología exacta.
		copied_objects = {}
		state = {}
		state["root"] = self._copy_value(
			self.tree.root,
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
		state["stress_mode"] = self.tree.stress_mode
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
		# Cada llamada usa una tabla nueva para que el snapshot guardado
		# permanezca independiente del estado que se está restaurando.
		copied_objects = {}
		self.tree.root = self._copy_value(
			state["root"],
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
		self.tree.stress_mode = state["stress_mode"]
		self.stress_mode = state["stress_mode"]

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

	def _save_operation(self, operation_type, description, before):
		# Todas las modificaciones producidas por una acción se agrupan en
		# una sola Operation, aunque el AVL haga varios pasos internos.
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
		# UndoStack mueve la acción de la pila undo a la pila redo.
		operation = self.undo_stack.undo()
		if operation is None:
			return None
		self.restore_snapshot(operation.before)
		return operation

	def redo(self):
		# UndoStack mueve la acción de la pila redo a la pila undo.
		operation = self.undo_stack.redo()
		if operation is None:
			return None
		self.restore_snapshot(operation.after)
		return operation

	def create_event(self, event):
		# El identificador no se puede repetir ni reutilizar después de
		# una eliminación definitiva.
		if self.tree.research(event.get_id()) is not None:
			return None
		if event.get_id() in self.tree.retired_ids:
			return None

		before = self.snapshot()
		self.tree.insert(event)
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
		return self._save_operation(
			"marcar_revisado",
			"Se marcó un evento como revisado.",
			before,
		)

	def archive_subtree(self, archive_age_hours=None):
		# El administrador solo busca y separa la rama. Scenario conserva
		# el historial global y registra todo el archivo como una acción.
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
		self.tree.metrics.increment("mass_archives")
		self.tree.metrics.increment(
			"archived_events",
			len(events),
		)
		if not self.tree.stress_mode:
			self.tree.balance()

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
		operation = self._save_operation(
			"procesar_reporte",
			"Se procesó el primer reporte de la cola.",
			before,
		)
		operation.report = report
		return operation

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
		self.tree.stress_mode = stress_mode
		self.stress_mode = stress_mode
		return self._save_operation(
			"cambiar_modo",
			"Se cambió el modo de ejecución.",
			before,
		)

	def save_version(self, name):
		# Una versión contiene el estado operativo, pero no las pilas ni
		# las demás versiones guardadas.
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
