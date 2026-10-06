class Metrics:
	# Scenario counters that can be restored.
	def __init__(self):
		self.counters = {
			"mass_archives": 0,
			"archived_events": 0,
			"reactivated_events": 0,
		}

	def increment(self, name, amount=1):
		self.counters[name] = self.counters.get(name, 0) + amount

	def get(self, name):
		return self.counters.get(name, 0)

	def snapshot(self):
		return dict(self.counters)

	def restore(self, snapshot):
		self.counters = dict(snapshot)
