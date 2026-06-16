"""
canvas.py – Kolekcja figur i operacje na niej.
Moduł odpowiada za przechowywanie wszystkich figur, ich zaznaczanie,
przesuwanie i usuwanie.
"""

import pygame
from shapes import Shape

# Kolor tła płótna
CANVAS_BG = (28, 32, 40)
GRID_COLOR = (38, 43, 54)


class Canvas:
    """Kolekcja figur z obsługą zaznaczania, przesuwania i usuwania."""

    def __init__(self, rect: pygame.Rect):
        self.rect: pygame.Rect = rect       # obszar rysowania
        self.shapes: list[Shape] = []       # kolekcja figur
        self.selected: Shape | None = None  # aktualnie zaznaczona figura
        self._drag_offset: tuple[int, int] = (0, 0)
        self._dragging: bool = False
        self.show_grid: bool = True

    # ── Dodawanie / usuwanie ──────────────────────────────────────────────────
    def add_shape(self, shape: Shape) -> None:
        """Dodaje figurę do kolekcji."""
        self.shapes.append(shape)
        self._select(shape)

    def remove_selected(self) -> str | None:
        """Usuwa zaznaczoną figurę. Zwraca info o usuniętej figurze."""
        if self.selected:
            info = self.selected.info()
            self.shapes.remove(self.selected)
            self.selected = None
            return info
        return None

    def clear_all(self) -> None:
        """Usuwa wszystkie figury."""
        self.shapes.clear()
        self.selected = None

    # ── Zaznaczanie ───────────────────────────────────────────────────────────
    def _select(self, shape: Shape | None) -> None:
        if self.selected:
            self.selected.selected = False
        self.selected = shape
        if shape:
            shape.selected = True

    def try_select(self, px: int, py: int) -> bool:
        """Zaznacza figurę pod kursorem (od wierzchu stosu). Zwraca True jeśli coś zaznaczono."""
        for shape in reversed(self.shapes):
            if shape.contains_point(px, py):
                self._select(shape)
                return True
        self._select(None)
        return False

    def deselect(self) -> None:
        self._select(None)

    # ── Drag & drop ───────────────────────────────────────────────────────────
    def start_drag(self, px: int, py: int) -> bool:
        """Inicjuje przesuwanie zaznaczonej figury."""
        if self.selected and self.selected.contains_point(px, py):
            self._drag_offset = (px - self.selected.x, py - self.selected.y)
            self._dragging = True
            return True
        return False

    def update_drag(self, px: int, py: int) -> None:
        if self._dragging and self.selected:
            self.selected.x = px - self._drag_offset[0]
            self.selected.y = py - self._drag_offset[1]

    def end_drag(self) -> None:
        self._dragging = False

    @property
    def is_dragging(self) -> bool:
        return self._dragging

    # ── Porządek rysowania ────────────────────────────────────────────────────
    def bring_to_front(self) -> None:
        """Przenosi zaznaczoną figurę na wierzch stosu."""
        if self.selected and self.selected in self.shapes:
            self.shapes.remove(self.selected)
            self.shapes.append(self.selected)

    def send_to_back(self) -> None:
        """Przenosi zaznaczoną figurę na dół stosu."""
        if self.selected and self.selected in self.shapes:
            self.shapes.remove(self.selected)
            self.shapes.insert(0, self.selected)

    # ── Rysowanie ─────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        """Rysuje tło, siatkę i wszystkie figury."""
        # Tło
        pygame.draw.rect(surface, CANVAS_BG, self.rect)

        # Siatka
        if self.show_grid:
            self._draw_grid(surface)

        # Figury
        clip = surface.get_clip()
        surface.set_clip(self.rect)
        for shape in self.shapes:
            shape.draw(surface)
        surface.set_clip(clip)

        # Ramka obszaru
        pygame.draw.rect(surface, (50, 55, 70), self.rect, 1)

    def _draw_grid(self, surface: pygame.Surface) -> None:
        step = 30
        for x in range(self.rect.left, self.rect.right, step):
            pygame.draw.line(surface, GRID_COLOR, (x, self.rect.top), (x, self.rect.bottom))
        for y in range(self.rect.top, self.rect.bottom, step):
            pygame.draw.line(surface, GRID_COLOR, (self.rect.left, y), (self.rect.right, y))

    # ── Serializacja (używana przez storage.py) ───────────────────────────────
    def get_shapes(self) -> list[Shape]:
        return list(self.shapes)

    def load_shapes(self, shapes: list[Shape]) -> None:
        self.shapes = list(shapes)
        self.selected = None

    # ── Informacje ────────────────────────────────────────────────────────────
    def count(self) -> int:
        return len(self.shapes)

    def shape_infos(self) -> list[str]:
        return [s.info() for s in self.shapes]
