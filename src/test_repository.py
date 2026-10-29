"""Работа с локальным тестовым репозиторием."""

import json
from pathlib import Path
import re


PACKAGE_PATTERN = re.compile(r"^[A-Z]$")


def validate_package_name(package):
    """Проверить имя тестового пакета."""
    if not isinstance(package, str):
        raise ValueError(
            "Имя тестового пакета должно быть строкой"
        )

    if not PACKAGE_PATTERN.fullmatch(package):
        raise ValueError(
            "Пакеты должны называться буквами A-Z"
        )


def validate_version(version):
    """Проверить версию тестового пакета."""
    if not isinstance(version, str):
        raise ValueError(
            "Версия пакета должна быть строкой"
        )

    if not version.strip():
        raise ValueError(
            "Версия пакета не должна быть пустой"
        )


def make_test_node(package, version):
    """Сформировать узел тестового графа."""
    validate_package_name(package)
    validate_version(version)
    return f"{package}@{version}"


def split_test_node(node):
    """Разделить тестовый узел на пакет и версию."""
    if not isinstance(node, str):
        raise ValueError(
            "Узел тестового графа должен быть строкой"
        )

    if "@" not in node:
        raise ValueError(
            f"Некорректный узел тестового графа: {node}"
        )

    package, version = node.rsplit("@", 1)
    validate_package_name(package)
    validate_version(version)
    return package, version


def validate_dependencies(dependencies):
    """Проверить список зависимостей пакета."""
    if not isinstance(dependencies, list):
        raise ValueError(
            "Зависимости должны быть списком"
        )

    for node in dependencies:
        split_test_node(node)


def validate_versions(versions):
    """Проверить версии тестового пакета."""
    if not isinstance(versions, dict):
        raise ValueError(
            "Версии пакета должны быть объектом JSON"
        )

    for version, dependencies in versions.items():
        validate_version(version)
        validate_dependencies(dependencies)


def validate_references(repository):
    """Проверить ссылки на пакеты и версии."""
    for versions in repository.values():
        for dependencies in versions.values():
            for node in dependencies:
                package, version = split_test_node(node)

                if package not in repository:
                    raise ValueError(
                        f"Зависимость не найдена: {package}"
                    )

                if version not in repository[package]:
                    raise ValueError(
                        "Версия зависимости не найдена: "
                        f"{package} {version}"
                    )


def validate_repository(repository):
    """Проверить структуру тестового репозитория."""
    if not isinstance(repository, dict):
        raise ValueError(
            "Тестовый репозиторий должен быть объектом JSON"
        )

    for package, versions in repository.items():
        validate_package_name(package)
        validate_versions(versions)

    validate_references(repository)


def load_test_repository(path):
    """Загрузить тестовый репозиторий."""
    try:
        text = Path(path).read_text(
            encoding="utf-8"
        )
        repository = json.loads(text)
    except FileNotFoundError as error:
        raise ValueError(
            f"Тестовый репозиторий не найден: {path}"
        ) from error
    except json.JSONDecodeError as error:
        raise ValueError(
            "Некорректный JSON тестового репозитория"
        ) from error

    validate_repository(repository)
    return repository


def get_test_dependencies(repository, node):
    """Получить зависимости тестового пакета."""
    package, version = split_test_node(node)

    if package not in repository:
        raise ValueError(
            f"Пакет отсутствует в репозитории: {package}"
        )

    if version not in repository[package]:
        raise ValueError(
            f"Версия пакета не найдена: {package} {version}"
        )

    return repository[package][version]