"""Тесты построения графа зависимостей."""

import unittest

from src.graph import (
    build_dependency_graph,
    build_reverse_dependency_graph,
)


class TestGraph(unittest.TestCase):
    """Проверить операции над графом."""

    def test_simple_graph(self):
        """Построить обычный граф."""
        repository = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }

        graph = build_dependency_graph(
            "A",
            repository.get,
        )

        self.assertEqual(
            graph,
            {
                "A": ["B", "C"],
                "B": ["D"],
                "D": [],
                "C": ["D"],
            },
        )

    def test_deep_graph(self):
        """Построить глубокий граф."""
        repository = {
            "A": ["B"],
            "B": ["C"],
            "C": ["D"],
            "D": ["E"],
            "E": [],
        }

        graph = build_dependency_graph(
            "A",
            repository.get,
        )

        self.assertEqual(
            graph["D"],
            ["E"],
        )
        self.assertIn(
            "E",
            graph,
        )

    def test_cycle(self):
        """Обработать циклический граф."""
        repository = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }

        graph = build_dependency_graph(
            "A",
            repository.get,
        )

        self.assertEqual(
            set(graph),
            {"A", "B", "C"},
        )
        self.assertEqual(
            graph["C"],
            ["A"],
        )

    def test_single_package(self):
        """Обработать пакет без зависимостей."""
        repository = {
            "A": [],
        }

        graph = build_dependency_graph(
            "A",
            repository.get,
        )

        self.assertEqual(
            graph,
            {"A": []},
        )

    def test_reverse_simple_graph(self):
        """Найти обратные зависимости простого графа."""
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "D": [],
            "C": ["D"],
        }

        reverse_graph = (
            build_reverse_dependency_graph(
                graph,
                "D",
            )
        )

        self.assertEqual(
            set(reverse_graph),
            {"D", "B", "C", "A"},
        )

    def test_reverse_deep_graph(self):
        """Найти обратные зависимости глубокого графа."""
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["D"],
            "D": ["E"],
            "E": [],
        }

        reverse_graph = (
            build_reverse_dependency_graph(
                graph,
                "E",
            )
        )

        self.assertEqual(
            set(reverse_graph),
            {"E", "D", "C", "B", "A"},
        )

    def test_reverse_cycle(self):
        """Обработать цикл в обратном графе."""
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }

        reverse_graph = (
            build_reverse_dependency_graph(
                graph,
                "B",
            )
        )

        self.assertEqual(
            set(reverse_graph),
            {"A", "B", "C"},
        )

    def test_reverse_missing_target(self):
        """Обработать отсутствующий целевой узел."""
        graph = {
            "A": ["B"],
            "B": [],
        }

        with self.assertRaises(ValueError):
            build_reverse_dependency_graph(
                graph,
                "C",
            )


if __name__ == "__main__":
    unittest.main()