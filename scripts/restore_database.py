#!/usr/bin/env python3
"""
Database Restore Script (Phase 7.3)
Restore database from backup files
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseRestore:
    """Database restore manager"""
    
    def __init__(
        self,
        backup_file: Path,
        postgres_host: str = "localhost",
        postgres_port: int = 5432,
        postgres_db: str = "amas",
        postgres_user: str = "postgres",
        postgres_password: Optional[str] = None
    ):
        self.backup_file = Path(backup_file)
        self.postgres_host = postgres_host
        self.postgres_port = postgres_port
        self.postgres_db = postgres_db
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password or os.getenv("POSTGRES_PASSWORD", "")
    
    def restore_postgres(self, drop_existing: bool = False) -> bool:
        """Restore PostgreSQL database from backup"""
        try:
            if not self.backup_file.exists():
                logger.error(f"❌ Backup file not found: {self.backup_file}")
                return False
            
            # Set password via environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = self.postgres_password
            
            if drop_existing:
                # Drop existing database (WARNING: Destructive!)
                logger.warning("⚠️  Dropping existing database...")
                drop_cmd = [
                    "psql",
                    "-h", self.postgres_host,
                    "-p", str(self.postgres_port),
                    "-U", self.postgres_user,
                    "-d", "postgres",  # Connect to postgres DB
                    "-c", f"DROP DATABASE IF EXISTS {self.postgres_db};"
                ]
                subprocess.run(drop_cmd, env=env, check=True)
                
                # Create new database
                create_cmd = [
                    "psql",
                    "-h", self.postgres_host,
                    "-p", str(self.postgres_port),
                    "-U", self.postgres_user,
                    "-d", "postgres",
                    "-c", f"CREATE DATABASE {self.postgres_db};"
                ]
                subprocess.run(create_cmd, env=env, check=True)
            
            # Restore from backup
            if self.backup_file.suffix == ".gz":
                # Compressed backup
                cmd = [
                    "pg_restore",
                    "-h", self.postgres_host,
                    "-p", str(self.postgres_port),
                    "-U", self.postgres_user,
                    "-d", self.postgres_db,
                    "--clean",  # Clean before restore
                    "--if-exists",  # Don't error if objects don't exist
                    str(self.backup_file)
                ]
            else:
                # SQL dump
                cmd = [
                    "psql",
                    "-h", self.postgres_host,
                    "-p", str(self.postgres_port),
                    "-U", self.postgres_user,
                    "-d", self.postgres_db,
                    "-f", str(self.backup_file)
                ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ PostgreSQL restore completed: {self.backup_file}")
                return True
            else:
                logger.error(f"❌ PostgreSQL restore failed: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"❌ PostgreSQL restore error: {e}", exc_info=True)
            return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AMAS Database Restore")
    parser.add_argument("backup_file", type=Path, help="Backup file to restore")
    parser.add_argument("--postgres-host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--postgres-port", type=int, default=5432, help="PostgreSQL port")
    parser.add_argument("--postgres-db", default="amas", help="PostgreSQL database")
    parser.add_argument("--postgres-user", default="postgres", help="PostgreSQL user")
    parser.add_argument("--drop-existing", action="store_true", help="Drop existing database before restore")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Confirm destructive operation
    if args.drop_existing:
        confirm = input("⚠️  WARNING: This will DROP the existing database. Continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Restore cancelled")
            return
    
    # Run restore
    restore = DatabaseRestore(
        backup_file=args.backup_file,
        postgres_host=args.postgres_host,
        postgres_port=args.postgres_port,
        postgres_db=args.postgres_db,
        postgres_user=args.postgres_user
    )
    
    success = restore.restore_postgres(drop_existing=args.drop_existing)
    if success:
        print("✅ Database restore completed successfully")
    else:
        print("❌ Database restore failed")
        exit(1)


if __name__ == "__main__":
    main()

