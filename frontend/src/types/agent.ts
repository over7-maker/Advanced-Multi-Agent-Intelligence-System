// Agent system type definitions

export enum AgentSpecialty {
  // Research specialists
  ACADEMIC_RESEARCHER = "academic_researcher",
  WEB_INTELLIGENCE = "web_intelligence_gatherer",
  NEWS_ANALYST = "news_trends_analyzer",
  COMPETITIVE_INTEL = "competitive_intelligence",
  SOCIAL_MONITOR = "social_media_monitor",
  
  // Analysis specialists  
  DATA_ANALYST = "data_analyst",
  STATISTICAL_MODELER = "statistical_modeler",
  PATTERN_RECOGNIZER = "pattern_recognition_expert",
  RISK_ASSESSOR = "risk_assessment_specialist",
  FINANCIAL_ANALYZER = "financial_performance_analyst",
  
  // Creative specialists
  GRAPHICS_DESIGNER = "graphics_diagram_designer",
  CONTENT_WRITER = "content_writer_editor",
  PRESENTATION_FORMATTER = "presentation_formatter",
  MEDIA_PRODUCER = "media_video_producer",
  INFOGRAPHIC_CREATOR = "infographic_creator",
  
  // QA specialists
  FACT_CHECKER = "fact_checker_validator",
  QUALITY_CONTROLLER = "output_quality_controller",
  COMPLIANCE_REVIEWER = "compliance_reviewer",
  ERROR_DETECTOR = "error_detection_specialist",
}

export enum TaskComplexity {
  SIMPLE = "simple",
  MODERATE = "moderate", 
  COMPLEX = "complex",
  ENTERPRISE = "enterprise",
  INVESTIGATION = "investigation",
}

export enum TaskStatus {
  PENDING = "pending",
  READY = "ready",
  IN_PROGRESS = "in_progress",
  BLOCKED = "blocked",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export interface AgentCapabilities {
  skills: string[];
  tools: string[];
  avgTaskDuration: number;
  maxParallelTasks: number;
  qualityScore: number;
  costPerHour: number;
}

export interface Agent {
  id: string;
  specialty: AgentSpecialty;
  status: 'available' | 'busy' | 'offline' | 'failed';
  currentTasks: string[];
  maxConcurrentTasks: number;
  capabilities: AgentCapabilities;
  loadPercentage: number;
  successRate: number;
  avgCompletionTime: number;
  qualityScore: number;
}

export interface SubTask {
  id: string;
  title: string;
  description: string;
  assignedAgent: AgentSpecialty;
  estimatedDurationHours: number;
  priority: number;
  dependsOn: string[];
  status: TaskStatus;
  startedAt?: Date;
  completedAt?: Date;
  outputSummary?: string;
  successCriteria: string[];
  qualityCheckpoints: string[];
}

export interface WorkflowPlan {
  id: string;
  userRequest: string;
  complexity: TaskComplexity;
  subTasks: SubTask[];
  executionPhases: string[];
  estimatedTotalHours: number;
  estimatedCostUsd: number;
  requiredSpecialists: AgentSpecialty[];
  qualityGates: QualityGate[];
  createdAt: Date;
  status: string;
  progressPercentage: number;
  riskAssessment: 'low' | 'medium' | 'high' | 'critical';
  userApprovalRequired: boolean;
}

export interface QualityGate {
  name: string;
  description: string;
  threshold: number;
  checkpoint: string;
}

export interface WorkflowExecution {
  executionId: string;
  workflowId: string;
  status: 'planned' | 'executing' | 'completed' | 'failed' | 'cancelled';
  progressPercentage: number;
  tasksCompleted: number;
  tasksInProgress: number;
  tasksPending: number;
  estimatedRemainingHours: number;
  overallHealth: 'healthy' | 'warning' | 'degraded';
  currentPhase: string;
  startedAt?: Date;
  completedAt?: Date;
}

export interface TeamComposition {
  researchAgents: AgentSpecialty[];
  analysisAgents: AgentSpecialty[];
  creativeAgents: AgentSpecialty[];
  qaAgents: AgentSpecialty[];
  estimatedCost: number;
  estimatedDuration: number;
  qualityScore: number;
}
