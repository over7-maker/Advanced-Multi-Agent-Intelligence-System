# AMAS Development Container

This directory contains the Dev Container configuration for the AMAS project.

## Purpose

The Dev Container provides a consistent, reproducible development environment with:
- Python 3.11 on Debian Bullseye
- Pre-configured VS Code extensions (Python, Ruff, YAML, GitHub Pull Requests and Issues)
- Docker-in-Docker support for containerized builds
- GitHub CLI for repository operations
- Automated dependency installation and setup

## Configuration Overview

### Lifecycle Commands

- **`initializeCommand`**: Validates Python version (3.11+)
- **`onCreateCommand`**: Performs optional setup (creates `.env` from `.env.example` if available)
  - Non-blocking: Warns if setup.sh missing, continues
- **`postCreateCommand`**: Required setup (installs dependencies)
  - Strict: Fails if setup.sh missing or execution fails
- **`updateContentCommand`**: Updates dependencies when container content changes
  - Strict: Fails if setup.sh missing or execution fails

### Resource Limits

- **Memory**: 4GB (sufficient for Python development with dependencies)
- **CPUs**: 2 cores (balanced for compilation and parallelism)

### Timeouts

All lifecycle commands have a 300-second (5-minute) timeout to prevent indefinite hangs.
- **Default**: 300 seconds (5 minutes) is reasonable for most dependency installations
- **For Large Projects**: If dependency installation takes longer, you can override the timeout in `devcontainer.json`:
  ```json
  "postCreateCommand": "... timeout 600 .devcontainer/setup.sh postCreate ..."
  ```
- **Note**: Large Python projects with complex dependencies (numpy, pandas, torch) may require up to 10 minutes on cold starts with slow internet

### Security Considerations

1. **Script Execution**: `setup.sh` is executed with explicit permissions (`chmod +x`)
   - **Important**: Review `setup.sh` in PRs before merging. The script runs with container user privileges.
   - For high-security environments, consider adding checksum validation before execution
2. **Timeout Protection**: All commands timeout after 5 minutes to prevent indefinite hangs
   - Note: Timeouts prevent hangs but don't protect against malicious payloads completing within the time window
   - Combine with minimal required privileges and input validation
3. **Error Handling**: Fail-fast behavior for critical setup steps prevents partial/insecure configurations
4. **Non-root User**: Container runs as `vscode` user (not root) to limit privilege escalation risk
5. **Image Updates**: Base images should be regularly updated to include security patches (see "Image Tagging" above)

### Image Tagging

The image tag `1-3.11-bullseye` is standard practice for Dev Containers:
- Microsoft maintains backward compatibility
- Tags are updated with security patches automatically
- For stricter reproducibility, consider pinning to a specific digest in production

### Features

- **Docker-in-Docker**: Required for building container images inside the dev container
- **GitHub CLI**: Useful for PR operations and repository management

## Usage

1. Open the project in VS Code
2. When prompted, click "Reopen in Container"
3. The container will automatically:
   - Install Python dependencies
   - Set up the virtual environment
   - Configure VS Code settings

## Troubleshooting

### Setup Script Fails

If `setup.sh` fails:
- Check logs: `/tmp/devcontainer-setup.log`
- Verify `requirements.txt` exists
- Ensure network connectivity for pip installs

### Container Won't Start

- Verify JSON syntax: `python3 -m json.tool .devcontainer/devcontainer.json`
- Check Docker has sufficient resources (4GB RAM, 2 CPUs)
- Review VS Code Dev Container logs

### Timeout Issues

If setup takes longer than 5 minutes:
- Check network connectivity
- Review dependency installation logs
- Consider increasing timeout if needed (not recommended)

## Customization

You can override settings locally by modifying `.devcontainer/devcontainer.json`:

### Example: Increase Memory Allocation
```json
{
  "runArgs": [
    "--memory=8g",
    "--cpus=4"
  ]
}
```

### Example: Add Additional Ports
```json
{
  "forwardPorts": [8000, 8080, 5432],
  "portsAttributes": {
    "5432": {
      "label": "PostgreSQL",
      "onAutoForward": "notify"
    }
  }
}
```

### Example: Add Environment Variables
```json
{
  "remoteEnv": {
    "CUSTOM_VAR": "value"
  }
}
```

## Best Practices

1. **Keep `setup.sh` simple**: It should be idempotent and handle errors gracefully
2. **Review changes**: Always review `setup.sh` changes in PRs before merging (security consideration)
3. **Update dependencies**: Regularly update `requirements.txt` and `requirements-dev.txt`
4. **Monitor resource usage**: Adjust `runArgs` if your system has limited resources
5. **For large projects**: Consider increasing memory to 6-8GB and CPUs to 4 cores for better performance with type checking and parallel test execution
