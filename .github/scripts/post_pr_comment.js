const fs = require('fs');
const path = require('path');

/**
 * Universal PR Commenter - JavaScript version
 * Creates consistent, rich PR comments for all AI workflows
 */

class UniversalPRCommenter {
  constructor() {
    this.commentTemplates = {
      dependency_analysis: {
        title: "🤖 AI Dependency & Code-Fix Analysis",
        icon: "🔧",
        description: "Intelligent dependency resolution and code enhancement"
      },
      security_audit: {
        title: "🛡️ AI Security & Threat Intelligence",
        icon: "🔒",
        description: "Comprehensive security vulnerability scanning and threat analysis"
      },
      build_analysis: {
        title: "🚀 AI Build & Deploy Insights",
        icon: "🏗️",
        description: "Intelligent build optimization and deployment analysis"
      },
      code_quality: {
        title: "📊 AI Code Quality & Performance",
        icon: "⚡",
        description: "Advanced code quality analysis and performance optimization"
      },
      project_audit: {
        title: "📚 AI Project Audit & Documentation",
        icon: "📖",
        description: "Comprehensive project analysis and documentation generation"
      },
      issue_responder: {
        title: "🤖 AI Issue Auto-Responder",
        icon: "💬",
        description: "Intelligent issue analysis and automated response generation"
      },
      self_improver: {
        title: "🧠 AI Project Self-Improver",
        icon: "🔄",
        description: "Continuous learning and project enhancement system"
      },
      parallel_analysis: {
        title: "⚡ AI Parallel Analysis",
        icon: "🚀",
        description: "Multi-provider parallel analysis for maximum reliability"
      },
      master_integration: {
        title: "🎯 AI Master Integration System",
        icon: "🌟",
        description: "Comprehensive AI system orchestration and analysis"
      }
    };
  }

  loadAIResults(workflowType, resultFile) {
    try {
      if (!fs.existsSync(resultFile)) {
        return { error: `Result file not found: ${resultFile}` };
      }
      
      const data = fs.readFileSync(resultFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      return { error: `Failed to load results: ${error.message}` };
    }
  }

  extractAIMetadata(results) {
    const metadata = {
      success: false,
      provider_used: "Unknown",
      response_time: 0,
      confidence: 0,
      analysis_type: "Unknown",
      timestamp: new Date().toISOString()
    };

    // Try different result structures
    if (results.metadata) {
      const meta = results.metadata;
      metadata.success = meta.ai_success || meta.success || false;
      metadata.provider_used = meta.provider_used || "Unknown";
      metadata.response_time = meta.response_time || 0;
      metadata.timestamp = meta.timestamp || metadata.timestamp;
    }

    if (results.ai_analysis) {
      const analysis = results.ai_analysis;
      if (typeof analysis === 'object') {
        metadata.confidence = analysis.confidence || 0;
        metadata.analysis_type = analysis.type || "analysis";
      }
    }

    if (results.summary) {
      const summary = results.summary;
      metadata.success = summary.ai_analysis_success || summary.success || false;
    }

    return metadata;
  }

  extractRecommendations(results) {
    const recommendations = [];

    // Try different recommendation structures
    if (results.recommendations) {
      const recs = results.recommendations;
      if (typeof recs === 'object') {
        // Handle structured recommendations
        Object.entries(recs).forEach(([key, value]) => {
          if (Array.isArray(value)) {
            recommendations.push(...value.slice(0, 3)); // Limit to 3 per category
          } else if (typeof value === 'string') {
            recommendations.push(value);
          }
        });
      } else if (Array.isArray(recs)) {
        recommendations.push(...recs.slice(0, 5)); // Limit to 5 total
      }
    }

    if (results.ai_analysis) {
      const analysis = results.ai_analysis;
      if (typeof analysis === 'object') {
        // Extract from analysis
        ['immediate_actions', 'long_term_improvements', 'workflow_changes'].forEach(key => {
          if (analysis[key] && Array.isArray(analysis[key])) {
            recommendations.push(...analysis[key].slice(0, 2)); // Limit to 2 per category
          }
        });
      }
    }

    if (results.fixes_applied) {
      const fixes = results.fixes_applied;
      if (typeof fixes === 'object') {
        const applied = fixes.applied_fixes || [];
        if (Array.isArray(applied)) {
          applied.slice(0, 3).forEach(fix => {
            recommendations.push(`Applied: ${fix.description || 'Fix'}`);
          });
        }
      }
    }

    // Remove duplicates and limit total
    const uniqueRecs = [...new Set(recommendations)].slice(0, 8);
    return uniqueRecs;
  }

  extractMetrics(results) {
    const metrics = {
      issues_found: 0,
      fixes_applied: 0,
      success_rate: 0,
      total_time: 0
    };

    // Try different metric structures
    if (results.issues_detected) {
      const issues = results.issues_detected;
      if (typeof issues === 'object') {
        const missingModules = issues.missing_modules || [];
        metrics.issues_found = Array.isArray(missingModules) ? missingModules.length : 0;
      }
    }

    if (results.fixes_applied) {
      const fixes = results.fixes_applied;
      if (typeof fixes === 'object') {
        metrics.fixes_applied = fixes.total_applied || 0;
      }
    }

    if (results.summary) {
      const summary = results.summary;
      metrics.success_rate = summary.overall_success_rate || 0;
      metrics.total_time = summary.total_time || 0;
    }

    return metrics;
  }

  generateComment(workflowType, results) {
    const template = this.commentTemplates[workflowType] || {
      title: "🤖 AI Analysis",
      icon: "🔍",
      description: "AI-powered analysis and recommendations"
    };

    const metadata = this.extractAIMetadata(results);
    const recommendations = this.extractRecommendations(results);
    const metrics = this.extractMetrics(results);

    // Build comment
    let comment = `## ${template.title}

**Status:** ${metadata.success ? '✅ Completed' : '❌ Failed'}
**Provider:** ${metadata.provider_used}
**Response Time:** ${metadata.response_time.toFixed(2)}s
**Confidence:** ${(metadata.confidence * 100).toFixed(1)}%

---

### 📊 Analysis Summary
${template.description}

`;

    // Add metrics if available
    if (metrics.issues_found > 0 || metrics.fixes_applied > 0) {
      comment += `**Issues Detected:** ${metrics.issues_found}
**Fixes Applied:** ${metrics.fixes_applied}
**Success Rate:** ${metrics.success_rate.toFixed(1)}%

---

`;
    }

    // Add recommendations
    if (recommendations.length > 0) {
      comment += `### 💡 Key Recommendations
${recommendations.slice(0, 5).map(rec => `- ${rec}`).join('\n')}

---

`;
    }

    // Add specific analysis content if available
    if (results.ai_analysis && typeof results.ai_analysis === 'object' && results.ai_analysis.analysis) {
      let analysisText = results.ai_analysis.analysis;
      if (analysisText.length > 200) {
        analysisText = analysisText.substring(0, 200) + "...";
      }
      comment += `### 🔍 Analysis Details
${analysisText}

---

`;
    }

    // Add footer
    comment += `### 🚀 AI Capabilities
- **16-Provider Fallback**: Maximum reliability and speed
- **Intelligent Analysis**: Advanced pattern recognition
- **Automated Fixes**: Self-healing system capabilities
- **Continuous Learning**: Improves over time

---

*${template.icon} Generated by ${template.title} at ${metadata.timestamp}*
*Advanced Multi-Agent Intelligence System v3.0*
`;

    return comment;
  }

  async postComment(workflowType, resultFile) {
    try {
      const results = this.loadAIResults(workflowType, resultFile);
      
      if (results.error) {
        console.log(`⚠️ ${results.error}`);
        return {
          success: false,
          error: results.error,
          workflow_type: workflowType
        };
      }

      const comment = this.generateComment(workflowType, results);
      
      return {
        success: true,
        comment: comment,
        workflow_type: workflowType,
        metadata: this.extractAIMetadata(results)
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        workflow_type: workflowType
      };
    }
  }
}

// Export for use in GitHub Actions
module.exports = UniversalPRCommenter;

// If run directly
if (require.main === module) {
  const args = process.argv.slice(2);
  const workflowType = args[0] || 'code_quality';
  const resultFile = args[1] || 'artifacts/ai_analysis_results.json';
  
  const commenter = new UniversalPRCommenter();
  
  commenter.postComment(workflowType, resultFile)
    .then(result => {
      if (result.success) {
        console.log('✅ Comment generated successfully');
        console.log(`🤖 Provider: ${result.metadata.provider_used}`);
        console.log(`⏱️ Response Time: ${result.metadata.response_time.toFixed(2)}s`);
        
        // Save comment to file
        fs.writeFileSync('pr_comment.md', result.comment);
        console.log('📄 Saved to: pr_comment.md');
      } else {
        console.log(`❌ Failed to generate comment: ${result.error}`);
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('❌ Error:', error);
      process.exit(1);
    });
}