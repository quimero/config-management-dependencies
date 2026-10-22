"""Точка входа анализатора зависимостей."""

import argparse

from src.config import load_config
from src.nuget import get_direct_dependencies


DEFAULT_CONFIG = "config.xml"


def parse_args():
    """Получить параметры запуска приложения."""
    parser = argparse.ArgumentParser(
        description="NuGet dependency graph visualizer"
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help="Path to XML configuration file"
    )
    return parser.parse_args()


def print_dependencies(
    package,
    version,
    dependencies,
):
    """Вывести прямые зависимости пакета."""
    print(
        f"Прямые зависимости "
        f"{package} {version}:"
    )

    if not dependencies:
        print("Зависимости отсутствуют")
        return

    for dependency in dependencies:
        print(
            f"- {dependency.package} "
            f"{dependency.version_range} "
            f"[{dependency.framework}]"
        )


def load_dependencies(config):
    """Получить зависимости по конфигурации."""
    if config.test_mode:
        raise ValueError(
            "Тестовый режим будет реализован "
            "на этапе 3"
        )

    return get_direct_dependencies(
        config.repository,
        config.package,
        config.version,
    )


def main():
    """Запустить приложение."""
    args = parse_args()

    try:
        config = load_config(args.config)
        dependencies = load_dependencies(config)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return 1

    print_dependencies(
        config.package,
        config.version,
        dependencies,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())