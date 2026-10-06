
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from scr.models.Event import Event


@dataclass
class Report:
    """Complete data for a report that has not been processed."""

    identifier: int
    magnitude: float
    depth: float
    epicenter: tuple
    occurrence_datetime: str
    revision: int
    station: str
    status: str = "Pendiente"
    decision: str = "Pendiente"
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Return report data in a table-friendly format."""
        return {
            "Identificador": f"SIS-{self.identifier:06d}",
            "Magnitud": self.magnitude,
            "Profundidad (km)": self.depth,
            "Epicentro X": self.epicenter[0],
            "Epicentro Y": self.epicenter[1],
            "Fecha y hora UTC": self.occurrence_datetime,
            "Revisión": self.revision,
            "Estación": self.station,
            "Estado": self.status,
            "Decisión": self.decision,
            "Mensaje": self.message,
        }

    def is_valid(self) -> bool:
        """Perform basic report-data validation."""
        try:
            datetime.fromisoformat(self.occurrence_datetime)
        except ValueError:
            return False

        return (
            1 <= self.identifier <= 999999
            and -2.0 <= self.magnitude <= 10.0
            and 0.0 <= self.depth <= 700.0
            and 0.0 <= self.epicenter[0] <= 1000.0
            and 0.0 <= self.epicenter[1] <= 1000.0
            and self.revision >= 1
            and bool(self.station.strip())
        )

    def to_event(self) -> Event:
        """Convert the report into the event type used by the AVL."""
        return Event(
            self.identifier,
            self.magnitude,
            self.depth,
            self.epicenter,
            self.occurrence_datetime,
            self.station,
            self.revision,
        )

    def has_same_event_data(self, event: Event) -> bool:
        """Compare physical data without using the station as a criterion."""
        return (
            self.magnitude == event.get_magnitude()
            and self.depth == event.get_depth()
            and self.epicenter == event.get_epicenter()
            and self.occurrence_datetime == event.get_datetime().strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
        )

    def finish(self, decision: str, message: str) -> None:
        self.status = "Procesado"
        self.decision = decision
        self.message = message
