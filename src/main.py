"""Точка входа приложения."""

import argparse

from src.config import load_config
from src.graph import (
    build_dependency_graph,
    build_reverse_dependency_graph,
)
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
    """Получить аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Анализатор зависимостей NuGet"
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help="Путь к XML-конфигурации",
    )
    parser.add_argument(
        "--reverse",
        help="Узел для поиска обратных зависимостей",
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


def print_reverse_dependencies(graph, target):
    """Вывести найденные обратные зависимости."""
    print(
        f"Обратные зависимости для {target}:"
    )

    dependencies = [
        package
        for package in graph
        if package != target
    ]

    if not dependencies:
        print("-")
        return

    for package in dependencies:
        print(package)


def build_test_graph(config):
    """Построить граф тестового репозитория."""
    repository = load_test_repository(
        config.repository
    )
    start_node = make_test_node(
        config.package,
        config.version,
    )

    def provider(node):
        """Получить зависимости тестового узла."""
        return get_test_dependencies(
            repository,
            node,
        )

    return build_dependency_graph(
        start_node,
        provider,
    )


def build_nuget_graph(config):
    """Построить граф настоящего NuGet."""
    start_node = make_nuget_node(
        config.package,
        config.version,
    )

    def provider(node):
        """Получить зависимости NuGet-узла."""
        return get_nuget_dependency_nodes(
            config.repository,
            node,
        )

    return build_dependency_graph(
        start_node,
        provider,
    )


def build_graph(config):
    """Построить граф для выбранного режима."""
    if config.test_mode:
        return build_test_graph(config)

    return build_nuget_graph(config)


def run(config, reverse_target=None):
    """Запустить приложение."""
    graph = build_graph(config)

    if reverse_target is None:
        print_graph(graph)
        return

    reverse_dependencies = (
        build_reverse_dependency_graph(
            graph,
            reverse_target,
        )
    )
    print_reverse_dependencies(
        reverse_dependencies,
        reverse_target,
    )


def main():
    """Запустить приложение."""
    args = parse_args()

    try:
        config = load_config(args.config)
        run(
            config,
            args.reverse,
        )
    except ValueError as error:
        print(f"Ошибка: {error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())