from dataclasses import dataclass
from typing import Optional
from typing import Any

class Operation:
	def __init__(self,operation_type,description,before, after):
		# Store both states so the action can be undone and redone.
		self.operation_type = operation_type
		self.description = description
		self.before = before
		self.after = after
		pass
