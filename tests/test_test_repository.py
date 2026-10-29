"""Тесты локального тестового репозитория."""

import json
import tempfile
import unittest
from pathlib import Path

from src.test_repository import (
    get_test_dependencies,
    load_test_repository,
    make_test_node,
)


class TestTestRepository(unittest.TestCase):
    """Проверить тестовый репозиторий."""

    def make_repository(self, data):
        """Создать временный JSON-файл."""
        temp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            encoding="utf-8",
        )
        json.dump(data, temp)
        temp.close()
        return Path(temp.name)

    def test_valid_repository(self):
        """Загрузить корректный репозиторий."""
        path = self.make_repository(
            {
                "A": {
                    "1.0.0": ["B@1.0.0"],
                },
                "B": {
                    "1.0.0": [],
                },
            }
        )

        try:
            repository = load_test_repository(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertEqual(
            repository["A"]["1.0.0"],
            ["B@1.0.0"],
        )

    def test_invalid_package_name(self):
        """Проверить неверное имя пакета."""
        path = self.make_repository(
            {
                "PackageA": {
                    "1.0.0": [],
                },
            }
        )

        try:
            with self.assertRaises(ValueError):
                load_test_repository(path)
        finally:
            path.unlink(missing_ok=True)

    def test_invalid_version(self):
        """Проверить пустую версию."""
        path = self.make_repository(
            {
                "A": {
                    "": [],
                },
            }
        )

        try:
            with self.assertRaises(ValueError):
                load_test_repository(path)
        finally:
            path.unlink(missing_ok=True)

    def test_invalid_dependencies(self):
        """Проверить неверный список зависимостей."""
        path = self.make_repository(
            {
                "A": {
                    "1.0.0": "B@1.0.0",
                },
            }
        )

        try:
            with self.assertRaises(ValueError):
                load_test_repository(path)
        finally:
            path.unlink(missing_ok=True)

    def test_missing_package(self):
        """Проверить отсутствующий пакет."""
        repository = {
            "A": {
                "1.0.0": [],
            },
        }

        with self.assertRaises(ValueError):
            get_test_dependencies(
                repository,
                "B@1.0.0",
            )

    def test_missing_version(self):
        """Проверить отсутствующую версию."""
        repository = {
            "A": {
                "1.0.0": [],
            },
        }

        with self.assertRaises(ValueError):
            get_test_dependencies(
                repository,
                "A@9.9.9",
            )

    def test_missing_dependency_version(self):
        """Проверить неверную версию зависимости."""
        path = self.make_repository(
            {
                "A": {
                    "1.0.0": ["B@2.0.0"],
                },
                "B": {
                    "1.0.0": [],
                },
            }
        )

        try:
            with self.assertRaises(ValueError):
                load_test_repository(path)
        finally:
            path.unlink(missing_ok=True)

    def test_make_test_node(self):
        """Сформировать тестовый узел."""
        node = make_test_node(
            "A",
            "1.0.0",
        )

        self.assertEqual(
            node,
            "A@1.0.0",
        )


if __name__ == "__main__":
    unittest.main()