from . import (
    auth_route,
    user_public_route,
    user_protected_route
)

"""
add your protected route here
"""
PROTECTED_ROUTES = [
    user_protected_route.router
]


"""
add your public route here
"""
PUBLIC_ROUTES = [
    auth_route.router,
    user_public_route.router
]
