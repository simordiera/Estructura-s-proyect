
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


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
