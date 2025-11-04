"""
Background SLO Evaluator

Periodically evaluates SLOs and triggers alerts when violations occur.
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime, timezone

from .slo_manager import get_slo_manager, SLOManager

logger = logging.getLogger(__name__)


class SLOEvaluator:
    """
    Background task that periodically evaluates SLOs and checks for violations.
    """
    
    def __init__(self, 
                 slo_manager: Optional[SLOManager] = None,
                 evaluation_interval_seconds: int = 60):
        """
        Initialize SLO Evaluator
        
        Args:
            slo_manager: SLO Manager instance (will create if None)
            evaluation_interval_seconds: How often to evaluate SLOs
        """
        self.slo_manager = slo_manager or get_slo_manager()
        self.evaluation_interval = evaluation_interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the SLO evaluation loop"""
        if self._running:
            logger.warning("SLO Evaluator is already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._evaluation_loop())
        logger.info(f"SLO Evaluator started (interval: {self.evaluation_interval}s)")
    
    async def stop(self):
        """Stop the SLO evaluation loop"""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("SLO Evaluator stopped")
    
    async def _evaluation_loop(self):
        """Main evaluation loop"""
        while self._running:
            try:
                # Evaluate all SLOs
                results = self.slo_manager.evaluate_all_slos()
                
                # Check for violations
                violations = self.slo_manager.get_violations()
                
                if violations:
                    logger.warning(f"Detected {len(violations)} SLO violations")
                    for violation in violations:
                        logger.warning(
                            f"SLO {violation.slo_name}: {violation.status} "
                            f"({violation.error_budget_remaining_percent:.2f}% budget remaining)"
                        )
                
                # Check for burn rate alerts
                try:
                    import yaml
                    import os
                    
                    slo_config_path = self.slo_manager.slo_config_path
                    with open(slo_config_path, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    burn_rate_alerts = self.slo_manager.check_burn_rate_alerts(config)
                    
                    if burn_rate_alerts:
                        logger.critical(f"Detected {len(burn_rate_alerts)} burn rate alerts")
                        for alert in burn_rate_alerts:
                            logger.critical(
                                f"Burn rate alert: {alert['alert_name']} for "
                                f"SLO {alert['slo_name']} (burn rate: {alert['burn_rate']:.2f}x)"
                            )
                except Exception as e:
                    logger.debug(f"Failed to check burn rate alerts: {e}")
                
                # Log summary
                logger.debug(
                    f"SLO evaluation complete: {len(results)} SLOs evaluated, "
                    f"{len(violations)} violations"
                )
                
            except Exception as e:
                logger.error(f"Error in SLO evaluation loop: {e}", exc_info=True)
            
            # Wait for next evaluation
            await asyncio.sleep(self.evaluation_interval)
    
    async def evaluate_once(self):
        """Evaluate SLOs once (for manual triggering)"""
        results = self.slo_manager.evaluate_all_slos()
        violations = self.slo_manager.get_violations()
        return {
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "slo_count": len(results),
            "violations_count": len(violations),
            "violations": [
                {
                    "slo_name": v.slo_name,
                    "status": v.status,
                    "error_budget_remaining_percent": v.error_budget_remaining_percent
                }
                for v in violations
            ]
        }


# Global evaluator instance
_global_evaluator: Optional[SLOEvaluator] = None


def initialize_slo_evaluator(evaluation_interval_seconds: int = 60) -> SLOEvaluator:
    """Initialize and start global SLO evaluator"""
    global _global_evaluator
    _global_evaluator = SLOEvaluator(
        evaluation_interval_seconds=evaluation_interval_seconds
    )
    return _global_evaluator


def get_slo_evaluator() -> Optional[SLOEvaluator]:
    """Get global SLO evaluator instance"""
    return _global_evaluator
