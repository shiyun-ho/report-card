from app.dependencies.auth import (
    SchoolIsolationDependency,
    get_current_user,
    get_current_user_optional,
    get_current_user_school_id,
    require_admin,
    require_form_teacher,
    require_role,
    require_school_isolation,
    require_school_isolation_admin_override,
    require_year_head,
    require_year_head_or_admin,
    verify_csrf_token,
)

__all__ = [
    "get_current_user",
    "get_current_user_optional",
    "get_current_user_school_id",
    "require_admin",
    "require_form_teacher",
    "require_role",
    "require_school_isolation",
    "require_school_isolation_admin_override",
    "require_year_head",
    "require_year_head_or_admin",
    "verify_csrf_token",
    "SchoolIsolationDependency",
]
