"""Точка входа анализатора зависимостей."""

import argparse

from src.config import load_config
from src.graph import build_dependency_graph
from src.nuget import (
    get_nuget_dependency_nodes,
    make_nuget_node,
)
from src.test_repository import (
    get_test_dependencies,
    load_test_repository,
    make_test_node,
)


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


def print_graph(graph):
    """Вывести граф зависимостей."""
    print("Граф зависимостей:")

    for package, dependencies in graph.items():
        if dependencies:
            text = ", ".join(dependencies)
        else:
            text = "-"

        print(f"{package} -> {text}")


def run_test_mode(config):
    """Запустить работу с тестовым репозиторием."""
    repository = load_test_repository(
        config.repository
    )
    start_node = make_test_node(
        config.package,
        config.version,
    )

    def provider(node):
        return get_test_dependencies(
            repository,
            node,
        )

    graph = build_dependency_graph(
        start_node,
        provider,
    )
    print_graph(graph)


def run_nuget_mode(config):
    """Построить полный граф зависимостей NuGet."""
    start_node = make_nuget_node(
        config.package,
        config.version,
    )

    def provider(node):
        return get_nuget_dependency_nodes(
            config.repository,
            node,
        )

    graph = build_dependency_graph(
        start_node,
        provider,
    )
    print_graph(graph)


def run(config):
    """Запустить выбранный режим работы."""
    if config.test_mode:
        run_test_mode(config)
        return

    run_nuget_mode(config)


def main():
    """Запустить приложение."""
    args = parse_args()

    try:
        config = load_config(args.config)
        run(config)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())