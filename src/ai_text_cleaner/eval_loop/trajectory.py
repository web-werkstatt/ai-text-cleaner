"""Score-Verlauf-Helpers — Convergence-Detection und kompakte Visualisierung."""

from __future__ import annotations


def improving(trajectory: list[float], min_delta: float) -> bool:
    """True, wenn der letzte Score um mindestens `min_delta` unter dem
    bisherigen Minimum (vor dem letzten Eintrag) liegt.

    Beispiel: trajectory=[0.92, 0.85, 0.84], min_delta=0.05 → False
              (0.85→0.84 ist nur 0.01 besser als 0.85).
              trajectory=[0.92, 0.85, 0.70], min_delta=0.05 → True.
    """
    if len(trajectory) < 2:
        return True
    previous_best = min(trajectory[:-1])
    return (previous_best - trajectory[-1]) >= min_delta


def total_improvement(trajectory: list[float]) -> float:
    """Differenz zwischen erstem und bestem (= niedrigstem) Score.
    Positive Werte = Verbesserung (Score sinkt = weniger KI-haft).
    """
    if not trajectory:
        return 0.0
    return trajectory[0] - min(trajectory)


def plot_ascii(trajectory: list[float]) -> str:
    """Kompakter ASCII-Plot des Score-Verlaufs für Report-Output.

    Score-Achse 0.0–1.0, Iterationen horizontal.
    """
    if not trajectory:
        return "(leer)"
    height = 5
    lines: list[list[str]] = [[" " for _ in range(len(trajectory))] for _ in range(height)]
    for col, score in enumerate(trajectory):
        clamped = max(0.0, min(1.0, score))
        row = height - 1 - int(round(clamped * (height - 1)))
        lines[row][col] = "●"
    grid = "\n".join("".join(row) for row in lines)
    start, end = trajectory[0], trajectory[-1]
    best = min(trajectory)
    return f"{grid}\nstart={start:.3f}  end={end:.3f}  best={best:.3f}  n={len(trajectory)}"


__all__ = ["improving", "plot_ascii", "total_improvement"]
