# Testing Guide - Phase 1: Self-Debugging Features

**Phase 1 Complete!** Your Desktop Agent now has intelligent error recovery capabilities.

## What's New

### 🔧 New Debugging Tools

1. **interpret_error** - Analyzes error messages using Claude
2. **search_solution_online** - Finds solutions from Stack Overflow/docs/GitHub
3. **try_alternative_installation** - Tries apt → snap → flatpak → pip → source
4. **verify_dependencies** - Checks if all dependencies are satisfied
5. **fix_broken_packages** - Fixes broken package installations
6. **install_with_retry** - High-level tool with automatic retry and recovery

### 🧠 Enhanced Agent Prompt

The agent now:
- Doesn't give up after first failure
- Interprets errors intelligently
- Tries alternative approaches
- Searches for solutions online
- Reports what it tried and how it fixed issues

---

## Access Your Enhanced Agent

**URL:** http://localhost:8000

You'll see:
- **Left panel:** AI Chatbot (now with debugging!)
- **Right panel:** VNC Desktop

---

## Test Scenarios

### Test 1: Package Not Found (Easy)

**What to test:** Agent finds correct package name

```
You: "Install Docker"
Expected behavior:
1. Tries "docker" → fails (package not found)
2. Uses interpret_error or search_package
3. Finds correct package "docker.io"
4. Installs docker.io successfully
5. Verifies installation
```

**Success criteria:** ✅ Installs docker.io without user intervention

---

### Test 2: Alternative Installation Method (Medium)

**What to test:** Agent tries snap when apt fails

```
You: "Install VS Code"
Expected behavior:
1. Tries apt → fails (not in default repos)
2. Uses try_alternative_installation
3. Tries snap install → succeeds
4. Verifies code is installed
```

**Success criteria:** ✅ Installs via snap after apt fails

---

### Test 3: Broken Package Recovery (Medium)

**What to test:** Agent fixes broken package state

First, break packages in VNC terminal:
```bash
# In VNC terminal (right panel)
sudo apt-get install -y some-fake-package
# This will create broken state
```

Then test:
```
You: "Install nginx"
Expected behavior:
1. Tries to install → may fail due to broken packages
2. Uses fix_broken_packages
3. Retries installation → succeeds
```

**Success criteria:** ✅ Fixes broken state and installs nginx

---

### Test 4: Dependency Verification (Advanced)

**What to test:** Agent checks dependencies

```
You: "Check dependencies for postgresql"
Expected behavior:
1. Uses verify_dependencies("postgresql")
2. Lists all dependencies
3. Shows which are installed/missing
```

**Success criteria:** ✅ Shows comprehensive dependency info

---

### Test 5: Intelligent Retry (Advanced)

**What to test:** High-level retry with auto-recovery

```
You: "Use install_with_retry to install git"
Expected behavior:
1. Uses install_with_retry tool
2. Handles any errors automatically
3. Reports detailed installation log
```

**Success criteria:** ✅ Installs successfully with retry logic

---

### Test 6: Error Interpretation (Advanced)

**What to test:** Agent analyzes custom error

```
You: "Interpret this error: 'E: Unable to locate package foo-bar-baz'"
Expected behavior:
1. Uses interpret_error
2. Explains: package not found in repos
3. Suggests solutions: check name, add PPA, use alternative
```

**Success criteria:** ✅ Provides actionable solutions

---

### Test 7: Complex Installation (Expert)

**What to test:** Multi-step installation with debugging

```
You: "Setup Python development environment with pip, virtualenv, and build tools"
Expected behavior:
1. Checks what's already installed
2. Updates package lists
3. Installs multiple packages
4. If any fail, uses debugging tools
5. Verifies each installation
6. Reports comprehensive setup info
```

**Success criteria:** ✅ Complete environment ready, handles any errors

---

## Expected Behavior Changes

### Before Phase 1 (Old Agent):
```
You: "Install Docker"
Agent:
  - Runs: sudo apt-get install -y docker
  - Error: "Unable to locate package docker"
  - Reports: ❌ Installation failed
  - STOPS ❌
```

### After Phase 1 (Enhanced Agent):
```
You: "Install Docker"
Agent:
  - Runs: sudo apt-get install -y docker
  - Error: "Unable to locate package docker"
  - Interprets error: "Package name is docker.io"
  - Runs: sudo apt-get install -y docker.io
  - Success: ✅
  - Verifies installation
  - Reports: "Installed docker.io. Note: package name is 'docker.io' not 'docker'"
```

---

## How to Test

### Quick Test (5 minutes)
```
1. Open http://localhost:8000
2. Try: "Install Docker"
3. Watch it self-correct when "docker" package not found
4. Verify it installs "docker.io" automatically
```

### Comprehensive Test (30 minutes)
```
1. Try all test scenarios above
2. Note which debugging tools get used
3. Check if agent explains what it tried
4. Verify installations work
```

### Stress Test (Advanced)
```
1. Intentionally break package state
2. Request multiple installations
3. Use incorrect package names
4. See how agent recovers
```

---

## Monitoring Agent Behavior

### What to Watch For:

**Good Signs:** ✅
- Agent doesn't give up after first failure
- Uses interpret_error when commands fail
- Tries alternative installation methods
- Explains what went wrong and how it fixed it
- Provides detailed results

**Areas to Improve:**
- If agent gives up too quickly
- If it doesn't use debugging tools
- If it repeats the same failed command
- If it doesn't explain what it tried

---

## Debugging the Debugger

If something doesn't work:

### Check Container Logs:
```bash
docker logs -f agent-chatbot
```

### Check if Tools are Available:
```
You: "List all available tools"
Expected: Should see debugging tools listed
```

### Test Individual Tools:
```
You: "Use interpret_error to analyze: package not found"
You: "Use search_solution_online for docker installation"
You: "Try alternative installation for code"
```

---

## Next Steps (Future Phases)

After validating Phase 1 works:

**Phase 2: Vision & GUI Control**
- Screenshot capture
- Claude Vision analysis
- Mouse/keyboard control
- Element detection

**Phase 3: File Operations**
- Bulk file organization
- Intelligent categorization
- Batch operations

**Phase 4: Form Filling**
- Form field detection
- Data extraction
- Human-in-the-loop approval

---

## Success Metrics

Phase 1 is successful if:

- ✅ Agent recovers from >70% of installation failures
- ✅ Uses debugging tools automatically (without being told)
- ✅ Tries at least 2 different approaches before giving up
- ✅ Explains what went wrong and how it fixed it
- ✅ Successfully installs packages that would have failed before

---

## Common Test Commands

```bash
# Start the agent
./run-chatbot.sh

# Stop the agent
docker stop agent-chatbot

# View logs
docker logs -f agent-chatbot

# Restart after code changes
docker stop agent-chatbot && ./run-chatbot.sh

# Check running containers
docker ps
```

---

## Reporting Issues

If you find bugs or unexpected behavior:

1. Note what you asked the agent to do
2. Note what error occurred
3. Check which debugging tools were used (or not used)
4. Share the agent's response
5. Check docker logs for detailed error messages

---

## Example Test Session

```
Terminal:
$ ./run-chatbot.sh
✅ Container started at http://localhost:8000

Browser (http://localhost:8000):

You: "Install Docker"

Agent:
  I'll install Docker for you. Let me start by checking if it's already installed.

  [Uses verify_installation("docker")]
  Docker is not installed.

  [Uses update_package_lists()]
  ✅ Package lists updated

  [Uses execute_shell_command("sudo apt-get install -y docker")]
  ❌ Command failed: Unable to locate package docker

  [Uses interpret_error("Unable to locate package docker", "installing Docker")]
  🔍 Error Analysis:
  Root Cause: Package name mismatch
  Why: Docker package is named "docker.io" in Ubuntu repos
  Solutions:
  1. Try: sudo apt-get install -y docker.io
  2. Alternative: Install from Docker's official repository
  3. Fallback: Use snap install docker

  [Uses execute_shell_command("sudo apt-get install -y docker.io")]
  ✅ Command successful

  [Uses verify_installation("docker")]
  ✅ docker is installed
  Location: /usr/bin/docker
  Version: Docker version 24.0.7

  ✅ Docker has been successfully installed! The package name in Ubuntu is "docker.io" rather than "docker".

  To verify: open a terminal in the VNC panel (right side) and run:
  docker --version

VNC Panel (right side):
  [Open terminal]
  $ docker --version
  Docker version 24.0.7, build afdd53b
```

---

## Congratulations!

You've successfully implemented Phase 1: Self-Debugging Installation Agent!

The agent now has the intelligence to:
- 🧠 Analyze errors
- 🔍 Search for solutions
- 🔄 Try alternatives
- 🛠️ Fix broken states
- 📊 Report detailed results

**Ready to test?** Open http://localhost:8000 and try the test scenarios above!
