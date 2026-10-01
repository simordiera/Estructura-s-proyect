from dataclasses import dataclass
from typing import Optional
class Operation:
	def __init__(self,operation_type,description,before, after):
		self.operation_type = operation_type
		self.description = description
		self.before = before
		self.after = after
		pass
