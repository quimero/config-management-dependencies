"""Тесты построения графа зависимостей."""

import unittest

from src.graph import build_dependency_graph


class TestGraph(unittest.TestCase):
    """Проверить алгоритм DFS."""

    def test_simple_graph(self):
        """Построить обычный граф."""
        repository = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }

        def provider(package):
            return repository[package]

        graph = build_dependency_graph(
            "A",
            provider,
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

        def provider(package):
            return repository[package]

        graph = build_dependency_graph(
            "A",
            provider,
        )

        self.assertIn("E", graph)
        self.assertEqual(graph["D"], ["E"])

    def test_cycle(self):
        """Обработать циклическую зависимость."""
        repository = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }

        def provider(package):
            return repository[package]

        graph = build_dependency_graph(
            "A",
            provider,
        )

        self.assertEqual(
            graph["C"],
            ["A"],
        )
        self.assertEqual(
            set(graph),
            {"A", "B", "C"},
        )

    def test_single_package(self):
        """Построить граф без зависимостей."""
        repository = {
            "A": [],
        }

        def provider(package):
            return repository[package]

        graph = build_dependency_graph(
            "A",
            provider,
        )

        self.assertEqual(
            graph,
            {"A": []},
        )


if __name__ == "__main__":
    unittest.main()