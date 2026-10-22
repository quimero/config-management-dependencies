"""Точка входа анализатора зависимостей."""

import argparse

from src.config import load_config


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


def print_config(config):
    """Вывести настройки в формате ключ-значение."""
    print(f"package={config.package}")
    print(f"repository={config.repository}")
    print(f"test_mode={config.test_mode}")
    print(f"version={config.version}")
    print(f"output_file={config.output_file}")
    print(f"ascii_tree={config.ascii_tree}")


def main():
    """Запустить приложение."""
    args = parse_args()

    try:
        config = load_config(args.config)
    except ValueError as error:
        print(f"Ошибка конфигурации: {error}")
        return 1

    print_config(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())