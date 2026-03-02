# HELM v2.0 - Architecture Setup Guide

## Directory Structure Created

```
Agent/
├── helm/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── logger.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── head_agent.py
│   │   ├── strategy_agent.py
│   │   └── finance_agent.py
│   │
│   ├── validation/
│   │   ├── __init__.py
│   │   └── validator.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── interface.py
│   │   ├── local_model.py
│   │   └── api_model.py
│   │
│   ├── environment/
│   │   ├── __init__.py
│   │   └── system_check.py
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   └── dashboard.py
│   │
│   └── tests/
│       ├── __init__.py
│       ├── scenario_1.py
│       ├── scenario_2.py
│       └── scenario_3.py
│
├── model_test/
│   ├── __init__.py
│   └── test_llm_gpu.py
│
├── helm_gpu/ (Virtual Environment - DO NOT MODIFY)
│
└── test_env/ (Old environment - DO NOT MODIFY)
```

## PowerShell Setup Commands

### Step 1: Create Directory Structure
```powershell
# Navigate to Agent folder
Set-Location "C:\Users\Lenovo\OneDrive\Desktop\Agent"

# Create main HELM directories
New-Item -ItemType Directory -Path "helm" -Force
New-Item -ItemType Directory -Path "helm\agents" -Force
New-Item -ItemType Directory -Path "helm\validation" -Force
New-Item -ItemType Directory -Path "helm\models" -Force
New-Item -ItemType Directory -Path "helm\environment" -Force
New-Item -ItemType Directory -Path "helm\storage" -Force
New-Item -ItemType Directory -Path "helm\ui" -Force
New-Item -ItemType Directory -Path "helm\tests" -Force
New-Item -ItemType Directory -Path "model_test" -Force

# Verify structure created
Tree /F helm
```

### Step 2: Verify Virtual Environment
```powershell
# Check helm_gpu is intact
Test-Path "C:\Users\Lenovo\OneDrive\Desktop\Agent\helm_gpu\Scripts\Activate.ps1"

# Activate environment
& "C:\Users\Lenovo\OneDrive\Desktop\Agent\helm_gpu\Scripts\Activate.ps1"
```

### Step 3: Test Installation
```powershell
# Verify CUDA setup
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"

# List installed packages
pip list | grep -E "torch|transformers|numpy"
```

## VS Code Workspace Setup

### Step 1: Open Workspace
```powershell
# From Agent directory, open VS Code
code .
```

### Step 2: Select Python Interpreter
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `Python: Select Interpreter`
3. Choose: `.venv/bin/python` or the helm_gpu path:
   ```
   C:\Users\Lenovo\OneDrive\Desktop\Agent\helm_gpu\Scripts\python.exe
   ```

### Step 3: Verify Interpreter Selection
In VS Code Terminal:
```powershell
# Activate helm_gpu
& "C:\Users\Lenovo\OneDrive\Desktop\Agent\helm_gpu\Scripts\Activate.ps1"

# Verify CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPUs:', torch.cuda.device_count())"
```

## Running Tests

### From Terminal (with activated environment):
```powershell
# Test Scenario 1: System Check
python helm/tests/scenario_1.py

# Test Scenario 2: Model Loading
python helm/tests/scenario_2.py

# Test Scenario 3: Agent Orchestration
python helm/tests/scenario_3.py

# Run GPU Test
python model_test/test_llm_gpu.py
```

## Project Files Summary

| File | Purpose |
|------|---------|
| `helm/__init__.py` | Package initialization |
| `helm/main.py` | Application entry point |
| `helm/config.py` | Centralized configuration |
| `helm/logger.py` | Logging management |
| `helm/agents/*` | Agent implementations (empty stubs) |
| `helm/validation/*` | Input/output validation |
| `helm/models/*` | Model abstraction layer |
| `helm/environment/*` | System checks (GPU, CUDA, dependencies) |
| `helm/storage/*` | Database abstraction |
| `helm/ui/*` | Dashboard interface |
| `helm/tests/*` | Test scenarios |
| `model_test/test_llm_gpu.py` | GPU testing script |

## Important Notes

✅ **Virtual Environment Status**
- `helm_gpu` remains untouched and fully functional
- All packages installed: PyTorch, Transformers, CUDA support
- GPU acceleration ready to use

✅ **Module Imports**
- All files use relative imports (ready for packaging)
- `__init__.py` files set up proper module exposure
- Import pattern: `from helm.agents import HeadAgent`

✅ **Next Steps**
1. Activate helm_gpu environment
2. Open VS Code workspace
3. Select helm_gpu as Python interpreter
4. Run test scenarios to verify setup
5. Begin implementing business logic in stub classes

## Troubleshooting

### If CUDA not detected:
```powershell
# Verify CUDA installation
nvidia-smi

# Reinstall torch with CUDA support (if needed)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### If imports fail:
```powershell
# Verify helm_gpu is activated
(helm_gpu) PS> 

# Check PYTHONPATH
[System.Environment]::GetEnvironmentVariable("PYTHONPATH")

# Test import
python -c "from helm.config import Config; print('Import successful')"
```

---

**Status**: ✅ HELM v2.0 Architecture Successfully Scaffolded
**Virtual Environment**: ✅ helm_gpu Ready
**GPU Support**: ✅ Configured
**Next Phase**: Implement business logic in stub classes
