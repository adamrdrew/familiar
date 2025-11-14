# Quick Start: Fast Mode & Browser Performance Configuration

**Feature**: 004-fast-mode-performance  
**For**: Developers who want faster test execution

---

## Overview

Familiar supports two ways to optimize test performance:

1. **`--fast` CLI flag**: Enable LLM flash mode and speed-optimized prompts
2. **`browser_profile` in suite.yaml**: Configure browser timing (page loads, action delays)

These can be used independently or combined for maximum speed.

---

## Quick Examples

### 1. Enable Fast Mode (Quickest Way)

```bash
# Run tests with speed optimizations
familiar run tests/login-flow --fast
```

**What it does**:
- Enables LLM flash mode (skip verbose thinking)
- Injects speed optimization prompt
- Uses your existing browser timing (or defaults)

**When to use**:
- Development/iteration
- Fast, stable applications
- When you have a fast LLM provider (Groq, Gemini Flash)

### 2. Configure Browser Timing (Persistent)

Edit your `suite.yaml`:

```yaml
name: "Fast Login Test"
browser_profile:
  minimum_wait_page_load_time: 0.2  # Fast page loads
  wait_between_actions: 0.2          # Quick actions
```

Run normally:
```bash
familiar run tests/login-flow
```

**What it does**:
- Reduces browser wait times
- Persists across all test runs
- No CLI flag needed

**When to use**:
- Production test suites for fast apps
- CI/CD pipelines
- When you want permanent speed optimization

### 3. Combine Both (Maximum Speed)

**suite.yaml**:
```yaml
name: "Ultra Fast Test"
temperature: 0.0
browser_profile:
  minimum_wait_page_load_time: 0.1
  wait_between_actions: 0.1
```

**Command**:
```bash
familiar run tests/login-flow --fast
```

**Result**: 2-3x faster execution!

---

## Detailed Walkthroughs

### Walkthrough 1: Adding Fast Mode to Existing Test

**Starting point**: You have a working test that takes 30 seconds

**Step 1**: Try fast mode
```bash
familiar run my-test --fast
```

**Step 2**: Observe results
```
Suite completed in 12.4s - All tests passed!
```

**Result**: ~60% faster! ✅

---

### Walkthrough 2: Configuring Browser Timing

**Starting point**: You have a fast, stable web app

**Step 1**: Add browser_profile to your suite.yaml

```yaml
name: "My Test Suite"
temperature: 0.5
step_timeout: 60

# Add this section
browser_profile:
  minimum_wait_page_load_time: 0.2
  wait_between_actions: 0.2
  headless: true
```

**Step 2**: Run your test
```bash
familiar run my-test
```

**Step 3**: Measure improvement
```
Before: 28.5s
After:  15.2s
Speedup: 47%
```

**Result**: Permanent speed improvement without changing test logic! ✅

---

### Walkthrough 3: Debugging with Fast Mode

**Scenario**: Fast mode makes your test fail

**Step 1**: Run with verbose to see what's happening
```bash
familiar run my-test --fast --verbose
```

**Step 2**: Identify the issue
```
[ERROR] Element not found: #submit-button
```

**Diagnosis**: Page loads too slowly for 0.1s wait

**Step 3**: Adjust timing in suite.yaml
```yaml
browser_profile:
  minimum_wait_page_load_time: 0.5  # Increase from 0.1
  wait_between_actions: 0.1          # Keep action delay low
```

**Step 4**: Test again
```bash
familiar run my-test --fast
```

**Result**: Passes! You found the right balance. ✅

---

## Configuration Recipes

### Recipe 1: Development (Fast Iteration)

**Goal**: Fastest possible feedback while developing tests

```yaml
# suite.yaml
name: "Dev Test"
temperature: 0.0
step_timeout: 30
browser_profile:
  minimum_wait_page_load_time: 0.1
  wait_between_actions: 0.1
  headless: false  # See what's happening
```

```bash
familiar run my-test --fast --no-headless
```

**Expected speed**: 2-3x faster than default

---

### Recipe 2: CI/CD (Fast & Reliable)

**Goal**: Fast execution without sacrificing reliability

```yaml
# suite.yaml
name: "CI Test"
temperature: 0.5
step_timeout: 60
retry_policy:
  type: "fixed"
  max_retries: 1  # One retry for flaky tests
browser_profile:
  minimum_wait_page_load_time: 0.3
  wait_between_actions: 0.2
  headless: true
```

```bash
familiar run my-test --fast
```

**Expected speed**: 50-70% faster with good reliability

---

### Recipe 3: Slow/Unreliable Site

**Goal**: Maximum reliability for challenging sites

```yaml
# suite.yaml
name: "Slow Site Test"
temperature: 0.5
step_timeout: 120
retry_policy:
  type: "exponential"
  max_retries: 3
browser_profile:
  minimum_wait_page_load_time: 3.0   # Long page load waits
  wait_between_actions: 2.0          # Conservative action delays
  headless: true
```

```bash
# DON'T use --fast flag for unreliable sites
familiar run my-test
```

**Expected speed**: Slower, but much more reliable

---

### Recipe 4: Mixed (Fast Pages, Slow LLM)

**Goal**: Optimize browser, keep standard LLM behavior

```yaml
# suite.yaml
name: "Mixed Optimization"
temperature: 0.5
browser_profile:
  minimum_wait_page_load_time: 0.2
  wait_between_actions: 0.2
```

```bash
# No --fast flag (keep full LLM reasoning)
familiar run my-test
```

**Expected speed**: Moderate speedup from browser timing only

---

## LLM Provider Recommendations

### For Maximum Speed with --fast

**Option 1: Groq (Recommended)**
```bash
export FAMILIAR_MODEL_PROVIDER="groq"
export FAMILIAR_MODEL="meta-llama/llama-4-maverick-17b-128e-instruct"
export GROQ_API_KEY="your-api-key"
```

**Speed**: Ultra-fast inference (100-200 tokens/sec)

**Option 2: Google Gemini Flash**
```bash
export FAMILIAR_MODEL_PROVIDER="google"
export FAMILIAR_MODEL="gemini-flash-lite-latest"
export GOOGLE_API_KEY="your-api-key"
```

**Speed**: Very fast inference (80-150 tokens/sec)

**Option 3: Anthropic Claude (Standard)**
```bash
export FAMILIAR_MODEL_PROVIDER="anthropic"
export FAMILIAR_MODEL="claude-sonnet-4-0"
export ANTHROPIC_API_KEY="your-api-key"
```

**Speed**: Moderate (40-60 tokens/sec), but highest quality

---

## Performance Measurement

### Baseline Measurement

```bash
# Run without optimizations
time familiar run my-test

# Result: 28.5 seconds
```

### Fast Mode Measurement

```bash
# Run with --fast flag only
time familiar run my-test --fast

# Result: 15.2 seconds
# Speedup: 47%
```

### Full Optimization Measurement

```bash
# Run with --fast + browser_profile (0.1s waits)
time familiar run my-test --fast

# Result: 10.8 seconds
# Speedup: 62%
```

---

## Common Patterns

### Pattern 1: Fast Mode by Default

Add an alias to your shell config:

```bash
# .bashrc or .zshrc
alias frun='familiar run --fast'
```

Usage:
```bash
frun my-test          # Runs with fast mode
familiar run my-test  # Runs standard mode when needed
```

### Pattern 2: Environment-Specific Timing

**Development (dev-suite.yaml)**:
```yaml
browser_profile:
  minimum_wait_page_load_time: 0.1
  wait_between_actions: 0.1
```

**Production (prod-suite.yaml)**:
```yaml
browser_profile:
  minimum_wait_page_load_time: 1.0
  wait_between_actions: 1.0
```

### Pattern 3: Conditional Fast Mode in CI

```bash
#!/bin/bash
# ci-test.sh

if [ "$CI_ENVIRONMENT" == "development" ]; then
  familiar run tests/ --all --fast
else
  familiar run tests/ --all  # Standard mode for production
fi
```

---

## Troubleshooting

### Q: Fast mode makes my tests fail

**A**: Your pages may load slowly. Increase browser wait times:

```yaml
browser_profile:
  minimum_wait_page_load_time: 0.5  # Increase from 0.1
```

### Q: --fast doesn't seem faster

**A**: Check your LLM provider. Slow providers see minimal speedup:

```bash
# Check current provider
echo $FAMILIAR_MODEL_PROVIDER

# Try Groq for maximum speed
export FAMILIAR_MODEL_PROVIDER="groq"
export GROQ_API_KEY="your-key"
```

### Q: How much speedup should I expect?

**A**: Depends on scenario:
- Simple 3-step test: 50-70% faster
- Complex 10-step test: 30-50% faster
- Heavy network/rendering: 20-30% faster

### Q: Is fast mode safe for production?

**A**: Use with caution:
- ✅ Development: Always use fast mode
- ✅ Stable apps: Safe to use
- ⚠️  Complex scenarios: Test carefully
- ❌ Flaky tests: Stick to standard mode

---

## Migration Guide

### From Standard to Fast Mode

**Before**:
```bash
familiar run my-test
# Takes 30 seconds
```

**After**:
```bash
familiar run my-test --fast
# Takes 12 seconds
```

**No changes to test files needed!**

### From Default Timing to Custom Timing

**Before** (suite.yaml):
```yaml
name: "My Test"
temperature: 0.5
# No browser_profile
```

**After** (suite.yaml):
```yaml
name: "My Test"
temperature: 0.5
browser_profile:
  minimum_wait_page_load_time: 0.2
  wait_between_actions: 0.2
```

**No test logic changes needed!**

---

## Next Steps

1. **Try fast mode**: Run existing test with `--fast` flag
2. **Measure speedup**: Compare execution times
3. **Tune timing**: Add `browser_profile` to suite.yaml
4. **Choose LLM**: Switch to Groq or Gemini Flash for maximum speed
5. **Update CI**: Add `--fast` to CI scripts for faster pipelines

---

## Related Documentation

- [Feature Specification](./spec.md) - Full requirements
- [Implementation Plan](./plan.md) - Technical details
- [Research](./research.md) - Performance analysis
- [Browser Profile Contract](./contracts/browser-profile-config.yaml) - Configuration schema
- [CLI Contract](./contracts/cli-interface.md) - CLI flag specification

