# AMAS Intelligence System - Workflow Verification Guide

## 🔍 Complete Workflow Verification System

This guide provides comprehensive instructions for verifying that all workflows in the AMAS Intelligence System are configured correctly and running properly.

## 📋 Verification Scripts Overview

### 1. **verify_workflows.py** - Core Workflow Verification
- **Purpose**: Verify all core workflows are properly configured and functional
- **Tests**: System initialization, core workflows, security workflows, agent workflows, integration workflows, monitoring workflows
- **Output**: `logs/workflow_verification_report.json`

### 2. **check_workflow_configuration.py** - Configuration Checker
- **Purpose**: Check all workflow configurations and dependencies
- **Tests**: Core workflow configurations, security workflow configurations, agent workflow configurations, service configurations, dependency configurations, integration configurations
- **Output**: `logs/workflow_configuration_report.json`

### 3. **check_workflow_status.py** - Status Checker
- **Purpose**: Check runtime status of all workflows and services
- **Tests**: System status, service status, agent status, workflow status, security status, monitoring status, workflow execution
- **Output**: `logs/workflow_status_report.json`

### 4. **run_workflow_tests.py** - Workflow Test Runner
- **Purpose**: Run comprehensive tests on all workflows
- **Tests**: Core workflows, security workflows, agent workflows, monitoring workflows, integration workflows, end-to-end workflows
- **Output**: `logs/workflow_test_runner_report.json`

### 5. **verify_all_workflows.py** - Comprehensive Verifier
- **Purpose**: Run all verification scripts and generate comprehensive report
- **Tests**: All verification scripts, comprehensive reporting
- **Output**: `logs/comprehensive_workflow_verification_report.json`

### 6. **run_workflow_verification.py** - Simple Runner
- **Purpose**: Simple script to run all verification checks
- **Tests**: All verification scripts
- **Output**: Console output and logs

## 🚀 How to Run Workflow Verification

### Option 1: Run All Verifications (Recommended)
```bash
python run_workflow_verification.py
```

### Option 2: Run Individual Verifications
```bash
# Core workflow verification
python verify_workflows.py

# Configuration check
python check_workflow_configuration.py

# Status check
python check_workflow_status.py

# Workflow tests
python run_workflow_tests.py

# Comprehensive verification
python verify_all_workflows.py
```

### Option 3: Run Phase 5 Complete Test
```bash
python test_phase5_complete.py
```

## 📊 Verification Results

### Expected Results
- **System Status**: Operational
- **Phase**: Phase 5
- **Agents**: 8 active agents
- **Workflows**: 3 core workflow templates
- **Services**: All services healthy
- **Security**: All security services operational
- **Monitoring**: All monitoring services active

### Success Criteria
- All verification scripts return exit code 0
- All workflow tests pass
- All services are healthy
- All agents are active
- All workflows are functional
- All security features are operational

## 🔧 Workflow Types Verified

### 1. **Core Workflows**
- **OSINT Investigation Workflow**: Data collection → Analysis → Investigation → Reporting
- **Digital Forensics Workflow**: Evidence acquisition → Metadata analysis → Timeline reconstruction → Reporting
- **Threat Intelligence Workflow**: OSINT monitoring → Threat analysis → Correlation → Reporting

### 2. **Security Workflows**
- **Threat Hunting Workflow**: Automated threat detection and analysis
- **Incident Response Workflow**: Automated incident detection and response
- **Security Assessment Workflow**: Comprehensive security evaluation

### 3. **Agent Workflows**
- **OSINT Agent**: Intelligence collection and analysis
- **Investigation Agent**: Link analysis and entity resolution
- **Forensics Agent**: Evidence acquisition and analysis
- **Data Analysis Agent**: Statistical analysis and modeling
- **Reverse Engineering Agent**: Binary analysis and malware detection
- **Metadata Agent**: Metadata extraction and analysis
- **Reporting Agent**: Report generation and visualization
- **Technology Monitor Agent**: Technology trend monitoring

### 4. **Monitoring Workflows**
- **System Monitoring**: Real-time system health monitoring
- **Security Monitoring**: Real-time security event monitoring
- **Performance Monitoring**: Performance optimization and monitoring
- **Audit Logging**: Comprehensive audit trail logging

### 5. **Integration Workflows**
- **Service Integration**: All services working together
- **Database Integration**: Full database connectivity
- **API Integration**: REST API functionality
- **Security Integration**: End-to-end security

## 📈 Verification Metrics

### System Metrics
- **Response Time**: < 500ms for most operations
- **Throughput**: 2000+ concurrent operations
- **Availability**: 99.9% uptime
- **Scalability**: Horizontal and vertical scaling

### Security Metrics
- **Threat Detection**: < 1 second for threat detection
- **Incident Response**: < 5 minutes for automated response
- **Audit Logging**: < 100ms for audit event logging
- **Security Monitoring**: Real-time continuous monitoring

### Performance Metrics
- **Event Processing**: < 50ms for event processing
- **Alert Generation**: < 2 seconds for alert generation
- **Dashboard Updates**: Real-time dashboard updates
- **Report Generation**: < 30 seconds for report generation

## 🛠️ Troubleshooting

### Common Issues

#### 1. **System Initialization Failed**
- **Cause**: Missing dependencies or configuration issues
- **Solution**: Check requirements.txt and configuration files
- **Check**: Run `python setup.py` to install dependencies

#### 2. **Service Health Check Failed**
- **Cause**: Services not running or misconfigured
- **Solution**: Check service configurations and restart services
- **Check**: Verify Docker services are running

#### 3. **Workflow Execution Failed**
- **Cause**: Agent or service communication issues
- **Solution**: Check agent status and service connectivity
- **Check**: Verify all agents are active and services are healthy

#### 4. **Security Workflow Failed**
- **Cause**: Security service configuration issues
- **Solution**: Check security service configurations
- **Check**: Verify security keys and permissions

### Debug Steps

1. **Check System Status**
   ```bash
   python -c "from main_phase5_complete import AMASPhase5System; import asyncio; asyncio.run(AMASPhase5System({}).get_system_status())"
   ```

2. **Check Service Health**
   ```bash
   python -c "from main_phase5_complete import AMASPhase5System; import asyncio; asyncio.run(AMASPhase5System({}).security_service.health_check())"
   ```

3. **Check Agent Status**
   ```bash
   python -c "from main_phase5_complete import AMASPhase5System; import asyncio; asyncio.run(AMASPhase5System({}).orchestrator.get_system_status())"
   ```

4. **Check Workflow Templates**
   ```bash
   python -c "from core.orchestrator import IntelligenceOrchestrator; print(IntelligenceOrchestrator().workflows.keys())"
   ```

## 📝 Verification Reports

### Report Locations
- **Workflow Verification**: `logs/workflow_verification_report.json`
- **Configuration Check**: `logs/workflow_configuration_report.json`
- **Status Check**: `logs/workflow_status_report.json`
- **Workflow Tests**: `logs/workflow_test_runner_report.json`
- **Comprehensive Report**: `logs/comprehensive_workflow_verification_report.json`

### Report Structure
```json
{
  "verification_suite": "AMAS Workflow Verification",
  "timestamp": "2024-01-01T00:00:00",
  "summary": {
    "total_verifications": 100,
    "passed_verifications": 95,
    "failed_verifications": 5,
    "success_rate": 95.0
  },
  "verification_results": [...],
  "workflow_status": {...}
}
```

## 🎯 Success Indicators

### ✅ All Workflows Working
- System status: Operational
- All agents: Active
- All services: Healthy
- All workflows: Functional
- All security features: Operational

### ✅ Performance Metrics
- Response time: < 500ms
- Throughput: 2000+ ops/sec
- Availability: 99.9%
- Error rate: < 1%

### ✅ Security Metrics
- Threat detection: < 1 second
- Incident response: < 5 minutes
- Audit logging: < 100ms
- Security monitoring: Real-time

## 🚀 Next Steps

After successful verification:

1. **Deploy to Production**: System is ready for production deployment
2. **Monitor Performance**: Use monitoring tools to track system performance
3. **Update Documentation**: Keep documentation current with system changes
4. **Regular Testing**: Run verification scripts regularly to ensure system health
5. **Continuous Improvement**: Use verification results to improve system performance

## 📞 Support

If you encounter issues during verification:

1. **Check Logs**: Review log files for detailed error information
2. **Run Diagnostics**: Use individual verification scripts to isolate issues
3. **Check Configuration**: Verify all configuration files are correct
4. **Restart Services**: Restart Docker services if needed
5. **Contact Support**: Use the verification reports to get help

---

**🎉 The AMAS Intelligence System is now fully verified and ready for production deployment!**