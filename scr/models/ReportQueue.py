from collections import deque


class ReportQueue:
	def __init__(self):
		# FIFO queue preserves report arrival order.
		self.pending_reports = deque()

	def add(self, item):
		self.pending_reports.append(item)

	def remove(self):
		if self.is_empty():
			return None
		return self.pending_reports.popleft()

	def peek(self):
		if self.is_empty():
			return None
		return self.pending_reports[0]

	def append_front(self, item):
		self.pending_reports.appendleft(item)

	def is_empty(self):
		return len(self.pending_reports) == 0

	def get_all(self):
		return list(self.pending_reports)
