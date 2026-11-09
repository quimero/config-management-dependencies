"""Построение и обход графа зависимостей."""


def dfs(package, dependency_provider, graph, visited):
    """Рекурсивно обойти зависимости пакета."""
    if package in visited:
        return

    visited.add(package)
    dependencies = dependency_provider(package)
    graph[package] = list(dependencies)

    for dependency in dependencies:
        dfs(
            dependency,
            dependency_provider,
            graph,
            visited,
        )


def build_dependency_graph(
    start_package,
    dependency_provider,
):
    """Построить полный граф зависимостей."""
    graph = {}
    visited = set()

    dfs(
        start_package,
        dependency_provider,
        graph,
        visited,
    )
    return graph


def reverse_graph(graph):
    """Развернуть направления всех рёбер графа."""
    reversed_graph = {
        package: []
        for package in graph
    }

    for package, dependencies in graph.items():
        for dependency in dependencies:
            reversed_graph.setdefault(
                dependency,
                [],
            )
            reversed_graph[dependency].append(package)

    return reversed_graph


def build_reverse_dependency_graph(graph, target):
    """Построить граф обратных зависимостей."""
    if target not in graph:
        raise ValueError(
            f"Узел отсутствует в графе: {target}"
        )

    reversed_graph = reverse_graph(graph)

    def provider(package):
        """Получить обратные зависимости узла."""
        return reversed_graph.get(
            package,
            [],
        )

    return build_dependency_graph(
        target,
        provider,
    )