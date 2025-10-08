"""Authorization module for AMAS"""


class AuthorizationManager:
    """Simple authorization manager"""

    def authorize(self, user: str, action: str) -> bool:
        """Authorize user action"""
        return True
