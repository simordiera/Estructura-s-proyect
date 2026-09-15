def __init__ (self):
	self.pending_reports = []
	self.undo_actions = []

def add(self, item):
	self.pending_reports.append(item)

def is_empty(self):
	length = len(self.pending_reports)
	if length == 0:
		return True
	return False

def remove(self):
	if self.is_empty():
		return None
	return self.pending_reports.pop(0)

def peek(self):
	if self.is_empty():
		return None
	return self.pending_reports[0]


def push_undo(self, item):
	self.undo_actions.append(item)

def is_undo_empty(self):
	length = len(self.undo_actions)
	if length == 0:
		return True
	return False

def pop_undo(self):
	if self.is_undo_empty():
		return None
	return self.undo_actions.pop()

def peek_undo(self):
	if self.is_undo_empty():
		return None
	return self.undo_actions[-1]
