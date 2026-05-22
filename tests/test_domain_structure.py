import importlib


def test_domain_packages_are_importable():
    modules = [
        "app.core",
        "app.domains",
        "app.domains.auth",
        "app.domains.learning",
        "app.domains.agent",
        "app.domains.rag",
    ]

    for module_name in modules:
        assert importlib.import_module(module_name)
