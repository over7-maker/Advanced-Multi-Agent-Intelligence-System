from prometheus_client import Counter, Gauge, Histogram


class EnterpriseMetrics:
    def __init__(self) -> None:
        # Business metrics
        self.user_sessions = Gauge("amas_active_user_sessions", "Active user sessions")
        self.agent_executions = Counter(
            "amas_agent_executions_total", "Agent executions", ["agent_type", "status"]
        )
        self.enterprise_requests = Counter(
            "amas_enterprise_requests_total",
            "Enterprise requests",
            ["auth_method", "user_role"],
        )

        # Security metrics
        self.failed_auth_attempts = Counter(
            "amas_failed_auth_attempts_total", "Failed auth attempts", ["method", "user"]
        )
        self.security_events = Counter(
            "amas_security_events_total", "Security events", ["event_type", "severity"]
        )

        # Performance metrics
        self.db_pool_utilization = Gauge(
            "amas_db_pool_utilization_percent", "DB pool utilization"
        )
        self.cache_operation_duration = Histogram(
            "amas_cache_operation_duration_seconds", "Cache operation duration", ["operation"]
        )

    def record_user_login(self, auth_method: str, role: str) -> None:
        self.enterprise_requests.labels(auth_method=auth_method, user_role=role).inc()

    def record_security_event(self, event_type: str, severity: str) -> None:
        self.security_events.labels(event_type=event_type, severity=severity).inc()
