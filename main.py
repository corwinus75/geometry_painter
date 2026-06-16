"""
main.py – Punkt wejścia aplikacji Geometry Painter.
Pętla główna Pygame, obsługa zdarzeń, integracja modułów.

Uruchomienie:
    python main.py

Skróty klawiszowe:
    S / 1        – tryb zaznaczania
    D / 2        – tryb rysowania
    C            – okrąg
    R            – prostokąt
    Q            – kwadrat
    T            – trójkąt
    P            – wielokąt
    Del          – usuń zaznaczoną figurę
    Ctrl+S       – zapisz projekt
    Ctrl+O       – wczytaj projekt
    G            – pokaż/ukryj siatkę
    Escape       – odznacz
    PageUp/Down  – na wierzch / na dół
"""

import sys
import pygame

from shapes import Circle, Rectangle, Square, Triangle, RegularPolygon
from canvas import Canvas
from storage import Storage
from ui import SidePanel, TopBar, Toast, init_fonts, UI_DANGER, UI_SUCCESS, UI_WARNING


# ─── Stałe okna ───────────────────────────────────────────────────────────────
WINDOW_W    = 1200
WINDOW_H    = 950
TOPBAR_H    = 42
PANEL_W     = 250
FPS         = 60


def _compute_layout(w: int, h: int) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
    canvas_rect = pygame.Rect(0, TOPBAR_H, w - PANEL_W, h - TOPBAR_H)
    panel_rect  = pygame.Rect(w - PANEL_W, TOPBAR_H, PANEL_W, h - TOPBAR_H)
    topbar_rect = pygame.Rect(0, 0, w, TOPBAR_H)
    return canvas_rect, panel_rect, topbar_rect


# ─────────────────────────────────────────────────────────────────────────────
# Fabryka figur
# ─────────────────────────────────────────────────────────────────────────────
def create_shape(shape_type: str, x: int, y: int, panel: SidePanel):
    """Tworzy figurę wybranego typu na podstawie ustawień panelu."""
    color = panel.color
    s1 = panel.size1
    s2 = panel.size2
    s3 = panel.size3
    sides = panel.sides

    if shape_type == "circle":
        return Circle(x, y, s1, color)
    elif shape_type == "rect":
        return Rectangle(x - s2 // 2, y - s3 // 2, s2, s3, color)
    elif shape_type == "square":
        return Square(x - s1 // 2, y - s1 // 2, s1, color)
    elif shape_type == "triangle":
        return Triangle(x, y, s1, color)
    elif shape_type == "polygon":
        return RegularPolygon(x, y, s1, sides, color)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Główna pętla
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    pygame.init()
    win_w, win_h = WINDOW_W, WINDOW_H
    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    pygame.display.set_caption("Geometry Painter")
    clock  = pygame.time.Clock()

    init_fonts()

    canvas_rect, panel_rect, topbar_rect = _compute_layout(win_w, win_h)
    canvas  = Canvas(canvas_rect)
    panel   = SidePanel(panel_rect)
    topbar  = TopBar(topbar_rect)
    storage = Storage()
    toast   = Toast()

    # Mapa klawiszy → typy figur
    shape_keys = {
        pygame.K_c: "circle",
        pygame.K_r: "rect",
        pygame.K_q: "square",
        pygame.K_t: "triangle",
        pygame.K_p: "polygon",
    }

    running = True
    while running:
        dt = clock.tick(FPS)
        toast.update(dt)

        # ── Aktualizuj layout przy zmianie rozmiaru okna ───────────────────────
        new_w, new_h = screen.get_size()
        if (new_w, new_h) != (win_w, win_h):
            win_w, win_h = new_w, new_h
            canvas_rect, panel_rect, topbar_rect = _compute_layout(win_w, win_h)
            canvas.rect = canvas_rect
            panel.resize(panel_rect)
            topbar.rect = topbar_rect


        # ── Zdarzenia ─────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # ── Klawiatura ────────────────────────────────────────────────────
            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                ctrl = mods & pygame.KMOD_CTRL

                # Skróty trybu
                if event.key == pygame.K_s and not ctrl:
                    panel._set_tool(panel.TOOL_SELECT)
                elif event.key in (pygame.K_d,) and not ctrl:
                    panel._set_tool(panel.TOOL_DRAW)

                # Ctrl+S / Ctrl+O
                elif event.key == pygame.K_s and ctrl:
                    _action_save(storage, canvas, toast)
                elif event.key == pygame.K_o and ctrl:
                    _action_load(storage, canvas, toast)

                # Wybór figury
                elif event.key in shape_keys and not ctrl:
                    key = shape_keys[event.key]
                    panel._set_shape(key)
                    panel._set_tool(panel.TOOL_DRAW)

                # Usuń zaznaczoną
                elif event.key == pygame.K_DELETE:
                    _action_delete(canvas, toast)

                # Siatka
                elif event.key == pygame.K_g:
                    canvas.show_grid = not canvas.show_grid

                # Escape – odznacz
                elif event.key == pygame.K_ESCAPE:
                    canvas.deselect()

                # PageUp / PageDown – kolejność
                elif event.key == pygame.K_PAGEUP:
                    canvas.bring_to_front()
                elif event.key == pygame.K_PAGEDOWN:
                    canvas.send_to_back()

            # ── Panel boczny ─────────────────────────────────────────────────
            actions = panel.handle_event(event)
            if "action" in actions:
                act = actions["action"]
                if act == "save":
                    _action_save(storage, canvas, toast)
                elif act == "load":
                    _action_load(storage, canvas, toast)
                elif act == "delete":
                    _action_delete(canvas, toast)
                elif act == "clear":
                    _action_clear(canvas, toast)
                elif act == "toggle_grid":
                    canvas.show_grid = not canvas.show_grid
                elif act == "to_front":
                    canvas.bring_to_front()
                elif act == "to_back":
                    canvas.send_to_back()

            # ── Kliknięcia na płótno ─────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if canvas.rect.collidepoint(mx, my):
                    if panel.tool == panel.TOOL_DRAW:
                        shape = create_shape(panel.shape_type, mx, my, panel)
                        if shape:
                            canvas.add_shape(shape)
                            print(f"  + {shape.info()}")
                    elif panel.tool == panel.TOOL_SELECT:
                        hit = canvas.try_select(mx, my)
                        if hit:
                            canvas.start_drag(mx, my)

            elif event.type == pygame.MOUSEMOTION:
                canvas.update_drag(*event.pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                canvas.end_drag()

        # ── Rysowanie ─────────────────────────────────────────────────────────
        screen.fill((18, 21, 28))

        canvas.draw(screen)
        topbar.draw(screen, canvas.count(), panel.tool, panel.shape_type)

        sel_info = canvas.selected.info() if canvas.selected else None
        panel.draw(screen, canvas.shape_infos(), sel_info)

        # Toast na środku płótna (dół)
        toast.draw(screen,
                   canvas.rect.centerx,
                   canvas.rect.bottom - 35)

        # Kursor: zmień kiedy w trybie rysowania
        if canvas.rect.collidepoint(pygame.mouse.get_pos()):
            if panel.tool == panel.TOOL_DRAW:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
            elif canvas.is_dragging:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


# ─────────────────────────────────────────────────────────────────────────────
# Akcje
# ─────────────────────────────────────────────────────────────────────────────
def _action_save(storage: Storage, canvas: Canvas, toast: Toast) -> None:
    ok, msg = storage.save(canvas.get_shapes())
    color = UI_SUCCESS if ok else UI_DANGER
    toast.show(msg, color)
    print(f"[ZAPIS] {msg}")


def _action_load(storage: Storage, canvas: Canvas, toast: Toast) -> None:
    shapes, msg = storage.load()
    if shapes is not None:
        canvas.load_shapes(shapes)
        toast.show(msg, UI_SUCCESS)
    else:
        toast.show(msg, UI_DANGER)
    print(f"[WCZYT] {msg}")


def _action_delete(canvas: Canvas, toast: Toast) -> None:
    info = canvas.remove_selected()
    if info:
        toast.show(f"Usunięto: {info[:40]}", UI_WARNING)
        print(f"[USUŃ] {info}")
    else:
        toast.show("Nic nie zaznaczono.", UI_DANGER)


def _action_clear(canvas: Canvas, toast: Toast) -> None:
    n = canvas.count()
    canvas.clear_all()
    toast.show(f"Usunięto wszystkie {n} figury.", UI_WARNING)
    print(f"[WYCZYŚĆ] Usunięto {n} figury.")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
