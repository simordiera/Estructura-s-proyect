class UndoStack:
	# Pila LIFO de acciones completas, no de pasos internos del AVL.
	def __init__(self):
		self.actions = []

	def push_undo(self, action):
		self.actions.append(action)

	def pop_undo(self):
		return self.actions.pop() if self.actions else None

	def peek_undo(self):
		return self.actions[-1] if self.actions else None

	def is_undo_empty(self):
		return not self.actions
