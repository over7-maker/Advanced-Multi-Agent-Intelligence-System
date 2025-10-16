#!/bin/bash
# BULLETPROOF AI Provider Availability Check
# Fixes the bash -e exit issue when checking for unset API keys

set +e  # CRITICAL: do not exit on non-zero tests
echo "🔍 Checking AI provider availability..."
available_providers=0

check_key() {
  local name="$1"
  local value="${!name}"
  if [ -n "$value" ] && [ ${#value} -gt 10 ]; then
    echo "✅ $name: Available (${#value} chars)"
    available_providers=$((available_providers+1))
  else
    echo "ℹ️ $name: Not set or too short"
  fi
}

echo "🔎 Checking all 19 supported providers..."
for key in DEEPSEEK_API_KEY CEREBRAS_API_KEY NVIDIA_API_KEY CODESTRAL_API_KEY GLM_API_KEY GROK_API_KEY COHERE_API_KEY CLAUDE_API_KEY GPT4_API_KEY GEMINI_API_KEY GROQAI_API_KEY MISTRAL_API_KEY KIMI_API_KEY QWEN_API_KEY GPTOSS_API_KEY GEMINIAI_API_KEY GEMINI2_API_KEY GROQ2_API_KEY CHUTES_API_KEY; do
  check_key "$key"
done

echo ""
echo "📊 PROVIDER AVAILABILITY SUMMARY:"
echo "  Available: $available_providers/19 providers"
echo ""

if [ "$available_providers" -eq 0 ]; then
  echo "🚨 CRITICAL: NO REAL AI PROVIDERS AVAILABLE!"
  echo "❌ Please add at least one valid API key to repository secrets:"
  echo "   - DEEPSEEK_API_KEY (recommended - free tier available)"
  echo "   - NVIDIA_API_KEY (high performance)"
  echo "   - CEREBRAS_API_KEY (fast inference)"
  echo "   - CODESTRAL_API_KEY (code specialist)"
  echo "   - COHERE_API_KEY, CLAUDE_API_KEY, GPT4_API_KEY"
  echo ""
  echo "🔗 Get free API keys:"
  echo "   - DeepSeek: https://platform.deepseek.com"
  echo "   - Cerebras: https://cloud.cerebras.ai"
  echo "   - OpenRouter: https://openrouter.ai (supports multiple models)"
  echo ""
  echo "📊 Current keys status:"
  echo "   DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:+SET (${#DEEPSEEK_API_KEY} chars)} ${DEEPSEEK_API_KEY:-NOT SET}"
  echo "   NVIDIA_API_KEY: ${NVIDIA_API_KEY:+SET (${#NVIDIA_API_KEY} chars)} ${NVIDIA_API_KEY:-NOT SET}"
  echo "   CEREBRAS_API_KEY: ${CEREBRAS_API_KEY:+SET (${#CEREBRAS_API_KEY} chars)} ${CEREBRAS_API_KEY:-NOT SET}"
  exit 1
else
  echo "✅ Real AI providers available ($available_providers) - proceeding with analysis"
  echo "AVAILABLE_PROVIDERS=$available_providers" >> $GITHUB_ENV
fi