from app.domains.developer.router import router
from app.domains.auth.dependency.dependencies import get_current_developer


def test_admin_router_requires_developer_role():
    assert any(
        dependency.dependency is get_current_developer
        for dependency in router.dependencies
    )
