class UndoStack:
	# Pila LIFO de acciones completas, no de pasos internos del AVL.
	def __init__(self):
		self.undo_actions = []
		self.redo_actions = []

	def push(self, operation):
		self.undo_actions.append(operation)
		self.redo_actions.clear()

	def undo(self):
		if not self.undo_actions:
			return None

		operation = self.undo_actions.pop()
		self.redo_actions.append(operation)
		return operation

	def redo(self):
		if not self.redo_actions:
			return None

		operation = self.redo_actions.pop()
		self.undo_actions.append(operation)
		return operation

	def is_undo_empty(self):
		return not self.undo_actions

	def is_redo_empty(self):
		return not self.redo_actions

	def peek_undo(self):
		return self.undo_actions[-1] if self.undo_actions else None

	def peek_redo(self):
		return self.redo_actions[-1] if self.redo_actions else None
