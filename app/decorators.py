"""Role-based access control (RBAC) helper.

Use @role_required("manager", "owner") on a route to restrict who can open it.
"""
from functools import wraps

from flask import abort, redirect, url_for, request
from flask_login import current_user


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                # Not logged in -> send to login, then back to this page.
                return redirect(url_for("auth.login", next=request.path))
            if current_user.role not in roles:
                abort(403)  # logged in but not allowed
            return view(*args, **kwargs)
        return wrapped
    return decorator
