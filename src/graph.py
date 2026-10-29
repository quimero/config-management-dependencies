"""Построение графа зависимостей алгоритмом DFS."""


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
