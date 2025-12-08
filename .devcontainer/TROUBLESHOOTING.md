# Devcontainer Build Troubleshooting

## Current Issue: Build Failing

If you're getting build errors, try these solutions:

### Solution 1: Use Simple Configuration (No Features)

If the build with features is failing, temporarily rename files:

```bash
# Backup current config
mv .devcontainer/devcontainer.json .devcontainer/devcontainer.json.with-features

# Use simple config
cp .devcontainer/devcontainer-simple.json .devcontainer/devcontainer.json
```

Then try reopening in container again.

### Solution 2: Build Manually to See Errors

```bash
# Build manually to see actual error
docker compose -f .devcontainer/docker-compose.yml build --progress=plain

# Or build Dockerfile directly
docker build -f .devcontainer/Dockerfile -t amas-dev .
```

### Solution 3: Check Docker Logs

```bash
# Check Docker daemon logs
docker info

# Check if base image can be pulled
docker pull python:3.11-slim

# Test network connectivity
docker run --rm python:3.11-slim python --version
```

### Solution 4: Disable Features Temporarily

Edit `.devcontainer/devcontainer.json` and comment out features:

```json
{
  "features": {
    // "ghcr.io/devcontainers/features/docker-in-docker:2": {
    //   "version": "latest"
    // },
    // "ghcr.io/devcontainers/features/github-cli:1": {
    //   "version": "latest"
    // }
  }
}
```

### Solution 5: Increase Build Timeout

If build is timing out, it might be network issues. Check:
- Docker Desktop proxy settings
- Internet connectivity
- Firewall blocking Docker

### Solution 6: Clear Docker Cache

```bash
# Clear build cache
docker builder prune -a

# Remove old images
docker image prune -a
```

## Common Build Errors

### Error: "Failed to copy requirements files"
**Fix:** Already fixed - requirements are now installed in post-create script

### Error: "Node.js installation failed"
**Fix:** Already fixed - Node.js installation is now optional

### Error: "Feature installation timeout"
**Fix:** Try Solution 4 (disable features) or Solution 1 (use simple config)

### Error: "Network timeout during build"
**Fix:** Check proxy settings, try Solution 6 (clear cache), or build offline

## Quick Test

To test if the Dockerfile works:

```bash
docker build -f .devcontainer/Dockerfile -t test-build .
```

If this works, the issue is with the devcontainer features or compose setup.

## Getting Help

If issues persist:
1. Check Docker Desktop is running
2. Check Docker has enough resources (Settings → Resources)
3. Try building without features first
4. Check network/proxy settings

