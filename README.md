# Geometry Painter

Prosty edytor figur geometrycznych 2D napisany w Pythonie z wykorzystaniem biblioteki Pygame.
<!-- TOC -->
* [Geometry Painter](#geometry-painter)
  * [Uruchomienie](#uruchomienie)
  * [Struktura projektu](#struktura-projektu)
  * [Figury](#figury)
  * [Sterowanie](#sterowanie)
  * [Zadania dodatkowe (zaimplementowane)](#zadania-dodatkowe-zaimplementowane)
  * [Wymagania techniczne](#wymagania-techniczne)
<!-- TOC -->

## Uruchomienie

```bash
pip install -r requirements.txt
python main.py
```

## Struktura projektu

| Moduł | Opis |
|-------|------|
| `main.py` | Punkt wejścia, pętla główna Pygame, obsługa zdarzeń |
| `shapes.py` | Klasa bazowa `Shape` + klasy pochodne (5 typów figur) |
| `canvas.py` | Kolekcja figur, zaznaczanie, drag & drop, siatka |
| `ui.py` | Panel boczny, przyciski, suwaki, paleta kolorów, toast |
| `storage.py` | Zapis/odczyt stanu programu przy użyciu Pickle |

## Figury

- **Okrąg** – środek + promień
- **Prostokąt** – lewy-górny róg + szerokość + wysokość
- **Kwadrat** – lewy-górny róg + bok
- **Trójkąt** – środek + rozmiar (równoboczny)
- **Wielokąt foremny** – środek + promień + liczba boków (3–12)

## Sterowanie

| Akcja | Klawisz |
|-------|---------|
| Tryb zaznaczania | `S` |
| Tryb rysowania | `D` |
| Okrąg | `C` |
| Prostokąt | `R` |
| Kwadrat | `Q` |
| Trójkąt | `T` |
| Wielokąt | `P` |
| Usuń zaznaczoną | `Delete` |
| Zapisz projekt | `Ctrl+S` |
| Wczytaj projekt | `Ctrl+O` |
| Pokaż/ukryj siatkę | `G` |
| Na wierzch | `PageUp` |
| Na dół | `PageDown` |
| Odznacz | `Escape` |

## Zadania dodatkowe (zaimplementowane)

- ✅ Dodatkowy typ figury – Wielokąt foremny (`RegularPolygon`)
- ✅ Usuwanie figur (`Delete` lub przycisk)
- ✅ Przesuwanie figur (drag & drop myszą)
- ✅ Zaznaczanie figury kliknięciem myszy
- ✅ Siatka pomocnicza (wł./wył.)
- ✅ Kolejność warstw (na wierzch / na dół)
- ✅ Toast z komunikatami o akcjach

## Wymagania techniczne

- Klasy + dziedziczenie (`Shape` → `Circle`, `Rectangle`, `Square`, `Triangle`, `RegularPolygon`)
- Hermetyzacja (prywatne metody i atrybuty)
- Polimorfizm (`draw()`, `contains_point()`, `info()`)
- Kolekcja obiektów (`list[Shape]` w `Canvas`)
- Moduły (5 osobnych plików .py)
- Biblioteka zewnętrzna: `pygame` (PyPI)
- Instrukcje warunkowe, pętle, funkcje – w każdym module
- Formatowanie napisów (`f-string` w metodach `info()`)
- Zapis/odczyt Pickle (`storage.py`)
