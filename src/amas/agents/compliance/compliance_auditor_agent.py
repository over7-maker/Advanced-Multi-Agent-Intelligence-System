"""
Compliance Auditor Agent for AMAS Intelligence System
Provides regulatory compliance monitoring, auditing, and reporting
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import re
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Compliance framework enumeration"""
    GDPR = "gdpr"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"
    CCPA = "ccpa"
    FERPA = "ferpa"


class ComplianceLevel(Enum):
    """Compliance level enumeration"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    REQUIRES_REVIEW = "requires_review"


class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    id: str
    framework: ComplianceFramework
    category: str
    title: str
    description: str
    requirements: List[str]
    controls: List[str]
    risk_level: RiskLevel
    automated_check: bool = True
    remediation_steps: List[str] = field(default_factory=list)


@dataclass
class ComplianceCheck:
    """Compliance check result"""
    rule_id: str
    status: ComplianceLevel
    score: float
    findings: List[str]
    recommendations: List[str]
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    risk_level: RiskLevel = RiskLevel.LOW


@dataclass
class ComplianceReport:
    """Compliance audit report"""
    id: str
    framework: ComplianceFramework
    overall_score: float
    compliance_level: ComplianceLevel
    checks: List[ComplianceCheck]
    summary: str
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)
    valid_until: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=90))


class ComplianceAuditorAgent:
    """
    Compliance Auditor Agent for AMAS Intelligence System
    
    Provides:
    - Automated compliance checking
    - Regulatory framework support
    - Risk assessment and mitigation
    - Compliance reporting and documentation
    - Continuous monitoring and alerting
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the compliance auditor agent"""
        self.config = config
        self.agent_id = "compliance_auditor_001"
        self.capabilities = [
            "compliance_auditing",
            "regulatory_analysis",
            "risk_assessment",
            "policy_validation",
            "audit_reporting",
            "continuous_monitoring"
        ]
        
        # Compliance rules database
        self.compliance_rules = {}
        self.framework_configs = {}
        
        # Audit results
        self.audit_results = {}
        self.compliance_reports = {}
        
        # Risk assessment
        self.risk_factors = {}
        self.mitigation_strategies = {}
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_tasks = []
        
        logger.info("Compliance Auditor Agent initialized")

    async def initialize(self):
        """Initialize the compliance auditor agent"""
        try:
            logger.info("Initializing Compliance Auditor Agent...")
            
            # Load compliance frameworks
            await self._load_compliance_frameworks()
            
            # Initialize compliance rules
            await self._initialize_compliance_rules()
            
            # Start monitoring
            await self._start_compliance_monitoring()
            
            logger.info("Compliance Auditor Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Compliance Auditor Agent: {e}")
            raise

    async def _load_compliance_frameworks(self):
        """Load compliance framework configurations"""
        try:
            # GDPR Configuration
            self.framework_configs[ComplianceFramework.GDPR] = {
                "name": "General Data Protection Regulation",
                "version": "2018",
                "scope": "EU data protection",
                "key_requirements": [
                    "Data minimization",
                    "Purpose limitation",
                    "Storage limitation",
                    "Accuracy",
                    "Security",
                    "Accountability",
                    "Transparency",
                    "Individual rights"
                ],
                "penalties": {
                    "max_fine": "€20M or 4% of annual turnover",
                    "criteria": "Whichever is higher"
                }
            }
            
            # SOC 2 Configuration
            self.framework_configs[ComplianceFramework.SOC2] = {
                "name": "SOC 2 Type II",
                "version": "2017",
                "scope": "Service organization controls",
                "trust_principles": [
                    "Security",
                    "Availability",
                    "Processing integrity",
                    "Confidentiality",
                    "Privacy"
                ],
                "audit_frequency": "Annual"
            }
            
            # HIPAA Configuration
            self.framework_configs[ComplianceFramework.HIPAA] = {
                "name": "Health Insurance Portability and Accountability Act",
                "version": "2013",
                "scope": "Healthcare data protection",
                "key_requirements": [
                    "Administrative safeguards",
                    "Physical safeguards",
                    "Technical safeguards",
                    "Organizational requirements",
                    "Policies and procedures"
                ],
                "penalties": {
                    "max_fine": "$1.5M per violation",
                    "criminal_penalties": "Up to 10 years imprisonment"
                }
            }
            
            # PCI DSS Configuration
            self.framework_configs[ComplianceFramework.PCI_DSS] = {
                "name": "Payment Card Industry Data Security Standard",
                "version": "4.0",
                "scope": "Payment card data protection",
                "requirements": [
                    "Install and maintain security systems",
                    "Protect cardholder data",
                    "Maintain vulnerability management",
                    "Implement strong access controls",
                    "Regularly monitor networks",
                    "Maintain information security policy"
                ],
                "compliance_levels": ["Level 1", "Level 2", "Level 3", "Level 4"]
            }
            
            logger.info(f"Loaded {len(self.framework_configs)} compliance frameworks")
            
        except Exception as e:
            logger.error(f"Failed to load compliance frameworks: {e}")
            raise

    async def _initialize_compliance_rules(self):
        """Initialize compliance rules for each framework"""
        try:
            # GDPR Rules
            await self._initialize_gdpr_rules()
            
            # SOC 2 Rules
            await self._initialize_soc2_rules()
            
            # HIPAA Rules
            await self._initialize_hipaa_rules()
            
            # PCI DSS Rules
            await self._initialize_pci_dss_rules()
            
            logger.info(f"Initialized {len(self.compliance_rules)} compliance rules")
            
        except Exception as e:
            logger.error(f"Failed to initialize compliance rules: {e}")
            raise

    async def _initialize_gdpr_rules(self):
        """Initialize GDPR compliance rules"""
        try:
            gdpr_rules = [
                ComplianceRule(
                    id="gdpr_001",
                    framework=ComplianceFramework.GDPR,
                    category="Data Processing",
                    title="Lawful Basis for Processing",
                    description="Ensure all personal data processing has a lawful basis",
                    requirements=[
                        "Consent must be freely given, specific, informed, and unambiguous",
                        "Processing must be necessary for contract performance",
                        "Processing must be necessary for legal compliance",
                        "Processing must be necessary for legitimate interests"
                    ],
                    controls=[
                        "Document lawful basis for each processing activity",
                        "Implement consent management system",
                        "Regular review of processing purposes",
                        "Data subject rights implementation"
                    ],
                    risk_level=RiskLevel.HIGH,
                    remediation_steps=[
                        "Conduct data processing audit",
                        "Update privacy notices",
                        "Implement consent management",
                        "Train staff on lawful basis requirements"
                    ]
                ),
                ComplianceRule(
                    id="gdpr_002",
                    framework=ComplianceFramework.GDPR,
                    category="Data Security",
                    title="Data Protection by Design and Default",
                    description="Implement appropriate technical and organizational measures",
                    requirements=[
                        "Data minimization",
                        "Purpose limitation",
                        "Storage limitation",
                        "Accuracy and up-to-date data",
                        "Security of processing"
                    ],
                    controls=[
                        "Encryption of personal data",
                        "Access controls and authentication",
                        "Regular security assessments",
                        "Incident response procedures",
                        "Data backup and recovery"
                    ],
                    risk_level=RiskLevel.HIGH,
                    remediation_steps=[
                        "Implement encryption at rest and in transit",
                        "Review and update access controls",
                        "Conduct security risk assessment",
                        "Update incident response procedures"
                    ]
                ),
                ComplianceRule(
                    id="gdpr_003",
                    framework=ComplianceFramework.GDPR,
                    category="Individual Rights",
                    title="Data Subject Rights",
                    description="Enable data subjects to exercise their rights",
                    requirements=[
                        "Right to information",
                        "Right of access",
                        "Right to rectification",
                        "Right to erasure",
                        "Right to restrict processing",
                        "Right to data portability",
                        "Right to object"
                    ],
                    controls=[
                        "Self-service portal for data subjects",
                        "Automated response to data subject requests",
                        "Identity verification procedures",
                        "Response time tracking",
                        "Appeal mechanisms"
                    ],
                    risk_level=RiskLevel.MEDIUM,
                    remediation_steps=[
                        "Implement data subject request portal",
                        "Create automated response workflows",
                        "Train staff on data subject rights",
                        "Establish response time SLAs"
                    ]
                )
            ]
            
            for rule in gdpr_rules:
                self.compliance_rules[rule.id] = rule
                
        except Exception as e:
            logger.error(f"Failed to initialize GDPR rules: {e}")

    async def _initialize_soc2_rules(self):
        """Initialize SOC 2 compliance rules"""
        try:
            soc2_rules = [
                ComplianceRule(
                    id="soc2_001",
                    framework=ComplianceFramework.SOC2,
                    category="Security",
                    title="Access Controls",
                    description="Implement appropriate access controls",
                    requirements=[
                        "User access provisioning and deprovisioning",
                        "Multi-factor authentication",
                        "Regular access reviews",
                        "Privileged access management",
                        "Session management"
                    ],
                    controls=[
                        "Identity and access management system",
                        "Role-based access controls",
                        "Regular access certifications",
                        "Privileged account monitoring",
                        "Session timeout controls"
                    ],
                    risk_level=RiskLevel.HIGH,
                    remediation_steps=[
                        "Implement IAM system",
                        "Enable MFA for all users",
                        "Conduct access review",
                        "Implement privileged access controls"
                    ]
                ),
                ComplianceRule(
                    id="soc2_002",
                    framework=ComplianceFramework.SOC2,
                    category="Availability",
                    title="System Availability",
                    description="Ensure system availability and performance",
                    requirements=[
                        "System monitoring and alerting",
                        "Disaster recovery procedures",
                        "Business continuity planning",
                        "Capacity management",
                        "Incident response"
                    ],
                    controls=[
                        "24/7 system monitoring",
                        "Automated failover systems",
                        "Regular DR testing",
                        "Performance monitoring",
                        "Incident management system"
                    ],
                    risk_level=RiskLevel.MEDIUM,
                    remediation_steps=[
                        "Implement comprehensive monitoring",
                        "Update disaster recovery procedures",
                        "Conduct DR testing",
                        "Establish incident response team"
                    ]
                )
            ]
            
            for rule in soc2_rules:
                self.compliance_rules[rule.id] = rule
                
        except Exception as e:
            logger.error(f"Failed to initialize SOC 2 rules: {e}")

    async def _initialize_hipaa_rules(self):
        """Initialize HIPAA compliance rules"""
        try:
            hipaa_rules = [
                ComplianceRule(
                    id="hipaa_001",
                    framework=ComplianceFramework.HIPAA,
                    category="Administrative Safeguards",
                    title="Security Officer and Workforce Training",
                    description="Designate security officer and provide workforce training",
                    requirements=[
                        "Designated security officer",
                        "Workforce training program",
                        "Information access management",
                        "Workforce access management",
                        "Security awareness training"
                    ],
                    controls=[
                        "Security officer designation",
                        "Regular training programs",
                        "Access management procedures",
                        "Security incident procedures",
                        "Contingency planning"
                    ],
                    risk_level=RiskLevel.HIGH,
                    remediation_steps=[
                        "Designate security officer",
                        "Develop training program",
                        "Implement access controls",
                        "Create incident response procedures"
                    ]
                )
            ]
            
            for rule in hipaa_rules:
                self.compliance_rules[rule.id] = rule
                
        except Exception as e:
            logger.error(f"Failed to initialize HIPAA rules: {e}")

    async def _initialize_pci_dss_rules(self):
        """Initialize PCI DSS compliance rules"""
        try:
            pci_rules = [
                ComplianceRule(
                    id="pci_001",
                    framework=ComplianceFramework.PCI_DSS,
                    category="Network Security",
                    title="Firewall Configuration",
                    description="Install and maintain firewall configuration",
                    requirements=[
                        "Firewall and router configuration",
                        "Default password changes",
                        "Network segmentation",
                        "Regular firewall reviews",
                        "Documentation of firewall rules"
                    ],
                    controls=[
                        "Network firewall implementation",
                        "Router security configuration",
                        "Network segmentation controls",
                        "Regular firewall rule reviews",
                        "Change management procedures"
                    ],
                    risk_level=RiskLevel.HIGH,
                    remediation_steps=[
                        "Implement network firewalls",
                        "Change default passwords",
                        "Implement network segmentation",
                        "Document firewall rules"
                    ]
                )
            ]
            
            for rule in pci_rules:
                self.compliance_rules[rule.id] = rule
                
        except Exception as e:
            logger.error(f"Failed to initialize PCI DSS rules: {e}")

    async def _start_compliance_monitoring(self):
        """Start continuous compliance monitoring"""
        try:
            self.monitoring_active = True
            
            # Start monitoring tasks
            self.monitoring_tasks = [
                asyncio.create_task(self._monitor_data_processing()),
                asyncio.create_task(self._monitor_access_controls()),
                asyncio.create_task(self._monitor_security_incidents()),
                asyncio.create_task(self._monitor_data_retention()),
                asyncio.create_task(self._generate_compliance_alerts())
            ]
            
            logger.info("Compliance monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start compliance monitoring: {e}")
            raise

    async def _monitor_data_processing(self):
        """Monitor data processing activities for compliance"""
        while self.monitoring_active:
            try:
                # Check for data processing activities
                # This would integrate with actual data processing systems
                
                # Simulate monitoring
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Data processing monitoring error: {e}")
                await asyncio.sleep(60)

    async def _monitor_access_controls(self):
        """Monitor access controls for compliance"""
        while self.monitoring_active:
            try:
                # Check access control compliance
                # This would integrate with IAM systems
                
                # Simulate monitoring
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Access control monitoring error: {e}")
                await asyncio.sleep(60)

    async def _monitor_security_incidents(self):
        """Monitor security incidents for compliance"""
        while self.monitoring_active:
            try:
                # Check for security incidents
                # This would integrate with SIEM systems
                
                # Simulate monitoring
                await asyncio.sleep(180)  # Check every 3 minutes
                
            except Exception as e:
                logger.error(f"Security incident monitoring error: {e}")
                await asyncio.sleep(60)

    async def _monitor_data_retention(self):
        """Monitor data retention policies for compliance"""
        while self.monitoring_active:
            try:
                # Check data retention compliance
                # This would integrate with data management systems
                
                # Simulate monitoring
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Data retention monitoring error: {e}")
                await asyncio.sleep(60)

    async def _generate_compliance_alerts(self):
        """Generate compliance alerts and notifications"""
        while self.monitoring_active:
            try:
                # Generate compliance alerts
                # This would check for compliance violations
                
                # Simulate alert generation
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"Compliance alert generation error: {e}")
                await asyncio.sleep(60)

    async def run_compliance_audit(self, framework: ComplianceFramework, scope: Dict[str, Any] = None) -> ComplianceReport:
        """Run a comprehensive compliance audit"""
        try:
            logger.info(f"Starting compliance audit for {framework.value}")
            
            # Get framework rules
            framework_rules = [
                rule for rule in self.compliance_rules.values()
                if rule.framework == framework
            ]
            
            if not framework_rules:
                raise Exception(f"No rules found for framework {framework.value}")
            
            # Run compliance checks
            checks = []
            total_score = 0
            
            for rule in framework_rules:
                check = await self._run_compliance_check(rule, scope)
                checks.append(check)
                total_score += check.score
            
            # Calculate overall score
            overall_score = total_score / len(checks) if checks else 0
            
            # Determine compliance level
            compliance_level = self._determine_compliance_level(overall_score)
            
            # Generate report
            report = ComplianceReport(
                id=f"audit_{framework.value}_{int(datetime.utcnow().timestamp())}",
                framework=framework,
                overall_score=overall_score,
                compliance_level=compliance_level,
                checks=checks,
                summary=await self._generate_audit_summary(checks, overall_score),
                recommendations=await self._generate_recommendations(checks)
            )
            
            # Store report
            self.compliance_reports[report.id] = report
            
            logger.info(f"Compliance audit completed: {compliance_level.value} ({overall_score:.1f}%)")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to run compliance audit: {e}")
            raise

    async def _run_compliance_check(self, rule: ComplianceRule, scope: Dict[str, Any] = None) -> ComplianceCheck:
        """Run a single compliance check"""
        try:
            # Simulate compliance check
            # In production, this would perform actual checks
            
            # Random score for simulation
            import random
            score = random.uniform(0.6, 1.0)
            
            # Determine status based on score
            if score >= 0.9:
                status = ComplianceLevel.COMPLIANT
            elif score >= 0.7:
                status = ComplianceLevel.PARTIALLY_COMPLIANT
            else:
                status = ComplianceLevel.NON_COMPLIANT
            
            # Generate findings
            findings = []
            recommendations = []
            
            if status == ComplianceLevel.NON_COMPLIANT:
                findings.append(f"Non-compliance detected for rule: {rule.title}")
                recommendations.extend(rule.remediation_steps)
            elif status == ComplianceLevel.PARTIALLY_COMPLIANT:
                findings.append(f"Partial compliance for rule: {rule.title}")
                recommendations.extend(rule.remediation_steps[:2])  # Top 2 recommendations
            
            # Generate evidence
            evidence = [
                f"Automated check completed at {datetime.utcnow().isoformat()}",
                f"Rule ID: {rule.id}",
                f"Framework: {rule.framework.value}"
            ]
            
            return ComplianceCheck(
                rule_id=rule.id,
                status=status,
                score=score * 100,
                findings=findings,
                recommendations=recommendations,
                evidence=evidence,
                risk_level=rule.risk_level
            )
            
        except Exception as e:
            logger.error(f"Failed to run compliance check for rule {rule.id}: {e}")
            return ComplianceCheck(
                rule_id=rule.id,
                status=ComplianceLevel.REQUIRES_REVIEW,
                score=0,
                findings=[f"Error during compliance check: {str(e)}"],
                recommendations=["Review system configuration and retry"],
                risk_level=RiskLevel.HIGH
            )

    def _determine_compliance_level(self, score: float) -> ComplianceLevel:
        """Determine compliance level based on score"""
        if score >= 90:
            return ComplianceLevel.COMPLIANT
        elif score >= 70:
            return ComplianceLevel.PARTIALLY_COMPLIANT
        else:
            return ComplianceLevel.NON_COMPLIANT

    async def _generate_audit_summary(self, checks: List[ComplianceCheck], overall_score: float) -> str:
        """Generate audit summary"""
        try:
            total_checks = len(checks)
            compliant_checks = len([c for c in checks if c.status == ComplianceLevel.COMPLIANT])
            non_compliant_checks = len([c for c in checks if c.status == ComplianceLevel.NON_COMPLIANT])
            partially_compliant_checks = len([c for c in checks if c.status == ComplianceLevel.PARTIALLY_COMPLIANT])
            
            summary = f"""
            Compliance Audit Summary:
            - Total Checks: {total_checks}
            - Compliant: {compliant_checks} ({compliant_checks/total_checks*100:.1f}%)
            - Partially Compliant: {partially_compliant_checks} ({partially_compliant_checks/total_checks*100:.1f}%)
            - Non-Compliant: {non_compliant_checks} ({non_compliant_checks/total_checks*100:.1f}%)
            - Overall Score: {overall_score:.1f}%
            """
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate audit summary: {e}")
            return "Error generating audit summary"

    async def _generate_recommendations(self, checks: List[ComplianceCheck]) -> List[str]:
        """Generate recommendations based on check results"""
        try:
            recommendations = []
            
            # Collect recommendations from non-compliant checks
            for check in checks:
                if check.status in [ComplianceLevel.NON_COMPLIANT, ComplianceLevel.PARTIALLY_COMPLIANT]:
                    recommendations.extend(check.recommendations)
            
            # Remove duplicates and prioritize
            unique_recommendations = list(set(recommendations))
            
            # Prioritize by risk level
            high_risk_recommendations = []
            medium_risk_recommendations = []
            low_risk_recommendations = []
            
            for rec in unique_recommendations:
                # Simple prioritization based on keywords
                if any(keyword in rec.lower() for keyword in ['critical', 'immediate', 'urgent', 'security']):
                    high_risk_recommendations.append(rec)
                elif any(keyword in rec.lower() for keyword in ['important', 'review', 'update', 'implement']):
                    medium_risk_recommendations.append(rec)
                else:
                    low_risk_recommendations.append(rec)
            
            # Combine prioritized recommendations
            prioritized_recommendations = (
                high_risk_recommendations + 
                medium_risk_recommendations + 
                low_risk_recommendations
            )
            
            return prioritized_recommendations[:10]  # Top 10 recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return ["Review compliance status and address identified issues"]

    async def get_compliance_status(self, framework: ComplianceFramework = None) -> Dict[str, Any]:
        """Get current compliance status"""
        try:
            if framework:
                # Get status for specific framework
                framework_rules = [
                    rule for rule in self.compliance_rules.values()
                    if rule.framework == framework
                ]
                
                return {
                    "framework": framework.value,
                    "total_rules": len(framework_rules),
                    "automated_rules": len([r for r in framework_rules if r.automated_check]),
                    "risk_distribution": {
                        level.value: len([r for r in framework_rules if r.risk_level == level])
                        for level in RiskLevel
                    },
                    "last_audit": self._get_last_audit_date(framework)
                }
            else:
                # Get overall status
                return {
                    "total_frameworks": len(self.framework_configs),
                    "total_rules": len(self.compliance_rules),
                    "automated_rules": len([r for r in self.compliance_rules.values() if r.automated_check]),
                    "frameworks": {
                        framework.value: {
                            "rules": len([r for r in self.compliance_rules.values() if r.framework == framework]),
                            "last_audit": self._get_last_audit_date(framework)
                        }
                        for framework in ComplianceFramework
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get compliance status: {e}")
            return {"error": str(e)}

    def _get_last_audit_date(self, framework: ComplianceFramework) -> Optional[str]:
        """Get last audit date for framework"""
        try:
            framework_reports = [
                report for report in self.compliance_reports.values()
                if report.framework == framework
            ]
            
            if framework_reports:
                latest_report = max(framework_reports, key=lambda r: r.generated_at)
                return latest_report.generated_at.isoformat()
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get last audit date: {e}")
            return None

    async def generate_compliance_report(self, framework: ComplianceFramework, format: str = "json") -> Union[Dict[str, Any], str]:
        """Generate compliance report in specified format"""
        try:
            # Run audit if no recent report exists
            recent_reports = [
                report for report in self.compliance_reports.values()
                if (report.framework == framework and 
                    report.generated_at > datetime.utcnow() - timedelta(days=7))
            ]
            
            if not recent_reports:
                report = await self.run_compliance_audit(framework)
            else:
                report = recent_reports[0]
            
            if format.lower() == "json":
                return {
                    "report_id": report.id,
                    "framework": report.framework.value,
                    "overall_score": report.overall_score,
                    "compliance_level": report.compliance_level.value,
                    "summary": report.summary,
                    "recommendations": report.recommendations,
                    "checks": [
                        {
                            "rule_id": check.rule_id,
                            "status": check.status.value,
                            "score": check.score,
                            "findings": check.findings,
                            "recommendations": check.recommendations,
                            "risk_level": check.risk_level.value
                        }
                        for check in report.checks
                    ],
                    "generated_at": report.generated_at.isoformat(),
                    "valid_until": report.valid_until.isoformat()
                }
            else:
                # Generate text report
                return await self._generate_text_report(report)
                
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise

    async def _generate_text_report(self, report: ComplianceReport) -> str:
        """Generate text format compliance report"""
        try:
            text_report = f"""
            COMPLIANCE AUDIT REPORT
            ========================
            
            Report ID: {report.id}
            Framework: {report.framework.value}
            Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}
            Valid Until: {report.valid_until.strftime('%Y-%m-%d %H:%M:%S')}
            
            OVERALL COMPLIANCE
            ==================
            Score: {report.overall_score:.1f}%
            Level: {report.compliance_level.value.upper()}
            
            SUMMARY
            =======
            {report.summary}
            
            RECOMMENDATIONS
            ===============
            """
            
            for i, rec in enumerate(report.recommendations, 1):
                text_report += f"{i}. {rec}\n"
            
            text_report += "\n\nDETAILED FINDINGS\n"
            text_report += "==================\n"
            
            for check in report.checks:
                text_report += f"\nRule: {check.rule_id}\n"
                text_report += f"Status: {check.status.value}\n"
                text_report += f"Score: {check.score:.1f}%\n"
                text_report += f"Risk Level: {check.risk_level.value}\n"
                
                if check.findings:
                    text_report += "Findings:\n"
                    for finding in check.findings:
                        text_report += f"  - {finding}\n"
                
                if check.recommendations:
                    text_report += "Recommendations:\n"
                    for rec in check.recommendations:
                        text_report += f"  - {rec}\n"
                
                text_report += "\n" + "-" * 50 + "\n"
            
            return text_report
            
        except Exception as e:
            logger.error(f"Failed to generate text report: {e}")
            return f"Error generating report: {str(e)}"

    async def shutdown(self):
        """Shutdown compliance auditor agent"""
        try:
            logger.info("Shutting down Compliance Auditor Agent...")
            
            # Stop monitoring
            self.monitoring_active = False
            
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            logger.info("Compliance Auditor Agent shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during compliance auditor shutdown: {e}")