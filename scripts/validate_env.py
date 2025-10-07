#!/usr/bin/env python3
"""
Environment Validation Script for AMAS

Validates that all required environment variables and dependencies are properly configured.
Supports minimal configuration modes for easier setup.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from amas.config.minimal_config import MinimalMode, get_minimal_config_manager
from amas.config.ai_config import get_ai_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"Python version: {sys.version}")
    return True


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "asyncio",
        "aiohttp",
        "pydantic",
        "numpy",
        "pandas",
        "scikit-learn",
        "psycopg2-binary",
        "redis",
        "neo4j",
        "fastapi",
        "uvicorn",
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            logger.info(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"✗ {package} - Not installed")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Install with: pip install -r requirements.txt")
        return False
    
    logger.info("All required packages are installed")
    return True


def check_environment_variables(mode: MinimalMode = MinimalMode.BASIC):
    """Check environment variables for minimal mode"""
    minimal_manager = get_minimal_config_manager()
    validation_result = minimal_manager.validate_minimal_setup(mode)
    
    logger.info(f"Validating environment for {mode.value} mode...")
    
    if validation_result["valid"]:
        logger.info("✓ Environment validation passed")
        logger.info(f"Available providers: {', '.join(validation_result['available_providers'])}")
    else:
        logger.error("✗ Environment validation failed")
        for warning in validation_result["warnings"]:
            logger.error(f"  - {warning}")
    
    if validation_result["recommendations"]:
        logger.info("Recommendations:")
        for rec in validation_result["recommendations"]:
            logger.info(f"  - {rec}")
    
    return validation_result["valid"]


def check_database_connections():
    """Check database connectivity"""
    logger.info("Checking database connections...")
    
    # Check PostgreSQL
    try:
        import psycopg2
        db_host = os.getenv("AMAS_DB_HOST", "localhost")
        db_port = os.getenv("AMAS_DB_PORT", "5432")
        db_user = os.getenv("AMAS_DB_USER", "amas")
        db_password = os.getenv("AMAS_DB_PASSWORD", "amas123")
        db_name = os.getenv("AMAS_DB_NAME", "amas")
        
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        conn.close()
        logger.info("✓ PostgreSQL connection successful")
    except Exception as e:
        logger.error(f"✗ PostgreSQL connection failed: {e}")
        return False
    
    # Check Redis
    try:
        import redis
        redis_host = os.getenv("AMAS_REDIS_HOST", "localhost")
        redis_port = int(os.getenv("AMAS_REDIS_PORT", "6379"))
        
        r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        r.ping()
        logger.info("✓ Redis connection successful")
    except Exception as e:
        logger.error(f"✗ Redis connection failed: {e}")
        return False
    
    # Check Neo4j
    try:
        from neo4j import GraphDatabase
        neo4j_host = os.getenv("AMAS_NEO4J_HOST", "localhost")
        neo4j_port = os.getenv("AMAS_NEO4J_PORT", "7687")
        neo4j_user = os.getenv("AMAS_NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("AMAS_NEO4J_PASSWORD", "amas123")
        
        driver = GraphDatabase.driver(
            f"bolt://{neo4j_host}:{neo4j_port}",
            auth=(neo4j_user, neo4j_password)
        )
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        logger.info("✓ Neo4j connection successful")
    except Exception as e:
        logger.error(f"✗ Neo4j connection failed: {e}")
        return False
    
    return True


def check_file_permissions():
    """Check file system permissions"""
    logger.info("Checking file permissions...")
    
    required_dirs = ["logs", "data", "artifacts"]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✓ Created directory: {dir_name}")
            except Exception as e:
                logger.error(f"✗ Cannot create directory {dir_name}: {e}")
                return False
        else:
            if not os.access(dir_path, os.W_OK):
                logger.error(f"✗ Directory {dir_name} is not writable")
                return False
            logger.info(f"✓ Directory {dir_name} is writable")
    
    return True


def generate_env_template(mode: MinimalMode = MinimalMode.BASIC):
    """Generate environment template file"""
    minimal_manager = get_minimal_config_manager()
    template = minimal_manager.get_environment_setup_guide(mode)
    
    template_file = f".env.{mode.value}.template"
    with open(template_file, "w") as f:
        f.write(template)
    
    logger.info(f"Generated environment template: {template_file}")
    return template_file


def generate_docker_compose(mode: MinimalMode = MinimalMode.BASIC):
    """Generate minimal docker-compose file"""
    minimal_manager = get_minimal_config_manager()
    compose_content = minimal_manager.get_minimal_docker_compose(mode)
    
    compose_file = f"docker-compose.{mode.value}.yml"
    with open(compose_file, "w") as f:
        f.write(compose_content)
    
    logger.info(f"Generated docker-compose file: {compose_file}")
    return compose_file


def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(description="Validate AMAS environment setup")
    parser.add_argument(
        "--mode",
        choices=["basic", "standard", "full"],
        default="basic",
        help="Minimal configuration mode (default: basic)"
    )
    parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Skip database connection checks"
    )
    parser.add_argument(
        "--generate-templates",
        action="store_true",
        help="Generate environment and docker-compose templates"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    mode = MinimalMode(args.mode)
    
    # Validation results
    results = {
        "python_version": False,
        "dependencies": False,
        "environment": False,
        "databases": False,
        "file_permissions": False,
        "overall": False,
    }
    
    # Run validations
    logger.info("Starting AMAS environment validation...")
    logger.info(f"Mode: {mode.value}")
    
    # Check Python version
    results["python_version"] = check_python_version()
    
    # Check dependencies
    results["dependencies"] = check_dependencies()
    
    # Check environment variables
    results["environment"] = check_environment_variables(mode)
    
    # Check database connections (if not skipped)
    if not args.skip_db:
        results["databases"] = check_database_connections()
    else:
        logger.info("Skipping database connection checks")
        results["databases"] = True
    
    # Check file permissions
    results["file_permissions"] = check_file_permissions()
    
    # Overall result
    results["overall"] = all(results.values())
    
    # Generate templates if requested
    if args.generate_templates:
        generate_env_template(mode)
        generate_docker_compose(mode)
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if results["overall"]:
            logger.info("🎉 All validations passed! AMAS is ready to run.")
        else:
            logger.error("❌ Some validations failed. Please fix the issues above.")
            sys.exit(1)
    
    return results["overall"]


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
