package amas.tool_access

# Default deny
default allow = false

# Allow tool access based on agent role and tool type
allow {
    input.agent_role == "code_reviewer"
    input.tool_name == "code_analyzer"
}

allow {
    input.agent_role == "security_auditor"
    input.tool_name == "vulnerability_scanner"
}

allow {
    input.agent_role == "security_auditor"
    input.tool_name == "code_analyzer"
}

allow {
    input.agent_role == "orchestrator"
    input.tool_name == "agent_dispatcher"
}

# Deny dangerous tools for non-admin roles
deny {
    input.tool_name == "system_executor"
    input.agent_role != "admin"
}

deny {
    input.tool_name == "database_migrator"
    input.agent_role != "admin"
    input.environment == "production"
}

# Allow escalation for risky actions with human approval
allow {
    input.tool_name == "dangerous_tool"
    input.has_human_approval == true
    input.approved_by != ""
}

# Rate limiting check
allow {
    input.tool_name == "rate_limited_tool"
    count(input.recent_calls) < input.rate_limit
}

# Check user permissions
allow {
    input.user_role == "admin"
}

allow {
    input.user_role == "developer"
    input.tool_name != "system_executor"
}
