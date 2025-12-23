# Optional Devcontainer Features

## Features Disabled by Default

To avoid build issues, features are currently disabled. You can enable them if needed:

### To Enable Features

Edit `.devcontainer/devcontainer.json` and uncomment:

```json
"features": {
  "ghcr.io/devcontainers/features/docker-in-docker:2": {
    "version": "latest"
  },
  "ghcr.io/devcontainers/features/github-cli:1": {
    "version": "latest"
  }
}
```

### What Each Feature Provides

1. **docker-in-docker**: Allows running Docker commands inside the container
   - Only needed if you need to build/test Docker images inside the container
   - Adds significant build time and complexity

2. **github-cli**: Provides `gh` command for GitHub operations
   - Only needed if you want to use GitHub CLI inside the container
   - Can be installed manually if needed: `apt-get install gh`

### Manual Installation (If Needed)

If you need these tools, install them in the post-create script or manually:

```bash
# Install GitHub CLI manually
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
apt update && apt install gh
```

Docker-in-docker is more complex and usually not needed for development.

