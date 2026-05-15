"""Tests für eval_loop/trajectory.py."""

from __future__ import annotations

from ai_text_cleaner.eval_loop.trajectory import improving, plot_ascii, total_improvement


def test_improving_empty() -> None:
    assert improving([], 0.01) is True


def test_improving_single_entry() -> None:
    assert improving([0.5], 0.01) is True


def test_improving_below_delta() -> None:
    assert improving([0.85, 0.84], 0.05) is False


def test_improving_above_delta() -> None:
    assert improving([0.85, 0.70], 0.05) is True


def test_improving_against_previous_best() -> None:
    assert improving([0.90, 0.50, 0.80], 0.01) is False
    assert improving([0.90, 0.50, 0.40], 0.05) is True


def test_total_improvement_positive_when_score_falls() -> None:
    assert total_improvement([0.90, 0.60, 0.40]) == 0.5


def test_total_improvement_zero_for_empty() -> None:
    assert total_improvement([]) == 0.0


def test_plot_ascii_contains_summary() -> None:
    plot = plot_ascii([0.9, 0.6, 0.3])
    assert "start=0.900" in plot
    assert "end=0.300" in plot
    assert "best=0.300" in plot
    assert "n=3" in plot


def test_plot_ascii_handles_empty() -> None:
    assert plot_ascii([]) == "(leer)"
