from . import (
    auth_route,
    user_public_route,
    user_protected_route,
    kid_route,
    keyword_restriction_route
)

"""
add your protected route here
"""
PROTECTED_ROUTES = [
    user_protected_route.router,
    kid_route.router,
    keyword_restriction_route.router
]


"""
add your public route here
"""
PUBLIC_ROUTES = [
    auth_route.router,
    user_public_route.router
]
