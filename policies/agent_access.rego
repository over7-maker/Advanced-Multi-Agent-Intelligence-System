# Agent Access Control Policy for AMAS
# Defines who can access which agents and under what conditions

package agent.access

import rego.v1

# Default deny
default allow := false

# Allow access if user has required role for the agent
allow if {
    input.user_id
    input.agent_id
    input.action in {"create", "read", "update", "delete", "execute"}
    
    # Get user roles from data
    user_data := data.users[input.user_id]
    user_roles := user_data.roles
    
    # Get required roles for the agent and action
    agent_data := data.agents[input.agent_id]
    required_roles := agent_data.required_roles[input.action]
    
    # Check if user has any of the required roles
    intersection := user_roles & required_roles
    count(intersection) > 0
}

# Allow read access for public agents
allow if {
    input.action == "read"
    input.agent_id
    data.agents[input.agent_id].public == true
}

# Allow access for admin users
allow if {
    input.user_id
    user_data := data.users[input.user_id]
    "admin" in user_data.roles
}

# Allow access during business hours for standard users
allow if {
    input.user_id
    input.agent_id
    input.action in {"read", "execute"}
    
    # Check if it's business hours
    now_hour := time.clock(time.now_ns())[0]
    now_hour >= 9
    now_hour <= 17
    
    # Check if user has standard access
    user_data := data.users[input.user_id]
    "standard_user" in user_data.roles
    
    # Check if agent allows standard access
    agent_data := data.agents[input.agent_id]
    agent_data.allow_standard_access == true
}

# Deny access during maintenance windows
allow if {
    not maintenance_active
}

maintenance_active if {
    maintenance := data.system.maintenance
    maintenance.active == true
    
    now := time.now_ns()
    now >= maintenance.start_time
    now <= maintenance.end_time
}

# Deny access if user is suspended
allow if {
    input.user_id
    user_data := data.users[input.user_id]
    user_data.status != "suspended"
}

# Deny access if agent is disabled
allow if {
    input.agent_id
    agent_data := data.agents[input.agent_id]
    agent_data.status != "disabled"
}

# Rate limiting check
allow if {
    input.user_id
    input.agent_id
    
    # Get rate limit data
    rate_limit_key := sprintf("%s:%s", [input.user_id, input.agent_id])
    rate_data := data.rate_limits[rate_limit_key]
    
    # Check if within rate limit
    now := time.now_ns()
    window_start := now - (60 * 1000000000)  # 60 seconds in nanoseconds
    
    recent_requests := [req | req := rate_data.requests[_]; req.timestamp >= window_start]
    count(recent_requests) < rate_data.limit_per_minute
}

# Provide denial reason
denial_reason := reason if {
    not allow
    
    # Check various denial conditions
    input.user_id
    input.agent_id
    
    user_data := data.users[input.user_id]
    agent_data := data.agents[input.agent_id]
    
    user_data.status == "suspended"
    reason := "User account is suspended"
} else := reason if {
    not allow
    input.agent_id
    agent_data := data.agents[input.agent_id]
    agent_data.status == "disabled"
    reason := "Agent is currently disabled"
} else := reason if {
    not allow
    maintenance_active
    reason := "System is under maintenance"
} else := reason if {
    not allow
    reason := "Insufficient permissions"
}

# Return structured result
result := {
    "allow": allow,
    "reason": denial_reason,
    "metadata": {
        "policy": "agent.access",
        "evaluated_at": time.now_ns(),
        "user_id": input.user_id,
        "agent_id": input.agent_id,
        "action": input.action
    }
}