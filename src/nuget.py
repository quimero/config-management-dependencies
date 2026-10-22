"""Получение зависимостей пакетов через NuGet V3 API."""

from dataclasses import dataclass
import gzip
import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


HTTP_TIMEOUT = 15
ANY_VERSION_RANGE = "(, )"
REGISTRATION_TYPES = (
    "RegistrationsBaseUrl/3.6.0",
    "RegistrationsBaseUrl",
)


@dataclass(frozen=True)
class Dependency:
    """Прямая зависимость NuGet-пакета."""

    package: str
    version_range: str
    framework: str


def fetch_json(url):
    """Получить JSON по указанному URL."""
    request = Request(
        url,
        headers={
            "User-Agent": "config-management-dependencies"
        }
    )

    try:
        with urlopen(
            request,
            timeout=HTTP_TIMEOUT
        ) as response:
            content = response.read()
            encoding = response.headers.get(
                "Content-Encoding"
            )
    except (HTTPError, URLError, TimeoutError) as error:
        raise ValueError(
            f"Ошибка запроса к NuGet: {error}"
        ) from error

    if encoding == "gzip":
        content = gzip.decompress(content)

    try:
        return json.loads(content.decode("utf-8"))
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        OSError,
    ) as error:
        raise ValueError(
            "Некорректный ответ NuGet API"
        ) from error


def find_registration_base(service_index):
    """Найти URL ресурса metadata NuGet."""
    resources = service_index.get("resources", [])

    for resource_type in REGISTRATION_TYPES:
        for resource in resources:
            if resource.get("@type") == resource_type:
                return resource.get("@id")

    raise ValueError(
        "NuGet-репозиторий не содержит Registration API"
    )


def make_registration_url(base_url, package):
    """Сформировать URL metadata пакета."""
    package_id = quote(
        package.lower(),
        safe=""
    )

    return (
        f"{base_url.rstrip('/')}/"
        f"{package_id}/index.json"
    )


def get_page_items(page):
    """Получить версии пакета со страницы metadata."""
    items = page.get("items")

    if items is not None:
        return items

    page_url = page.get("@id")

    if not page_url:
        raise ValueError(
            "Некорректная страница NuGet metadata"
        )

    page_data = fetch_json(page_url)
    return page_data.get("items", [])


def find_catalog_entry(index_data, version):
    """Найти metadata указанной версии пакета."""
    for page in index_data.get("items", []):
        for leaf in get_page_items(page):
            catalog = leaf.get("catalogEntry", {})

            if not isinstance(catalog, dict):
                continue

            catalog_version = catalog.get(
                "version",
                ""
            )

            if catalog_version.lower() == version.lower():
                return catalog

    raise ValueError(
        f"Версия пакета не найдена: {version}"
    )


def extract_dependencies(catalog):
    """Извлечь прямые зависимости из metadata."""
    result = []

    for group in catalog.get("dependencyGroups", []):
        framework = group.get(
            "targetFramework"
        ) or "any"

        for item in group.get("dependencies", []):
            package = item.get("id")

            if not package:
                continue

            version_range = item.get(
                "range"
            ) or ANY_VERSION_RANGE

            result.append(
                Dependency(
                    package=package,
                    version_range=version_range,
                    framework=framework,
                )
            )

    result.sort(
        key=lambda item: (
            item.framework.lower(),
            item.package.lower(),
        )
    )
    return result


def get_direct_dependencies(
    repository,
    package,
    version,
):
    """Получить прямые зависимости пакета."""
    service_index = fetch_json(repository)
    base_url = find_registration_base(
        service_index
    )
    registration_url = make_registration_url(
        base_url,
        package
    )
    index_data = fetch_json(registration_url)
    catalog = find_catalog_entry(
        index_data,
        version
    )
    return extract_dependencies(catalog)