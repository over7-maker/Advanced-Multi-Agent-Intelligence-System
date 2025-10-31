"""
Data Management Module for AMAS
Implements data versioning with DVC, data retention policies, backup/recovery procedures,
data privacy controls, and data lineage tracking
"""

import asyncio
import hashlib
import json
import logging
import os
import secrets
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

logger = logging.getLogger(__name__)


class DataClassification(Enum):
    """Data classification levels"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class DataRetentionPolicy(Enum):
    """Data retention policy types"""

    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"  # 30 days
    MEDIUM_TERM = "medium_term"  # 1 year
    LONG_TERM = "long_term"  # 7 years
    PERMANENT = "permanent"


class BackupType(Enum):
    """Backup types"""

    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class DataVersionManager:
    """Data versioning with DVC integration"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dvc_remote = config.get("dvc_remote", "s3://amas-data-bucket")
        self.data_dir = Path(config.get("data_dir", "data"))
        self.version_history = []

    async def initialize_dvc(self) -> bool:
        """Initialize DVC repository"""
        try:
            # Check if DVC is installed
            result = subprocess.run(
                ["dvc", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error("DVC not installed")
                return False

            # Initialize DVC if not already initialized
            if not (self.data_dir / ".dvc").exists():
                result = subprocess.run(
                    ["dvc", "init", "--no-scm"],
                    cwd=self.data_dir,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    logger.error(f"Failed to initialize DVC: {result.stderr}")
                    return False

            # Add remote storage
            result = subprocess.run(
                ["dvc", "remote", "add", "-d", "storage", self.dvc_remote],
                cwd=self.data_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.warning(f"Failed to add DVC remote: {result.stderr}")

            logger.info("DVC initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize DVC: {e}")
            return False

    async def add_data_file(
        self, file_path: str, classification: str = DataClassification.INTERNAL.value
    ) -> bool:
        """Add data file to DVC tracking"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False

            # Add file to DVC
            result = subprocess.run(
                ["dvc", "add", str(file_path)],
                cwd=self.data_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.error(f"Failed to add file to DVC: {result.stderr}")
                return False

            # Create version metadata
            version_info = {
                "file_path": str(file_path),
                "classification": classification,
                "added_at": datetime.utcnow().isoformat(),
                "file_hash": await self._calculate_file_hash(file_path),
                "file_size": file_path.stat().st_size,
            }

            self.version_history.append(version_info)
            logger.info(f"Added {file_path} to DVC tracking")
            return True

        except Exception as e:
            logger.error(f"Failed to add data file: {e}")
            return False

    async def commit_data_changes(self, message: str) -> bool:
        """Commit data changes to DVC"""
        try:
            result = subprocess.run(
                ["dvc", "commit"], cwd=self.data_dir, capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error(f"Failed to commit DVC changes: {result.stderr}")
                return False

            # Push to remote storage
            result = subprocess.run(
                ["dvc", "push"], cwd=self.data_dir, capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.warning(f"Failed to push to remote: {result.stderr}")

            logger.info("Data changes committed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to commit data changes: {e}")
            return False

    async def get_data_versions(self, file_path: str) -> List[Dict[str, Any]]:
        """Get version history for a data file"""
        try:
            result = subprocess.run(
                ["dvc", "show", "versions", str(file_path)],
                cwd=self.data_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.error(f"Failed to get versions: {result.stderr}")
                return []

            # Parse DVC output (simplified)
            versions = []
            for line in result.stdout.split("\n"):
                if line.strip():
                    versions.append(
                        {
                            "version": line.strip(),
                            "timestamp": datetime.utcnow().isoformat(),  # Mock timestamp
                        }
                    )

            return versions

        except Exception as e:
            logger.error(f"Failed to get data versions: {e}")
            return []

    async def checkout_data_version(self, file_path: str, version: str) -> bool:
        """Checkout specific version of data file"""
        try:
            result = subprocess.run(
                ["dvc", "checkout", f"{file_path}@{version}"],
                cwd=self.data_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.error(f"Failed to checkout version: {result.stderr}")
                return False

            logger.info(f"Checked out version {version} of {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to checkout data version: {e}")
            return False

    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


class DataRetentionManager:
    """Data retention policy management"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.retention_policies = self._load_retention_policies()
        self.data_lifecycle = []

    def _load_retention_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load data retention policies"""
        return {
            "logs": {
                "classification": DataClassification.INTERNAL.value,
                "retention_period": 90,  # days
                "policy": DataRetentionPolicy.SHORT_TERM.value,
                "auto_delete": True,
            },
            "user_data": {
                "classification": DataClassification.CONFIDENTIAL.value,
                "retention_period": 2555,  # 7 years
                "policy": DataRetentionPolicy.LONG_TERM.value,
                "auto_delete": False,
            },
            "analytics_data": {
                "classification": DataClassification.INTERNAL.value,
                "retention_period": 365,  # 1 year
                "policy": DataRetentionPolicy.MEDIUM_TERM.value,
                "auto_delete": True,
            },
            "backup_data": {
                "classification": DataClassification.CONFIDENTIAL.value,
                "retention_period": 30,  # 30 days
                "policy": DataRetentionPolicy.SHORT_TERM.value,
                "auto_delete": True,
            },
        }

    async def apply_retention_policy(self, data_type: str, file_path: str) -> bool:
        """Apply retention policy to data file"""
        try:
            policy = self.retention_policies.get(data_type)
            if not policy:
                logger.warning(f"No retention policy found for data type: {data_type}")
                return False

            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False

            # Calculate file age
            file_age = datetime.utcnow() - datetime.fromtimestamp(
                file_path.stat().st_mtime
            )
            age_days = file_age.days

            # Check if file should be deleted
            if policy["auto_delete"] and age_days > policy["retention_period"]:
                await self._delete_expired_data(file_path, data_type, policy)
                return True

            # Log data lifecycle event
            await self._log_data_lifecycle(file_path, data_type, policy, age_days)

            return True

        except Exception as e:
            logger.error(f"Failed to apply retention policy: {e}")
            return False

    async def _delete_expired_data(
        self, file_path: Path, data_type: str, policy: Dict[str, Any]
    ):
        """Delete expired data file"""
        try:
            # Create backup before deletion if required
            if policy.get("backup_before_delete", False):
                await self._create_backup(file_path)

            # Delete file
            file_path.unlink()
            logger.info(f"Deleted expired data file: {file_path}")

            # Log deletion event
            await self._log_data_lifecycle(
                file_path,
                data_type,
                policy,
                datetime.utcnow().timestamp(),
                action="deleted",
            )

        except Exception as e:
            logger.error(f"Failed to delete expired data: {e}")

    async def _log_data_lifecycle(
        self,
        file_path: Path,
        data_type: str,
        policy: Dict[str, Any],
        age_days: int,
        action: str = "retention_check",
    ):
        """Log data lifecycle event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "file_path": str(file_path),
            "data_type": data_type,
            "classification": policy["classification"],
            "retention_policy": policy["policy"],
            "age_days": age_days,
            "action": action,
        }
        self.data_lifecycle.append(event)

    async def _create_backup(self, file_path: Path):
        """Create backup of file before deletion"""
        backup_dir = Path("backups") / "retention"
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / f"{file_path.name}.{int(time.time())}"
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")


class DataBackupManager:
    """Data backup and recovery procedures"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backup_storage = config.get("backup_storage", "local")
        self.backup_retention_days = config.get("backup_retention_days", 30)
        self.backup_schedule = config.get("backup_schedule", "daily")
        self.backup_history = []

    async def create_backup(
        self,
        source_path: str,
        backup_type: str = BackupType.FULL.value,
        description: str = "",
    ) -> Dict[str, Any]:
        """Create data backup"""
        try:
            backup_id = f"backup_{secrets.token_hex(8)}"
            timestamp = datetime.utcnow()

            backup_info = {
                "backup_id": backup_id,
                "source_path": source_path,
                "backup_type": backup_type,
                "description": description,
                "created_at": timestamp.isoformat(),
                "status": "in_progress",
                "size_bytes": 0,
                "file_count": 0,
            }

            # Create backup based on type
            if backup_type == BackupType.FULL.value:
                backup_path = await self._create_full_backup(source_path, backup_id)
            elif backup_type == BackupType.INCREMENTAL.value:
                backup_path = await self._create_incremental_backup(
                    source_path, backup_id
                )
            else:
                backup_path = await self._create_differential_backup(
                    source_path, backup_id
                )

            if backup_path:
                backup_info["backup_path"] = str(backup_path)
                backup_info["status"] = "completed"
                backup_info["size_bytes"] = await self._calculate_backup_size(
                    backup_path
                )
                backup_info["file_count"] = await self._count_backup_files(backup_path)
            else:
                backup_info["status"] = "failed"

            self.backup_history.append(backup_info)
            logger.info(f"Created {backup_type} backup: {backup_id}")
            return backup_info

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return {"error": str(e)}

    async def _create_full_backup(
        self, source_path: str, backup_id: str
    ) -> Optional[Path]:
        """Create full backup"""
        try:
            backup_dir = Path("backups") / "full" / backup_id
            backup_dir.mkdir(parents=True, exist_ok=True)

            source = Path(source_path)
            if source.is_file():
                shutil.copy2(source, backup_dir / source.name)
            else:
                shutil.copytree(source, backup_dir / source.name)

            return backup_dir

        except Exception as e:
            logger.error(f"Failed to create full backup: {e}")
            return None

    async def _create_incremental_backup(
        self, source_path: str, backup_id: str
    ) -> Optional[Path]:
        """Create incremental backup"""
        try:
            # Find last backup
            last_backup = await self._find_last_backup()
            if not last_backup:
                # No previous backup, create full backup
                return await self._create_full_backup(source_path, backup_id)

            backup_dir = Path("backups") / "incremental" / backup_id
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Copy only changed files since last backup
            source = Path(source_path)
            last_backup_time = datetime.fromisoformat(last_backup["created_at"])

            if source.is_file():
                if source.stat().st_mtime > last_backup_time.timestamp():
                    shutil.copy2(source, backup_dir / source.name)
            else:
                for file_path in source.rglob("*"):
                    if (
                        file_path.is_file()
                        and file_path.stat().st_mtime > last_backup_time.timestamp()
                    ):
                        rel_path = file_path.relative_to(source)
                        dest_path = backup_dir / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, dest_path)

            return backup_dir

        except Exception as e:
            logger.error(f"Failed to create incremental backup: {e}")
            return None

    async def _create_differential_backup(
        self, source_path: str, backup_id: str
    ) -> Optional[Path]:
        """Create differential backup"""
        # Simplified implementation - same as incremental for now
        return await self._create_incremental_backup(source_path, backup_id)

    async def _find_last_backup(self) -> Optional[Dict[str, Any]]:
        """Find the most recent backup"""
        if not self.backup_history:
            return None

        return max(self.backup_history, key=lambda x: x["created_at"])

    async def _calculate_backup_size(self, backup_path: Path) -> int:
        """Calculate total size of backup"""
        total_size = 0
        for file_path in backup_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size

    async def _count_backup_files(self, backup_path: Path) -> int:
        """Count files in backup"""
        return len([f for f in backup_path.rglob("*") if f.is_file()])

    async def restore_backup(self, backup_id: str, destination_path: str) -> bool:
        """Restore data from backup"""
        try:
            # Find backup
            backup_info = None
            for backup in self.backup_history:
                if backup["backup_id"] == backup_id:
                    backup_info = backup
                    break

            if not backup_info:
                logger.error(f"Backup not found: {backup_id}")
                return False

            backup_path = Path(backup_info["backup_path"])
            if not backup_path.exists():
                logger.error(f"Backup path not found: {backup_path}")
                return False

            destination = Path(destination_path)
            destination.mkdir(parents=True, exist_ok=True)

            # Restore files
            if backup_path.is_file():
                shutil.copy2(backup_path, destination / backup_path.name)
            else:
                shutil.copytree(backup_path, destination / backup_path.name)

            logger.info(f"Restored backup {backup_id} to {destination_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False

    async def cleanup_old_backups(self) -> int:
        """Clean up old backups based on retention policy"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.backup_retention_days)
            deleted_count = 0

            for backup in self.backup_history[:]:
                backup_date = datetime.fromisoformat(backup["created_at"])
                if backup_date < cutoff_date:
                    # Delete backup files
                    backup_path = Path(backup.get("backup_path", ""))
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                        deleted_count += 1

                    # Remove from history
                    self.backup_history.remove(backup)

            logger.info(f"Cleaned up {deleted_count} old backups")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            return 0


class DataPrivacyManager:
    """Data privacy controls (GDPR/CCPA compliance)"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.privacy_policies = self._load_privacy_policies()
        self.data_subjects = {}  # Track data subjects
        self.consent_records = []

    def _load_privacy_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load data privacy policies"""
        return {
            "gdpr": {
                "data_minimization": True,
                "purpose_limitation": True,
                "storage_limitation": True,
                "accuracy": True,
                "consent_required": True,
                "right_to_erasure": True,
                "right_to_portability": True,
                "right_to_rectification": True,
            },
            "ccpa": {
                "right_to_know": True,
                "right_to_delete": True,
                "right_to_opt_out": True,
                "non_discrimination": True,
            },
        }

    async def register_data_subject(
        self,
        subject_id: str,
        personal_data: Dict[str, Any],
        consent_given: bool = False,
    ) -> bool:
        """Register a data subject for privacy tracking"""
        try:
            data_subject = {
                "subject_id": subject_id,
                "personal_data": personal_data,
                "consent_given": consent_given,
                "consent_date": (
                    datetime.utcnow().isoformat() if consent_given else None
                ),
                "registered_at": datetime.utcnow().isoformat(),
                "data_retention_until": None,
                "privacy_preferences": {},
            }

            self.data_subjects[subject_id] = data_subject

            # Log consent if given
            if consent_given:
                await self._log_consent(subject_id, "initial_consent", personal_data)

            logger.info(f"Registered data subject: {subject_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to register data subject: {e}")
            return False

    async def process_data_subject_request(
        self, subject_id: str, request_type: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process data subject privacy requests"""
        try:
            if subject_id not in self.data_subjects:
                return {"error": "Data subject not found"}

            data_subject = self.data_subjects[subject_id]
            response = {
                "subject_id": subject_id,
                "request_type": request_type,
                "processed_at": datetime.utcnow().isoformat(),
                "status": "completed",
            }

            if request_type == "access":
                response["data"] = await self._provide_data_access(subject_id)
            elif request_type == "rectification":
                response["status"] = await self._rectify_data(subject_id, request_data)
            elif request_type == "erasure":
                response["status"] = await self._erase_data(subject_id)
            elif request_type == "portability":
                response["data"] = await self._export_data(subject_id)
            elif request_type == "consent_withdrawal":
                response["status"] = await self._withdraw_consent(subject_id)
            else:
                response["status"] = "unsupported_request_type"

            return response

        except Exception as e:
            logger.error(f"Failed to process data subject request: {e}")
            return {"error": str(e)}

    async def _provide_data_access(self, subject_id: str) -> Dict[str, Any]:
        """Provide data access to subject"""
        data_subject = self.data_subjects[subject_id]
        return {
            "personal_data": data_subject["personal_data"],
            "data_categories": list(data_subject["personal_data"].keys()),
            "processing_purposes": ["service_provision", "analytics"],
            "retention_period": "7_years",
        }

    async def _rectify_data(self, subject_id: str, new_data: Dict[str, Any]) -> str:
        """Rectify personal data"""
        data_subject = self.data_subjects[subject_id]
        data_subject["personal_data"].update(new_data)
        data_subject["last_updated"] = datetime.utcnow().isoformat()
        return "completed"

    async def _erase_data(self, subject_id: str) -> str:
        """Erase personal data (right to be forgotten)"""
        if subject_id in self.data_subjects:
            del self.data_subjects[subject_id]
        return "completed"

    async def _export_data(self, subject_id: str) -> Dict[str, Any]:
        """Export data in portable format"""
        data_subject = self.data_subjects[subject_id]
        return {
            "export_format": "json",
            "data": data_subject["personal_data"],
            "exported_at": datetime.utcnow().isoformat(),
        }

    async def _withdraw_consent(self, subject_id: str) -> str:
        """Withdraw consent for data processing"""
        data_subject = self.data_subjects[subject_id]
        data_subject["consent_given"] = False
        data_subject["consent_withdrawn_at"] = datetime.utcnow().isoformat()
        return "completed"

    async def _log_consent(
        self, subject_id: str, consent_type: str, data: Dict[str, Any]
    ):
        """Log consent events"""
        consent_record = {
            "subject_id": subject_id,
            "consent_type": consent_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data_categories": list(data.keys()),
            "ip_address": "unknown",  # Would be captured in real implementation
        }
        self.consent_records.append(consent_record)


class DataLineageTracker:
    """Data lineage tracking and provenance"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.lineage_graph = {}
        self.data_operations = []

    async def track_data_operation(
        self,
        operation_id: str,
        operation_type: str,
        input_data: List[str],
        output_data: List[str],
        metadata: Dict[str, Any],
    ) -> bool:
        """Track a data operation for lineage"""
        try:
            operation = {
                "operation_id": operation_id,
                "operation_type": operation_type,
                "input_data": input_data,
                "output_data": output_data,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat(),
                "execution_time": metadata.get("execution_time", 0),
                "user_id": metadata.get("user_id"),
            }

            self.data_operations.append(operation)

            # Update lineage graph
            for input_file in input_data:
                if input_file not in self.lineage_graph:
                    self.lineage_graph[input_file] = {
                        "produced_by": [],
                        "consumed_by": [],
                    }
                self.lineage_graph[input_file]["consumed_by"].append(operation_id)

            for output_file in output_data:
                if output_file not in self.lineage_graph:
                    self.lineage_graph[output_file] = {
                        "produced_by": [],
                        "consumed_by": [],
                    }
                self.lineage_graph[output_file]["produced_by"].append(operation_id)

            logger.info(f"Tracked data operation: {operation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to track data operation: {e}")
            return False

    async def get_data_lineage(self, data_file: str) -> Dict[str, Any]:
        """Get lineage information for a data file"""
        try:
            if data_file not in self.lineage_graph:
                return {"error": "Data file not found in lineage"}

            lineage_info = {
                "data_file": data_file,
                "produced_by": [],
                "consumed_by": [],
                "full_lineage": await self._build_full_lineage(data_file),
            }

            # Get operation details
            for operation_id in self.lineage_graph[data_file]["produced_by"]:
                operation = next(
                    (
                        op
                        for op in self.data_operations
                        if op["operation_id"] == operation_id
                    ),
                    None,
                )
                if operation:
                    lineage_info["produced_by"].append(operation)

            for operation_id in self.lineage_graph[data_file]["consumed_by"]:
                operation = next(
                    (
                        op
                        for op in self.data_operations
                        if op["operation_id"] == operation_id
                    ),
                    None,
                )
                if operation:
                    lineage_info["consumed_by"].append(operation)

            return lineage_info

        except Exception as e:
            logger.error(f"Failed to get data lineage: {e}")
            return {"error": str(e)}

    async def _build_full_lineage(self, data_file: str) -> Dict[str, Any]:
        """Build complete lineage tree for data file"""
        visited = set()
        lineage_tree = {"file": data_file, "children": [], "parents": []}

        # Find all ancestors (files that produced this file)
        await self._find_ancestors(data_file, lineage_tree["parents"], visited)

        # Find all descendants (files produced from this file)
        await self._find_descendants(data_file, lineage_tree["children"], visited)

        return lineage_tree

    async def _find_ancestors(self, data_file: str, ancestors: List, visited: Set):
        """Recursively find ancestor files"""
        if data_file in visited:
            return
        visited.add(data_file)

        for operation_id in self.lineage_graph[data_file]["produced_by"]:
            operation = next(
                (
                    op
                    for op in self.data_operations
                    if op["operation_id"] == operation_id
                ),
                None,
            )
            if operation:
                for input_file in operation["input_data"]:
                    ancestors.append(
                        {
                            "file": input_file,
                            "operation": operation,
                        }
                    )
                    await self._find_ancestors(input_file, ancestors, visited)

    async def _find_descendants(self, data_file: str, descendants: List, visited: Set):
        """Recursively find descendant files"""
        if data_file in visited:
            return
        visited.add(data_file)

        for operation_id in self.lineage_graph[data_file]["consumed_by"]:
            operation = next(
                (
                    op
                    for op in self.data_operations
                    if op["operation_id"] == operation_id
                ),
                None,
            )
            if operation:
                for output_file in operation["output_data"]:
                    descendants.append(
                        {
                            "file": output_file,
                            "operation": operation,
                        }
                    )
                    await self._find_descendants(output_file, descendants, visited)


class DataManagementService:
    """Comprehensive data management service"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.version_manager = DataVersionManager(config)
        self.retention_manager = DataRetentionManager(config)
        self.backup_manager = DataBackupManager(config)
        self.privacy_manager = DataPrivacyManager(config)
        self.lineage_tracker = DataLineageTracker(config)

    async def initialize_data_management(self) -> bool:
        """Initialize all data management components"""
        try:
            # Initialize DVC
            dvc_initialized = await self.version_manager.initialize_dvc()
            if not dvc_initialized:
                logger.warning(
                    "DVC initialization failed, continuing without version control"
                )

            logger.info("Data management system initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize data management: {e}")
            return False

    async def get_data_management_dashboard(self) -> Dict[str, Any]:
        """Get data management dashboard data"""
        return {
            "version_control": {
                "dvc_initialized": (self.version_manager.data_dir / ".dvc").exists(),
                "tracked_files": len(self.version_manager.version_history),
            },
            "retention_policies": {
                "total_policies": len(self.retention_manager.retention_policies),
                "lifecycle_events": len(self.retention_manager.data_lifecycle),
            },
            "backup_status": {
                "total_backups": len(self.backup_manager.backup_history),
                "last_backup": (
                    self.backup_manager.backup_history[-1]["created_at"]
                    if self.backup_manager.backup_history
                    else None
                ),
            },
            "privacy_compliance": {
                "data_subjects": len(self.privacy_manager.data_subjects),
                "consent_records": len(self.privacy_manager.consent_records),
            },
            "data_lineage": {
                "tracked_files": len(self.lineage_tracker.lineage_graph),
                "total_operations": len(self.lineage_tracker.data_operations),
            },
        }
