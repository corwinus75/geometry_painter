"""
storage.py – Zapis i odczyt stanu projektu przy użyciu biblioteki Pickle.
"""

import pickle
import os
from pathlib import Path
from shapes import Shape

#DEFAULT_PATH = Path.home() / "geometry_painter_save.gp"
DEFAULT_PATH = Path(__file__).parent / "geometry_painter_save.gp"


class Storage:
    """Obsługuje serializację/deserializację listy figur."""

    def __init__(self, path: Path | str | None = None):
        self.path: Path = Path(path) if path else DEFAULT_PATH

    def save(self, shapes: list[Shape]) -> tuple[bool, str]:
        """
        Zapisuje listę figur do pliku (Pickle).
        Zwraca (sukces, komunikat).
        """
        try:
            with open(self.path, "wb") as f:
                pickle.dump(shapes, f, protocol=pickle.HIGHEST_PROTOCOL)
            return True, f"Zapisano {len(shapes)} figur → {self.path}"
        except (OSError, pickle.PicklingError) as exc:
            return False, f"Błąd zapisu: {exc}"

    def load(self) -> tuple[list[Shape] | None, str]:
        """
        Wczytuje listę figur z pliku (Pickle).
        Zwraca (lista_figur | None, komunikat).
        """
        if not self.path.exists():
            return None, f"Plik nie istnieje: {self.path}"
        try:
            with open(self.path, "rb") as f:
                shapes = pickle.load(f)
            if not isinstance(shapes, list):
                return None, "Nieprawidłowy format pliku."
            return shapes, f"Wczytano {len(shapes)} figur z {self.path}"
        except (OSError, pickle.UnpicklingError, Exception) as exc:
            return None, f"Błąd odczytu: {exc}"

    def exists(self) -> bool:
        return self.path.exists()

    def delete(self) -> tuple[bool, str]:
        """Usuwa plik zapisu."""
        try:
            os.remove(self.path)
            return True, "Plik zapisu usunięty."
        except OSError as exc:
            return False, f"Błąd usuwania: {exc}"
