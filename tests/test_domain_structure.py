import importlib


def test_domain_packages_are_importable():
    modules = [
        "app.common.security",
        "app.domains",
        "app.domains.admin",
        "app.domains.admin.indexing_service",
        "app.domains.admin.router",
        "app.domains.auth",
        "app.domains.auth.models",
        "app.domains.auth.repository",
        "app.domains.auth.router",
        "app.domains.auth.schemas",
        "app.domains.auth.service",
        "app.domains.chat",
        "app.domains.chat.router",
        "app.domains.chat.schemas",
        "app.domains.chat.service",
        "app.domains.learning",
        "app.domains.learning.content_router",
        "app.domains.learning.models",
        "app.domains.learning.repository",
        "app.domains.learning.router",
        "app.domains.learning.schemas",
        "app.domains.learning.service",
        "app.domains.agent",
        "app.domains.agent.router",
        "app.domains.agent.schemas",
        "app.domains.rag",
        "app.domains.rag.retriever",
        "app.domains.rag.schemas",
        "app.domains.rag.service",
        "app.domains.stage3",
        "app.domains.stage3.router",
        "app.domains.stage3.schemas",
        "app.domains.stage3.service",
    ]

    for module_name in modules:
        assert importlib.import_module(module_name)
