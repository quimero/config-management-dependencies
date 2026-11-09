"""Визуализация графа зависимостей."""

import subprocess
from pathlib import Path


D2_COMMAND = "d2"
D2_SCALE = "0.5"
SUCCESS_CODE = 0


def escape_d2(text):
    """Экранировать специальный текст для D2."""
    return text.replace(
        "\\",
        "\\\\",
    ).replace(
        '"',
        '\\"',
    )


def quote_d2(text):
    """Заключить имя узла в кавычки D2."""
    return f'"{escape_d2(text)}"'


def graph_to_d2(graph):
    """Преобразовать граф в текст D2."""
    lines = ["direction: right"]
    connected = set()

    for package, dependencies in graph.items():
        for dependency in dependencies:
            source = quote_d2(package)
            target = quote_d2(dependency)
            lines.append(f"{source} -> {target}")
            connected.add(package)
            connected.add(dependency)

    for package in graph:
        if package not in connected:
            lines.append(quote_d2(package))

    return "\n".join(lines) + "\n"


def save_d2_source(d2_text, output_file):
    """Сохранить текстовое представление D2."""
    output_path = Path(output_file)
    source_path = output_path.with_suffix(".d2")
    source_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    source_path.write_text(
        d2_text,
        encoding="utf-8",
    )
    return source_path


def render_d2(source_file, output_file):
    """Создать PNG при помощи D2 CLI."""
    try:
        result = subprocess.run(
            [
                D2_COMMAND,
                "--scale",
                D2_SCALE,
                str(source_file),
                str(output_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise ValueError(
            "D2 CLI не найден"
        ) from error

    if result.returncode != SUCCESS_CODE:
        message = (
            result.stderr.strip()
            or "неизвестная ошибка D2"
        )
        raise ValueError(
            f"Ошибка D2: {message}"
        )


def append_ascii_children(
    graph,
    node,
    prefix,
    path,
    lines,
):
    """Добавить дочерние узлы ASCII-дерева."""
    children = graph.get(node, [])
    current_path = path | {node}
    last_index = len(children) - 1

    for index, child in enumerate(children):
        is_last = index == last_index
        connector = "└── " if is_last else "├── "
        suffix = (
            " [cycle]"
            if child in current_path
            else ""
        )
        lines.append(
            f"{prefix}{connector}{child}{suffix}"
        )

        if child in current_path:
            continue

        next_prefix = prefix + (
            "    "
            if is_last
            else "│   "
        )
        append_ascii_children(
            graph,
            child,
            next_prefix,
            current_path,
            lines,
        )


def build_ascii_tree(graph, root):
    """Построить ASCII-дерево зависимостей."""
    if root not in graph:
        raise ValueError(
            f"Узел отсутствует в графе: {root}"
        )

    lines = [root]
    append_ascii_children(
        graph,
        root,
        "",
        set(),
        lines,
    )
    return "\n".join(lines)