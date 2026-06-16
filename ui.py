"""
ui.py – Panel boczny, przyciski, pasek narzędzi i okna dialogowe.
Moduł odpowiada za całą warstwę interfejsu użytkownika.
Ikony renderowane fontem FontAwesome Free (fa-solid-900.ttf, licencja OFL).
"""

import pygame
import math
import os
from shapes import DEFAULT_COLORS

# ── Paleta kolorów UI ─────────────────────────────────────────────────────────
UI_BG        = (22, 26, 34)
UI_PANEL     = (53, 53, 66)#(30, 34, 44)
UI_SURFACE   = (38, 43, 54)#pygame.Color('cadetblue1')
UI_BORDER    = (55, 62, 78)
UI_TEXT      = (220, 225, 235)
UI_SUBTEXT   = (130, 140, 160)
UI_ACCENT    = (79, 142, 247)
UI_DANGER    = (220, 60, 60)
UI_SUCCESS   = (60, 180, 100)
UI_WARNING   = (230, 160, 30)

# ── FontAwesome – kody ikon ───────────────────────────────────────────────────
FA = {
    "save":    "\uf0c7",   # floppy disk
    "load":    "\uf07c",   # folder open
    "trash":   "\uf1f8",   # trash
    "draw":    "\uf303",   # pencil-alt
    "select":  "\uf245",   # mouse pointer
    "grid":    "\uf00a",   # grid
    "warning": "\uf071",   # exclamation-triangle
    "up":      "\uf062",   # arrow-up
    "down":    "\uf063",   # arrow-down
    "circle":  "\uf111",   # circle
    "square":  "\uf0c8",   # square
    "rectangle": "\uf0c8\uf0c8", #rectangle
    "shapes":  "\uf61f",   # shapes
    "draw_pen":"\uf304",   # pen
    "polygon": "\uf5ee",   # draw-polygon
    "triangle": "\uf04b",  # triangle
    "times":   "\uf00d",   # times (X)
    "check":   "\uf00c",   # check
}

FONT_SMALL  = None
FONT_MEDIUM = None
FONT_LARGE  = None
FONT_MONO   = None
FONT_FA_SM  = None   # FontAwesome mały (12 px)
FONT_FA_MD  = None   # FontAwesome normalny (14 px)


def _fa_path() -> str:
    """Szuka pliku fa-solid-900.ttf obok modułu ui.py."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "fa-solid-900.ttf")


def init_fonts() -> None:
    """Inicjuje fonty. Wywoływane po pygame.init()."""
    global FONT_SMALL, FONT_MEDIUM, FONT_LARGE, FONT_MONO
    global FONT_FA_SM, FONT_FA_MD
    pygame.font.init()
    FONT_SMALL  = pygame.font.SysFont(['arial', 'segoeui', 'liberationsans', 'dejavusans', 'sans'], 10)
    FONT_MEDIUM = pygame.font.SysFont(['arial', 'segoeui', 'liberationsans', 'dejavusans', 'sans'], 14)
    FONT_LARGE  = pygame.font.SysFont(['arial', 'segoeui', 'liberationsans', 'dejavusans', 'sans'], 17, bold=True)
    FONT_MONO   = pygame.font.SysFont(['consolas', 'inconsolata', 'liberationmono', 'dejavusansmono', 'monospace'], 12)

    fa = _fa_path()
    if os.path.exists(fa):
        FONT_FA_SM = pygame.font.Font(fa, 11)
        FONT_FA_MD = pygame.font.Font(fa, 13)
    else:
        # fallback – bez ikon (nie przerwie programu)
        FONT_FA_SM = FONT_SMALL
        FONT_FA_MD = FONT_MEDIUM


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def draw_text(surface, text, x, y, font=None, color=UI_TEXT, shadow=False):
    if font is None:
        font = FONT_MEDIUM
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        surface.blit(s, (x + 1, y + 1))
    img = font.render(text, True, color)
    surface.blit(img, (x, y))
    return img.get_rect(topleft=(x, y))


def draw_rounded_rect(surface, color, rect, radius=6, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def _wrap_text(text: str, font, max_width: int) -> list[str]:
    """Dzieli tekst na linie pasujące do max_width pikseli."""
    if font.size(text)[0] <= max_width:
        return [text]
    lines = []
    while text:
        lo, hi = 1, len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if font.size(text[:mid])[0] <= max_width:
                lo = mid
            else:
                hi = mid - 1
        lines.append(text[:lo])
        text = text[lo:]
    return lines


def _blit_centered(surface, img, rect):
    """Rysuje obraz wycentrowany w rect."""
    r = img.get_rect(center=rect.center)
    surface.blit(img, r)


# ─────────────────────────────────────────────────────────────────────────────
# Button
# ─────────────────────────────────────────────────────────────────────────────
class Button:
    """
    Interaktywny przycisk z efektem hover/press.
    Ikona (FA) renderowana osobnym fontem obok etykiety tekstowej.
    """

    def __init__(self, rect, label: str, color=UI_SURFACE,
                 text_color=UI_TEXT, icon: str = ""):
        self.rect       = pygame.Rect(rect)
        self.label      = label
        self.icon       = icon          # kod FA np. "\uf0c7"
        self.color      = color
        self.hover_color = _lighten(color, 1.18)
        self.press_color = _lighten(color, 0.82)
        self.text_color = text_color
        self.active     = False
        self._hovered   = False
        self._pressed   = False
        self.enabled    = True

    def handle_event(self, event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self.rect.collidepoint(event.pos):
                self._pressed = False
                return True
            self._pressed = False
        return False

    def draw(self, surface: pygame.Surface) -> None:
        # Kolor tła
        if not self.enabled:
            col = _mix(self.color, UI_BG, 0.5)
        elif self._pressed or self.active:
            col = self.press_color
        elif self._hovered:
            col = self.hover_color
        else:
            col = self.color

        border_col = UI_ACCENT if self.active else UI_BORDER
        border_w   = 2 if self.active else 1
        draw_rounded_rect(surface, col, self.rect, radius=6,
                          border=border_w, border_color=border_col)

        text_col = UI_TEXT if self.enabled else UI_SUBTEXT

        # Renderuj ikonę i tekst osobno
        icon_surf = None
        if self.icon and FONT_FA_MD:
            icon_surf = FONT_FA_MD.render(self.icon, True, text_col)

        text_surf = FONT_MEDIUM.render(self.label, True, text_col)

        # Oblicz łączną szerokość i wycentruj w przycisku
        gap = 6
        total_w = text_surf.get_width()
        if icon_surf:
            total_w += icon_surf.get_width() + gap

        start_x = self.rect.centerx - total_w // 2
        cy = self.rect.centery

        if icon_surf:
            iy = cy - icon_surf.get_height() // 2
            surface.blit(icon_surf, (start_x, iy))
            start_x += icon_surf.get_width() + gap

        ty = cy - text_surf.get_height() // 2
        surface.blit(text_surf, (start_x, ty))


# ─────────────────────────────────────────────────────────────────────────────
# ColorSwatch
# ─────────────────────────────────────────────────────────────────────────────
class ColorSwatch:
    """Pojedynczy kafelek koloru."""

    def __init__(self, rect, color):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.selected = False
        self._hovered = False

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
        if self.selected:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 3, border_radius=4)
        elif self._hovered:
            pygame.draw.rect(surface, UI_TEXT, self.rect, 2, border_radius=4)
        else:
            pygame.draw.rect(surface, UI_BORDER, self.rect, 1, border_radius=4)


# ─────────────────────────────────────────────────────────────────────────────
# Slider
# ─────────────────────────────────────────────────────────────────────────────
class Slider:
    """Suwak wartości liczbowej (int)."""

    def __init__(self, rect, min_val: int, max_val: int, value: int, label: str):
        self.rect = pygame.Rect(rect)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.label = label
        self._dragging = False

    @property
    def _track(self) -> pygame.Rect:
        return pygame.Rect(self.rect.x, self.rect.centery - 3, self.rect.width, 6)

    @property
    def _handle_x(self) -> int:
        ratio = (self.value - self.min_val) / max(1, self.max_val - self.min_val)
        return int(self.rect.x + ratio * self.rect.width)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hx = self._handle_x
            handle_rect = pygame.Rect(hx - 8, self.rect.centery - 8, 16, 16)
            if handle_rect.collidepoint(event.pos) or self._track.collidepoint(event.pos):
                self._dragging = True
                return self._update_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            return self._update_from_mouse(event.pos[0])
        return False

    def _update_from_mouse(self, mx: int) -> bool:
        old = self.value
        ratio = (mx - self.rect.x) / max(1, self.rect.width)
        ratio = max(0.0, min(1.0, ratio))
        self.value = int(self.min_val + ratio * (self.max_val - self.min_val))
        return self.value != old

    def draw(self, surface: pygame.Surface) -> None:
        draw_text(surface, f"{self.label}: {self.value}",
                  self.rect.x, self.rect.y - 16, color=UI_SUBTEXT, font=FONT_SMALL)
        track = self._track
        pygame.draw.rect(surface, UI_BORDER, track, border_radius=3)
        filled = pygame.Rect(track.x, track.y,
                             self._handle_x - track.x, track.height)
        pygame.draw.rect(surface, UI_ACCENT, filled, border_radius=3)
        pygame.draw.circle(surface, UI_ACCENT, (self._handle_x, self.rect.centery), 8)
        pygame.draw.circle(surface, UI_TEXT,   (self._handle_x, self.rect.centery), 8, 2)


# ─────────────────────────────────────────────────────────────────────────────
# Toast
# ─────────────────────────────────────────────────────────────────────────────
class Toast:
    """Krótki komunikat wyświetlany na ekranie przez określony czas."""

    def __init__(self):
        self._msg: str = ""
        self._color = UI_SUCCESS
        self._timer: int = 0

    def show(self, msg: str, color=UI_SUCCESS, duration_ms: int = 2500) -> None:
        self._msg = msg
        self._color = color
        self._timer = duration_ms

    def update(self, dt_ms: int) -> None:
        if self._timer > 0:
            self._timer -= dt_ms

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        if self._timer <= 0 or not self._msg:
            return
        img = FONT_MEDIUM.render(self._msg, True, self._color)
        surface.blit(img, (x - img.get_width() // 2, y))


# ─────────────────────────────────────────────────────────────────────────────
# SidePanel
# ─────────────────────────────────────────────────────────────────────────────
class SidePanel:
    TOOL_SELECT = "select"
    TOOL_DRAW   = "draw"

    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.tool       = self.TOOL_SELECT
        self.shape_type = "circle"
        self.color      = DEFAULT_COLORS[0]
        self.size1      = 50
        self.size2      = 100
        self.size3      = 60
        self.sides      = 6
        self._list_scroll    = 0
        self._list_rect      = pygame.Rect(0, 0, 0, 0)
        self._list_content_h = 0
        self._build_widgets()

    def resize(self, rect: pygame.Rect) -> None:
        """Przebudowuje widgety po zmianie rozmiaru panelu zachowując stan."""
        tool   = self.tool
        shape  = self.shape_type
        color  = self.color
        size1, size2, size3, sides = self.size1, self.size2, self.size3, self.sides
        self.rect = rect
        self._build_widgets()
        self._set_tool(tool)
        self._set_shape(shape)
        self._set_color(color)
        self.sl_size1.value = size1
        self.sl_size2.value = size2
        self.sl_size3.value = size3
        self.sl_sides.value = sides

    def _build_widgets(self) -> None:
        x = self.rect.x + 10
        w = self.rect.width - 20
        y = self.rect.y + 10

        # Tryb narzędzia
        bw = (w - 4) // 2
        self.btn_select = Button((x, y, bw, 32), "Zaznacz",
                                 icon=FA["select"], color=UI_SURFACE)
        self.btn_draw   = Button((x + bw + 4, y, bw, 32), "Rysuj",
                                 icon=FA["draw"], color=UI_SURFACE)
        self.btn_select.active = True
        y += 42

        # Typ figury
        shape_defs = [
            ("circle",   FA["circle"],   "Okrąg"),
            ("rect",     FA["rectangle"],   "Prostokąt"),
            ("square",   FA["square"],   "Kwadrat"),
            ("triangle", FA["triangle"],    "Trójkąt"),
            ("polygon",  FA["polygon"],  "Wielokąt"),
        ]
        self.shape_buttons: dict[str, Button] = {}
        bh = 28
        for key, icon, lbl in shape_defs:
            btn = Button((x, y, w, bh), lbl, color=UI_SURFACE, icon=icon)
            self.shape_buttons[key] = btn
            y += bh + 3
        self.shape_buttons["circle"].active = True
        y += 8

        # Suwaki
        sl_w = w
        y += 18  # miejsce na "_section_label ROZMIAR"
        self.sl_size1 = Slider((x, y + 16, sl_w, 20), 10, 150, 50,  "Rozmiar")
        y += 48
        self.sl_size2 = Slider((x, y + 16, sl_w, 20), 10, 250, 100, "Szerokość")
        y += 48
        self.sl_size3 = Slider((x, y + 16, sl_w, 20), 10, 250, 60,  "Wysokość")
        y += 48
        self.sl_sides = Slider((x, y + 16, sl_w, 20), 3, 12,  6,    "Boki")
        y += 48 + 8

        # Paleta kolorów
        sw = 22
        self.swatches: list[ColorSwatch] = []
        per_row = w // (sw + 4)
        for i, col in enumerate(DEFAULT_COLORS):
            cx = x + (i % per_row) * (sw + 4)
            cy = y + (i // per_row) * (sw + 4)
            self.swatches.append(ColorSwatch((cx, cy, sw, sw), col))
        self.swatches[0].selected = True
        rows = math.ceil(len(DEFAULT_COLORS) / per_row)
        y += rows * (sw + 4) + 10

        # Operacje
        self.btn_save     = Button((x, y, w, 30), "Zapisz projekt",
                                   color=(40, 70, 50), icon=FA["save"])
        y += 34
        self.btn_load     = Button((x, y, w, 30), "Wczytaj projekt",
                                   color=(40, 55, 80), icon=FA["load"])
        y += 34
        self.btn_delete   = Button((x, y, w, 30), "Usuń zaznaczoną",
                                   color=(70, 35, 35), icon=FA["trash"],
                                   text_color=(255, 120, 120))
        y += 34
        self.btn_clear    = Button((x, y, w, 30), "Wyczyść",
                                   color=(60, 40, 30), icon=FA["warning"],
                                   text_color=(230, 160, 30))
        y += 34
        self.btn_grid     = Button((x, y, w, 30), "Siatka wł./wył.",
                                   color=UI_SURFACE, icon=FA["grid"])
        y += 34
        self.btn_to_front = Button((x, y, (w - 4) // 2, 28), "Wierzch",
                                   icon=FA["up"])
        self.btn_to_back  = Button((x + (w - 4) // 2 + 4, y, (w - 4) // 2, 28),
                                   "Dół", icon=FA["down"])
        y += 38
        self._list_y = y

    # ── Aktywne przyciski ─────────────────────────────────────────────────────
    def _set_tool(self, tool: str) -> None:
        self.tool = tool
        self.btn_select.active = (tool == self.TOOL_SELECT)
        self.btn_draw.active   = (tool == self.TOOL_DRAW)

    def _set_shape(self, key: str) -> None:
        self.shape_type = key
        for k, btn in self.shape_buttons.items():
            btn.active = (k == key)

    def _set_color(self, color: tuple) -> None:
        self.color = color
        for sw in self.swatches:
            sw.selected = (sw.color == color)

    # ── Zdarzenia ─────────────────────────────────────────────────────────────
    def handle_event(self, event) -> dict:
        result = {}

        if self.btn_select.handle_event(event):
            self._set_tool(self.TOOL_SELECT)
            result["tool"] = self.TOOL_SELECT
        if self.btn_draw.handle_event(event):
            self._set_tool(self.TOOL_DRAW)
            result["tool"] = self.TOOL_DRAW

        for key, btn in self.shape_buttons.items():
            if btn.handle_event(event):
                self._set_shape(key)
                self._set_tool(self.TOOL_DRAW)
                result["shape_type"] = key
                result["tool"] = self.TOOL_DRAW

        for sl in [self.sl_size1, self.sl_size2, self.sl_size3, self.sl_sides]:
            sl.handle_event(event)
        self.size1 = self.sl_size1.value
        self.size2 = self.sl_size2.value
        self.size3 = self.sl_size3.value
        self.sides = self.sl_sides.value

        for sw in self.swatches:
            if sw.handle_event(event):
                self._set_color(sw.color)
                result["color"] = sw.color

        if self.btn_save.handle_event(event):     result["action"] = "save"
        if self.btn_load.handle_event(event):     result["action"] = "load"
        if self.btn_delete.handle_event(event):   result["action"] = "delete"
        if self.btn_clear.handle_event(event):    result["action"] = "clear"
        if self.btn_grid.handle_event(event):     result["action"] = "toggle_grid"
        if self.btn_to_front.handle_event(event): result["action"] = "to_front"
        if self.btn_to_back.handle_event(event):  result["action"] = "to_back"

        if event.type == pygame.MOUSEWHEEL:
            if self._list_rect.collidepoint(pygame.mouse.get_pos()):
                visible_h = max(1, self._list_rect.height - 10)
                max_scroll = max(0, self._list_content_h - visible_h)
                self._list_scroll = max(0, min(max_scroll,
                                               self._list_scroll - event.y * 15))

        return result

    # ── Widoczność suwaków ────────────────────────────────────────────────────
    def _slider_visible(self, name: str) -> bool:
        st = self.shape_type
        if name == "size1":
            return st in {"circle", "square", "triangle","polygon"}
        if name == "size2": return st == "rect"
        if name == "size3": return st == "rect"
        if name == "sides": return st == "polygon"
        return False

    # ── Rysowanie ─────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface, shape_infos: list[str],
             selected_info: str | None = None) -> None:

        draw_rounded_rect(surface, UI_PANEL, self.rect, radius=0)
        pygame.draw.line(surface, UI_BORDER,
                         (self.rect.x, self.rect.y),
                         (self.rect.x, self.rect.bottom))

        x, w = self.rect.x + 10, self.rect.width - 20

        self._section_label(surface, x, self.rect.y + 10, "TRYB")
        self.btn_select.draw(surface)
        self.btn_draw.draw(surface)

        sy = self.btn_select.rect.bottom + 12
        self._section_label(surface, x, sy, "FIGURA")
        for btn in self.shape_buttons.values():
            btn.draw(surface)

        sl_y = list(self.shape_buttons.values())[-1].rect.bottom + 14
        self._section_label(surface, x, sl_y, "ROZMIAR")

        if self._slider_visible("size1"): self.sl_size1.draw(surface)
        if self._slider_visible("size2"): self.sl_size2.draw(surface)
        if self._slider_visible("size3"): self.sl_size3.draw(surface)
        if self._slider_visible("sides"): self.sl_sides.draw(surface)
        col_y = self.sl_sides.rect.bottom - 4
        self._section_label(surface, x, col_y, "KOLOR")
        for sw in self.swatches:
            sw.draw(surface)

        # Podgląd aktualnego koloru
        pygame.draw.rect(surface, self.color,
                         pygame.Rect(x + w - 30, col_y - 3, 22, 22), border_radius=4)
        pygame.draw.rect(surface, UI_BORDER,
                         pygame.Rect(x + w - 30, col_y - 3, 22, 22), 1, border_radius=4)

        op_y = self.swatches[-1].rect.bottom + 14
        self._section_label(surface, x, op_y, "OPERACJE")
        for btn in [self.btn_save, self.btn_load, self.btn_delete,
                    self.btn_clear, self.btn_grid,
                    self.btn_to_front, self.btn_to_back]:
            btn.draw(surface)

        # Lista figur
        list_y = self._list_y
        self._section_label(surface, x, list_y, f"FIGURY ({len(shape_infos)})")
        list_y += 16
        list_rect = pygame.Rect(x, list_y, w, self.rect.bottom - list_y - 8)
        self._list_rect = list_rect
        pygame.draw.rect(surface, UI_SURFACE, list_rect, border_radius=4)
        pygame.draw.rect(surface, UI_BORDER,  list_rect, 1, border_radius=4)

        # Zbuduj wszystkie linie (z zawijaniem) żeby znać łączną wysokość
        max_w = list_rect.width - 14
        all_lines: list[tuple[str, tuple]] = []
        for info in reversed(shape_infos):
            col = UI_ACCENT if (selected_info and info == selected_info) else UI_SUBTEXT
            for line in _wrap_text(info, FONT_SMALL, max_w):
                all_lines.append((line, col))

        total_h = len(all_lines) * 15
        self._list_content_h = total_h
        visible_h = max(1, list_rect.height - 10)
        max_scroll = max(0, total_h - visible_h)
        self._list_scroll = min(self._list_scroll, max_scroll)

        clip = surface.get_clip()
        surface.set_clip(list_rect.inflate(-2, -2))
        iy = list_rect.y + 5 - self._list_scroll
        for line, col in all_lines:
            if iy + 15 > list_rect.y:
                draw_text(surface, line, list_rect.x + 5, iy, font=FONT_SMALL, color=col)
            iy += 15
            if iy >= list_rect.bottom - 5:
                break
        surface.set_clip(clip)

        # Scrollbar – rysowany tylko gdy treść nie mieści się w całości
        if total_h > visible_h:
            sb_x  = list_rect.right - 5
            sb_h  = list_rect.height - 6
            thumb_h = max(16, sb_h * visible_h // max(1, total_h))
            thumb_y = list_rect.y + 3 + (sb_h - thumb_h) * self._list_scroll // max(1, max_scroll)
            pygame.draw.rect(surface, UI_BORDER,
                             (sb_x, list_rect.y + 3, 4, sb_h), border_radius=2)
            pygame.draw.rect(surface, UI_ACCENT,
                             (sb_x, thumb_y, 4, thumb_h), border_radius=2)

    @staticmethod
    def _section_label(surface, x, y, text):
        draw_text(surface, text, x, y, font=FONT_SMALL, color=UI_SUBTEXT)
        pygame.draw.line(surface, UI_BORDER,
                         (x + len(text) * 7 + 4, y + 6),
                         (x + 175, y + 6))


# ─────────────────────────────────────────────────────────────────────────────
# TopBar
# ─────────────────────────────────────────────────────────────────────────────
class TopBar:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect

    def draw(self, surface: pygame.Surface, canvas_count: int,
             tool: str, shape_type: str) -> None:
        draw_rounded_rect(surface, UI_BG, self.rect, radius=0)
        pygame.draw.line(surface, UI_BORDER,
                         (self.rect.x, self.rect.bottom),
                         (self.rect.right, self.rect.bottom))

        # Ikona + tytuł
        if FONT_FA_MD:
            icon_surf = FONT_FA_MD.render(FA["shapes"], True, UI_ACCENT)
            surface.blit(icon_surf, (self.rect.x + 12, self.rect.centery - icon_surf.get_height() // 2))
            tx = self.rect.x + 12 + icon_surf.get_width() + 6
        else:
            tx = self.rect.x + 12

        draw_text(surface, "Geometry Painter",
                  tx, self.rect.centery - 9,
                  font=FONT_LARGE, color=UI_TEXT)

        tool_label = "Zaznaczanie" if tool == "select" else f"Rysuj: {shape_type}"
        status = (f"Figury: {canvas_count}  |  Tryb: {tool_label}  |  "
                  f"[Del] usuń  [Ctrl+S] zapisz  [Ctrl+O] wczytaj  [G] siatka")
        draw_text(surface, status,
                  self.rect.x + 230, self.rect.centery - 7,
                  font=FONT_SMALL, color=UI_SUBTEXT)


# ─────────────────────────────────────────────────────────────────────────────
# Helpery prywatne
# ─────────────────────────────────────────────────────────────────────────────
def _lighten(color, factor: float) -> tuple:
    return tuple(min(255, int(c * factor)) for c in color)


def _mix(a, b, t: float) -> tuple:
    return tuple(int(ac * (1 - t) + bc * t) for ac, bc in zip(a, b))