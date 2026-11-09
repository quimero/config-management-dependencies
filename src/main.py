"""Точка входа приложения."""

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
from src.visualization import (
    build_ascii_tree,
    graph_to_d2,
    render_d2,
    save_d2_source,
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
    return parser.parse_args()


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


def get_graph_root(graph):
    """Получить корневой узел графа."""
    if not graph:
        raise ValueError(
            "Граф зависимостей пуст"
        )

    return next(iter(graph))


def visualize_graph(graph, config):
    """Создать представления графа."""
    d2_text = graph_to_d2(graph)
    source_file = save_d2_source(
        d2_text,
        config.output_file,
    )
    render_d2(
        source_file,
        config.output_file,
    )

    print(f"D2-файл: {source_file}")
    print(f"PNG-файл: {config.output_file}")

    if config.ascii_tree:
        root = get_graph_root(graph)
        print("ASCII-дерево:")
        print(
            build_ascii_tree(
                graph,
                root,
            )
        )


def run(config):
    """Запустить приложение."""
    graph = build_graph(config)
    visualize_graph(
        graph,
        config,
    )


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