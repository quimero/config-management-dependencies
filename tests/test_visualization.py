"""Тесты визуализации графа."""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.visualization import (
    build_ascii_tree,
    graph_to_d2,
    render_d2,
    save_d2_source,
)


class TestVisualization(unittest.TestCase):
    """Проверить визуализацию графа."""

    def test_graph_to_d2(self):
        """Преобразовать граф в D2."""
        graph = {
            "A@1.0.0": ["B@1.0.0"],
            "B@1.0.0": [],
        }

        result = graph_to_d2(graph)

        self.assertIn(
            '"A@1.0.0" -> "B@1.0.0"',
            result,
        )

    def test_d2_single_node(self):
        """Добавить отдельный узел в D2."""
        graph = {
            "A@1.0.0": [],
        }

        result = graph_to_d2(graph)

        self.assertIn(
            '"A@1.0.0"',
            result,
        )

    def test_ascii_tree(self):
        """Построить обычное ASCII-дерево."""
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }

        result = build_ascii_tree(
            graph,
            "A",
        )

        self.assertIn(
            "├── B",
            result,
        )
        self.assertIn(
            "└── C",
            result,
        )

    def test_ascii_cycle(self):
        """Обработать цикл в ASCII-дереве."""
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }

        result = build_ascii_tree(
            graph,
            "A",
        )

        self.assertIn(
            "A [cycle]",
            result,
        )

    def test_ascii_missing_root(self):
        """Обработать отсутствующий корень."""
        graph = {
            "A": [],
        }

        with self.assertRaises(ValueError):
            build_ascii_tree(
                graph,
                "B",
            )

    def test_save_d2_source(self):
        """Сохранить D2-файл."""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "graph.png"
            source = save_d2_source(
                "A -> B\n",
                output,
            )

            self.assertTrue(
                source.is_file()
            )
            self.assertEqual(
                source.suffix,
                ".d2",
            )

    @patch("src.visualization.subprocess.run")
    def test_render_d2(self, mock_run):
        """Запустить D2 CLI."""
        mock_run.return_value = (
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout="",
                stderr="",
            )
        )

        render_d2(
            "graph.d2",
            "graph.png",
        )

        mock_run.assert_called_once()

    @patch("src.visualization.subprocess.run")
    def test_render_d2_error(self, mock_run):
        """Обработать ошибку D2 CLI."""
        mock_run.return_value = (
            subprocess.CompletedProcess(
                args=[],
                returncode=1,
                stdout="",
                stderr="D2 error",
            )
        )

        with self.assertRaises(ValueError):
            render_d2(
                "graph.d2",
                "graph.png",
            )

    @patch("src.visualization.subprocess.run")
    def test_missing_d2(self, mock_run):
        """Обработать отсутствие D2 CLI."""
        mock_run.side_effect = FileNotFoundError

        with self.assertRaises(ValueError):
            render_d2(
                "graph.d2",
                "graph.png",
            )


if __name__ == "__main__":
    unittest.main()