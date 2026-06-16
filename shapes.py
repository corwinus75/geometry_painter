"""
shapes.py – Klasy figur geometrycznych.
Moduł zawiera klasę bazową Shape oraz klasy pochodne:
Circle, Rectangle, Square, Triangle, RegularPolygon.
"""
from abc import abstractmethod

import pygame
import math


# ─── Paleta kolorów domyślnych ────────────────────────────────────────────────
DEFAULT_COLORS = [
    (52, 152, 219),   # niebieski
    (46, 204, 113),   # zielony
    (231, 76, 60),    # czerwony
    (241, 196, 15),   # żółty
    (155, 89, 182),   # fioletowy
    (26, 188, 156),   # turkusowy
    (230, 126, 34),   # pomarańczowy
    (236, 240, 241),  # biały
]


class Shape:
    """Klasa bazowa reprezentująca figurę geometryczną."""

    # Licznik instancji – do generowania unikalnych ID
    _id_counter: int = 0

    def __init__(self, x: int, y: int, color: tuple[int, int, int]):
        Shape._id_counter += 1
        self.id: int = Shape._id_counter
        self.x: int = x
        self.y: int = y
        self.color: tuple[int, int, int] = color
        self.selected: bool = False
        self.border_width: int = 2   # grubość obramowania

    # ── Rysowanie ─────────────────────────────────────────────────────────────
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Rysuje figurę na podanej powierzchni (do nadpisania)."""
        pass

    def draw_selection_highlight(self, surface: pygame.Surface) -> None:
        """Rysuje podświetlenie zaznaczenia wokół bounding-box figury."""
        rect = self.bounding_rect()
        if rect:
            r = rect.inflate(8, 8)
            pygame.draw.rect(surface, (255, 255, 255), r, 2, border_radius=4)

    # ── Geometria ─────────────────────────────────────────────────────────────
    @abstractmethod
    def bounding_rect(self):
        """Zwraca prostokąt ograniczający figurę (do nadpisania)."""
        pass
        # return None

    def contains_point(self, px: int, py: int) -> bool:
        """Sprawdza, czy punkt (px, py) leży wewnątrz figury."""
        rect = self.bounding_rect()
        if rect:
            return rect.collidepoint(px, py)
        return False

    def move(self, dx: int, dy: int) -> None:
        """Przesuwa figurę o (dx, dy)."""
        self.x += dx
        self.y += dy

    # ── Informacje ────────────────────────────────────────────────────────────
    def info(self) -> str:
        """Zwraca tekstową informację o figurze."""
        return f"[#{self.id}] {self.__class__.__name__} @ ({self.x}, {self.y})"

    def __repr__(self) -> str:
        return self.info()


# ─── Okrąg ────────────────────────────────────────────────────────────────────
class Circle(Shape):
    """Okrąg opisany przez środek (x, y) i promień."""

    def __init__(self, x: int, y: int, radius: int, color: tuple[int, int, int]):
        super().__init__(x, y, color)
        self.radius: int = max(5, radius)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        border_color = _darken(self.color)
        pygame.draw.circle(surface, border_color, (self.x, self.y), self.radius, self.border_width)
        if self.selected:
            self.draw_selection_highlight(surface)

    def bounding_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x - self.radius, self.y - self.radius,
            self.radius * 2, self.radius * 2
        )

    def contains_point(self, px: int, py: int) -> bool:
        return math.hypot(px - self.x, py - self.y) <= self.radius

    def info(self) -> str:
        return (f"[#{self.id}] Okrąg  środek=({self.x},{self.y})  "
                f"r={self.radius}  kolor={_rgb_str(self.color)}")


# ─── Prostokąt ────────────────────────────────────────────────────────────────
class Rectangle(Shape):
    """Prostokąt opisany lewym-górnym rogiem (x, y), szerokością i wysokością."""

    def __init__(self, x: int, y: int, width: int, height: int,
                 color: tuple[int, int, int]):
        super().__init__(x, y, color)
        self.width: int = max(5, width)
        self.height: int = max(5, height)

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.bounding_rect()
        pygame.draw.rect(surface, self.color, rect, border_radius=4)
        border_color = _darken(self.color)
        pygame.draw.rect(surface, border_color, rect, self.border_width, border_radius=4)
        if self.selected:
            self.draw_selection_highlight(surface)

    def bounding_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def info(self) -> str:
        return (f"[#{self.id}] Prostokąt  ({self.x},{self.y})  "
                f"{self.width}×{self.height}  kolor={_rgb_str(self.color)}")


# ─── Kwadrat ──────────────────────────────────────────────────────────────────
class Square(Rectangle):
    """Kwadrat – prostokąt o równych bokach."""

    def __init__(self, x: int, y: int, side: int, color: tuple[int, int, int]):
        super().__init__(x, y, side, side, color)
        self.side: int = max(5, side)

    def info(self) -> str:
        return (f"[#{self.id}] Kwadrat  ({self.x},{self.y})  "
                f"bok={self.side}  kolor={_rgb_str(self.color)}")


# ─── Trójkąt ──────────────────────────────────────────────────────────────────
class Triangle(Shape):
    """Trójkąt równoboczny opisany środkiem (x, y) i długością boku."""

    def __init__(self, x: int, y: int, size: int, color: tuple[int, int, int]):
        super().__init__(x, y, color)
        self.size: int = max(5, size)

    def _vertices(self) -> list[tuple[float, float]]:
        s = self.size
        return [
            (self.x, self.y - s * math.sqrt(3)/3),  # górny wierzchołek
            (self.x - s/2, self.y + s * math.sqrt(3)/6),  # lewy dolny
            (self.x + s/2, self.y + s * math.sqrt(3)/6),  # prawy dolny
        ]

    def draw(self, surface: pygame.Surface) -> None:
        pts = self._vertices()
        pygame.draw.polygon(surface, self.color, pts)
        border_color = _darken(self.color)
        pygame.draw.polygon(surface, border_color, pts, self.border_width)
        if self.selected:
            self.draw_selection_highlight(surface)

    def bounding_rect(self) -> pygame.Rect:
        pts = self._vertices()
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, y0 = int(min(xs)), int(min(ys))
        x1, y1 = int(max(xs)), int(max(ys))
        return pygame.Rect(x0, y0, x1 - x0, y1 - y0)

    def contains_point(self, px: int, py: int) -> bool:
        """Sprawdzenie metodą znaku pól trójkątów."""
        pts = self._vertices()
        return _point_in_triangle(px, py, pts[0], pts[1], pts[2])

    def info(self) -> str:
        return (f"[#{self.id}] Trójkąt  środek=({self.x},{self.y})  "
                f"bok={self.size}  kolor={_rgb_str(self.color)}")


# ─── Wielokąt foremny ─────────────────────────────────────────────────────────
class RegularPolygon(Shape):
    """Wielokąt foremny n-kątny opisany środkiem (x, y) i promieniem."""

    def __init__(self, x: int, y: int, radius: int, sides: int,
                 color: tuple[int, int, int]):
        super().__init__(x, y, color)
        self.radius: int = max(5, radius)
        self.sides: int = max(3, sides)

    def _vertices(self) -> list[tuple[float, float]]:
        pts = []
        for i in range(self.sides):
            angle = math.radians(360 / self.sides * i - 90)
            px = self.x + self.radius * math.cos(angle)
            py = self.y + self.radius * math.sin(angle)
            pts.append((px, py))
        return pts

    def draw(self, surface: pygame.Surface) -> None:
        pts = self._vertices()
        pygame.draw.polygon(surface, self.color, pts)
        border_color = _darken(self.color)
        pygame.draw.polygon(surface, border_color, pts, self.border_width)
        if self.selected:
            self.draw_selection_highlight(surface)

    def bounding_rect(self) -> pygame.Rect:
        pts = self._vertices()
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, y0 = int(min(xs)), int(min(ys))
        x1, y1 = int(max(xs)), int(max(ys))
        return pygame.Rect(x0, y0, x1 - x0, y1 - y0)

    def contains_point(self, px: int, py: int) -> bool:
        return math.hypot(px - self.x, py - self.y) <= self.radius

    def info(self) -> str:
        return (f"[#{self.id}] Wielokąt-{self.sides}  środek=({self.x},{self.y})  "
                f"r={self.radius}  kolor={_rgb_str(self.color)}")
# To implement eventually
# class Ellipse(Shape):
#     def __init__(self, x: int, y: int, radius: int, color: tuple[int, int, int]):
#         super.__init__(x, y, color)

# ─── Helpery ──────────────────────────────────────────────────────────────────
def _darken(color: tuple[int, int, int], factor: float = 0.6) -> tuple[int, int, int]:
    """Przyciemnia kolor."""
    return tuple(max(0, int(c * factor)) for c in color)


def _rgb_str(color: tuple[int, int, int]) -> str:
    return "rgb({},{},{})".format(*color)


def _sign(val: float) -> float:
    return -1 if val < 0 else (1 if val > 0 else 0)


def _point_in_triangle(px, py, a, b, c) -> bool:
    """Ray-casting – czy punkt (px,py) leży w trójkącie ABC."""
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    d1 = cross((px, py), a, b)
    d2 = cross((px, py), b, c)
    d3 = cross((px, py), c, a)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)
