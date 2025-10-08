"""Audit module for AMAS"""

class AuditLogger:
    """Simple audit logger"""

    def log(self, message: str) -> None:
        """Log audit message"""
        print(f"AUDIT: {message}")
