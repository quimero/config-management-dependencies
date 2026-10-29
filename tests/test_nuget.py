"""Тесты получения зависимостей NuGet."""

import unittest
from unittest.mock import patch

from src.nuget import (
    ANY_VERSION_RANGE,
    Dependency,
    extract_dependencies,
    find_catalog_entry,
    find_registration_base,
    get_direct_dependencies,
    get_minimum_version,
    get_nuget_dependency_nodes,
    make_dependency_nodes,
    make_nuget_node,
    make_registration_url,
    split_nuget_node,
)


SERVICE_INDEX = {
    "resources": [
        {
            "@id": "https://example.test/registration/",
            "@type": "RegistrationsBaseUrl/3.6.0",
        }
    ]
}

CATALOG_ENTRY = {
    "version": "1.0.0",
    "dependencyGroups": [
        {
            "targetFramework": ".NETStandard2.0",
            "dependencies": [
                {
                    "id": "Package.A",
                    "range": "[1.0.0, 2.0.0)",
                },
                {
                    "id": "Package.B",
                },
            ],
        }
    ],
}

REGISTRATION_INDEX = {
    "items": [
        {
            "items": [
                {
                    "catalogEntry": CATALOG_ENTRY,
                }
            ]
        }
    ]
}


class TestNuget(unittest.TestCase):
    """Проверить получение зависимостей NuGet."""

    def test_find_registration_base(self):
        """Найти Registration API."""
        result = find_registration_base(
            SERVICE_INDEX
        )

        self.assertEqual(
            result,
            "https://example.test/registration/"
        )

    def test_missing_registration_base(self):
        """Проверить отсутствие Registration API."""
        with self.assertRaises(ValueError):
            find_registration_base(
                {"resources": []}
            )

    def test_make_registration_url(self):
        """Проверить формирование URL пакета."""
        result = make_registration_url(
            "https://example.test/registration/",
            "Test.Package"
        )

        self.assertEqual(
            result,
            "https://example.test/registration/"
            "test.package/index.json"
        )

    def test_extract_dependencies(self):
        """Извлечь прямые зависимости."""
        dependencies = extract_dependencies(
            CATALOG_ENTRY
        )

        self.assertEqual(
            dependencies[0].package,
            "Package.A"
        )
        self.assertEqual(
            dependencies[0].version_range,
            "[1.0.0, 2.0.0)"
        )
        self.assertEqual(
            dependencies[1].package,
            "Package.B"
        )
        self.assertEqual(
            dependencies[1].version_range,
            ANY_VERSION_RANGE
        )

    def test_empty_dependencies(self):
        """Проверить пакет без зависимостей."""
        catalog = {
            "version": "1.0.0"
        }

        dependencies = extract_dependencies(
            catalog
        )

        self.assertEqual(dependencies, [])

    def test_find_catalog_entry(self):
        """Найти metadata нужной версии."""
        catalog = find_catalog_entry(
            REGISTRATION_INDEX,
            "1.0.0"
        )

        self.assertEqual(
            catalog["version"],
            "1.0.0"
        )

    def test_missing_version(self):
        """Проверить отсутствующую версию."""
        with self.assertRaises(ValueError):
            find_catalog_entry(
                REGISTRATION_INDEX,
                "9.9.9"
            )

    @patch("src.nuget.fetch_json")
    def test_external_page(self, mock_fetch):
        """Проверить отдельную страницу metadata."""
        index_data = {
            "items": [
                {
                    "@id": "https://example.test/page.json"
                }
            ]
        }
        mock_fetch.return_value = {
            "items": [
                {
                    "catalogEntry": CATALOG_ENTRY
                }
            ]
        }

        catalog = find_catalog_entry(
            index_data,
            "1.0.0"
        )

        self.assertEqual(
            catalog["version"],
            "1.0.0"
        )

    @patch("src.nuget.fetch_json")
    def test_direct_dependencies(self, mock_fetch):
        """Проверить полный процесс получения."""
        mock_fetch.side_effect = [
            SERVICE_INDEX,
            REGISTRATION_INDEX,
        ]

        dependencies = get_direct_dependencies(
            "https://example.test/v3/index.json",
            "Test.Package",
            "1.0.0",
        )

        self.assertEqual(
            dependencies[0].package,
            "Package.A"
        )
        self.assertEqual(
            dependencies[1].package,
            "Package.B"
        )

    def test_minimum_version(self):
        """Получить минимальную версию."""
        self.assertEqual(
            get_minimum_version("[4.3.0, )"),
            "4.3.0"
        )

    def test_exact_version(self):
        """Получить точную версию."""
        self.assertEqual(
            get_minimum_version("[2.0.0]"),
            "2.0.0"
        )

    def test_nuget_node(self):
        """Создать и разобрать узел NuGet."""
        node = make_nuget_node(
            "Test.Package",
            "1.0.0"
        )

        self.assertEqual(
            node,
            "Test.Package@1.0.0"
        )
        self.assertEqual(
            split_nuget_node(node),
            ("Test.Package", "1.0.0")
        )

    def test_dependency_nodes(self):
        """Преобразовать зависимости в узлы."""
        dependencies = [
            Dependency(
                package="Package.A",
                version_range="[1.0.0, )",
                framework="net6.0",
            ),
            Dependency(
                package="Package.A",
                version_range="[1.0.0, )",
                framework="net7.0",
            ),
        ]

        nodes = make_dependency_nodes(
            dependencies
        )

        self.assertEqual(
            nodes,
            ["Package.A@1.0.0"]
        )

    @patch("src.nuget.get_direct_dependencies")
    def test_nuget_dependency_nodes(
        self,
        mock_dependencies,
    ):
        """Получить дочерние узлы NuGet."""
        mock_dependencies.return_value = [
            Dependency(
                package="Package.A",
                version_range="[1.2.0, )",
                framework="net6.0",
            )
        ]

        nodes = get_nuget_dependency_nodes(
            "https://example.test/index.json",
            "Root.Package@2.0.0",
        )

        self.assertEqual(
            nodes,
            ["Package.A@1.2.0"],
        )

        mock_dependencies.assert_called_once_with(
            "https://example.test/index.json",
            "Root.Package",
            "2.0.0",
        )

if __name__ == "__main__":
    unittest.main()