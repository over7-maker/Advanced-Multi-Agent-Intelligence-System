# 🔧 Install Node.js & npm - Quick Guide

## ⚠️ **Node.js/npm Not Installed**

Your container doesn't have Node.js/npm installed. Here are installation options:

---

## 🚀 **Option 1: Install via apt (Recommended for Debian/Ubuntu)**

```bash
# Update package list
apt-get update

# Install Node.js 18.x and npm
apt-get install -y nodejs npm

# Verify installation
node --version
npm --version
```

---

## 🚀 **Option 2: Install via NodeSource (Latest LTS)**

```bash
# Install Node.js 18.x from NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

---

## 🚀 **Option 3: Install via nvm (Node Version Manager)**

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload shell
source ~/.bashrc

# Install Node.js 18
nvm install 18
nvm use 18

# Verify installation
node --version
npm --version
```

---

## 🚀 **Option 4: Use Docker/DevContainer with Node.js**

If you're using a devcontainer, update your `.devcontainer/devcontainer.json`:

```json
{
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "18"
    }
  }
}
```

---

## ✅ **After Installation**

Once Node.js is installed:

```bash
cd frontend
npm install
npm run dev
```

---

## 🔍 **Check Current Status**

```bash
# Check if Node.js is installed
which node
node --version

# Check if npm is installed
which npm
npm --version
```

---

**Choose the option that works best for your environment! 🚀**

