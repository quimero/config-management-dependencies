"""Тесты XML-конфигурации."""

import tempfile
import unittest
from pathlib import Path

from src.config import load_config


VALID_XML = """<?xml version="1.0" encoding="UTF-8"?>
<config>
    <package>Newtonsoft.Json</package>
    <repository>https://api.nuget.org/v3/index.json</repository>
    <test_mode>false</test_mode>
    <version>13.0.3</version>
    <output_file>dependencies.png</output_file>
    <ascii_tree>true</ascii_tree>
</config>
"""


class TestConfig(unittest.TestCase):
    """Проверить загрузку конфигурации."""

    def make_config(self, content):
        """Создать временный XML-файл."""
        temp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".xml",
            delete=False,
            encoding="utf-8"
        )
        temp.write(content)
        temp.close()
        return Path(temp.name)

    def load_temp(self, content):
        """Загрузить временную конфигурацию."""
        path = self.make_config(content)

        try:
            return load_config(path)
        finally:
            path.unlink(missing_ok=True)

    def test_valid_config(self):
        """Проверить корректную конфигурацию."""
        config = self.load_temp(VALID_XML)

        self.assertEqual(config.package, "Newtonsoft.Json")
        self.assertEqual(config.version, "13.0.3")
        self.assertFalse(config.test_mode)
        self.assertTrue(config.ascii_tree)
        self.assertEqual(
            config.output_file,
            "dependencies.png"
        )

    def test_missing_file(self):
        """Проверить отсутствующий файл."""
        with self.assertRaises(ValueError):
            load_config("missing_config.xml")

    def test_invalid_xml(self):
        """Проверить повреждённый XML."""
        content = "<config><package>Test</config>"

        with self.assertRaises(ValueError):
            self.load_temp(content)

    def test_missing_package(self):
        """Проверить отсутствующее имя пакета."""
        content = VALID_XML.replace(
            "<package>Newtonsoft.Json</package>",
            ""
        )

        with self.assertRaises(ValueError):
            self.load_temp(content)

    def test_empty_version(self):
        """Проверить пустую версию."""
        content = VALID_XML.replace(
            "<version>13.0.3</version>",
            "<version></version>"
        )

        with self.assertRaises(ValueError):
            self.load_temp(content)

    def test_invalid_repository(self):
        """Проверить неправильный URL."""
        content = VALID_XML.replace(
            "https://api.nuget.org/v3/index.json",
            "wrong_repository"
        )

        with self.assertRaises(ValueError):
            self.load_temp(content)

    def test_invalid_test_mode(self):
        """Проверить неправильный test_mode."""
        content = VALID_XML.replace(
            "<test_mode>false</test_mode>",
            "<test_mode>maybe</test_mode>"
        )

        with self.assertRaises(ValueError):
            self.load_temp(content)

    def test_invalid_ascii_tree(self):
        """Проверить неправильный ascii_tree."""
        content = VALID_XML.replace(
            "<ascii_tree>true</ascii_tree>",
            "<ascii_tree>maybe</ascii_tree>"
        )

        with self.assertRaises(ValueError):
            self.load_temp(content)

    def test_invalid_output_file(self):
        """Проверить расширение выходного файла."""
        content = VALID_XML.replace(
            "dependencies.png",
            "dependencies.txt"
        )

        with self.assertRaises(ValueError):
            self.load_temp(content)

    def test_missing_test_repository(self):
        """Проверить отсутствующий тестовый репозиторий."""
        content = VALID_XML.replace(
            "<test_mode>false</test_mode>",
            "<test_mode>true</test_mode>"
        ).replace(
            "https://api.nuget.org/v3/index.json",
            "missing_repository.txt"
        )

        with self.assertRaises(ValueError):
            self.load_temp(content)

if __name__ == "__main__":
    unittest.main()