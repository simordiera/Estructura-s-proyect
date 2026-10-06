class UndoStack:
	def __init__(self):
		# Keep independent undo and redo histories.
		self.undo_actions = []
		self.redo_actions = []

	def push(self, operation):
		# Push a new operation and clear stale redo actions.
		self.undo_actions.append(operation)
		self.redo_actions.clear()

	def undo(self):
		if len(self.undo_actions) == 0:
			return None

		operation = self.undo_actions.pop()
		self.redo_actions.append(operation)
		return operation

	def redo(self):
		if len(self.redo_actions) == 0:
			return None

		operation = self.redo_actions.pop()
		self.undo_actions.append(operation)
		return operation

	def is_undo_empty(self):
		return len(self.undo_actions) == 0

	def is_redo_empty(self):
		return len(self.redo_actions) == 0

	def peek_undo(self):
		if len(self.undo_actions) == 0:
			return None
		return self.undo_actions[-1]

	def peek_redo(self):
		if len(self.redo_actions) == 0:
			return None
		return self.redo_actions[-1]
