"""Чтение и проверка XML-конфигурации."""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as etree


TRUE_VALUES = {"true", "1", "yes"}
FALSE_VALUES = {"false", "0", "no"}


@dataclass
class Config:
    """Настройки анализатора зависимостей."""

    package: str
    repository: str
    test_mode: bool
    version: str
    output_file: str
    ascii_tree: bool


def get_text(root, name):
    """Получить обязательное текстовое значение XML."""
    element = root.find(name)

    if element is None or element.text is None:
        raise ValueError(f"Отсутствует параметр: {name}")

    value = element.text.strip()

    if not value:
        raise ValueError(f"Пустой параметр: {name}")

    return value


def parse_bool(value, name):
    """Преобразовать текстовое значение в bool."""
    normalized = value.lower()

    if normalized in TRUE_VALUES:
        return True

    if normalized in FALSE_VALUES:
        return False

    raise ValueError(
        f"Параметр {name} должен быть true или false"
    )


def validate_repository(repository, test_mode):
    """Проверить адрес или путь тестового репозитория."""
    if test_mode:
        if not Path(repository).is_file():
            raise ValueError(
                "Файл тестового репозитория не найден"
            )
        return

    parsed = urlparse(repository)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Некорректный URL репозитория")

    if not parsed.netloc:
        raise ValueError("Некорректный URL репозитория")


def validate_output_file(output_file):
    """Проверить имя выходного изображения."""
    if not output_file.lower().endswith(".png"):
        raise ValueError(
            "Имя выходного файла должно оканчиваться на .png"
        )


def load_config(path):
    """Загрузить и проверить XML-конфигурацию."""
    try:
        root = etree.parse(path).getroot()
    except FileNotFoundError as error:
        raise ValueError(
            f"Файл конфигурации не найден: {path}"
        ) from error
    except etree.ParseError as error:
        raise ValueError(
            "Ошибка формата XML"
        ) from error

    package = get_text(root, "package")
    repository = get_text(root, "repository")
    test_mode = parse_bool(
        get_text(root, "test_mode"),
        "test_mode"
    )
    version = get_text(root, "version")
    output_file = get_text(root, "output_file")
    ascii_tree = parse_bool(
        get_text(root, "ascii_tree"),
        "ascii_tree"
    )

    validate_repository(repository, test_mode)
    validate_output_file(output_file)

    return Config(
        package=package,
        repository=repository,
        test_mode=test_mode,
        version=version,
        output_file=output_file,
        ascii_tree=ascii_tree,
    )