
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from scr.models.Event import Event


@dataclass
class Report:
    """Datos completos de un reporte que todavía no ha sido procesado."""

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
        """Devuelve los datos en un formato sencillo para la tabla."""
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
        """Hace una validación básica de los datos del reporte."""
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
        """Convierte el reporte en el tipo de evento que usa el AVL."""
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
        """Compara datos físicos sin usar la estación como criterio."""
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
