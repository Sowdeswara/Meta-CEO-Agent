# HELM v2.0 Quick Reference

## Installation & Setup (30 seconds)

```powershell
# 1. Navigate to Agent folder
cd C:\Users\Lenovo\OneDrive\Desktop\Agent

# 2. Activate environment
& helm_gpu\Scripts\Activate.ps1

# 3. Run test
python helm\tests\scenario_1.py
```

## Basic Usage (3 minutes)

```python
from helm import HELM

# Initialize
helm = HELM(enable_local_model=True)

# Make a decision
decision = helm.process_decision(
    prompt="Your business question",
    context={
        'revenue': 100000,
        'costs': 60000,
        'investment': 50000,
        'expected_returns': 80000
    },
    required_fields=['revenue', 'costs', 'investment', 'expected_returns']
)

# Use the decision
print(f"Decision: {decision['decision_text']}")
print(f"Confidence: {decision['confidence']:.0%}")
print(f"ROI: {decision['roi_estimate']:.0%}")
print(f"Status: {decision['status']}")

# Shutdown
helm.shutdown()
```

## Core Classes

```python
# Main System
from helm import HELM
helm = HELM()  # Initialize entire system
helm.process_decision(prompt, context, fields)  # Make decision
helm.shutdown()  # Cleanup

# Models
from helm.models import LocalModel, APIModel
model = LocalModel()  # Local GPU model
model.load()
response = model.infer("prompt")

# Agents
from helm.agents import HeadAgent, StrategyAgent, FinanceAgent
head = HeadAgent()  # Orchestration
strategy = StrategyAgent()  # Strategy analysis
finance = FinanceAgent()  # Financial metrics

# Validation
from helm.validation import Validator
validator = Validator()
score = validator.calculate_validation_score(data, fields)

# Database
from helm.storage import Database
db = Database()
db.insert_decision(decision)
recent = db.get_recent_decisions(limit=10)

# Configuration
from helm import Config
config = Config()
print(config.validation_threshold)  # 0.70
print(config.default_model)  # microsoft/phi-2
```

## Configuration

### Environment Variables

```bash
# GPU
USE_LOCAL_MODEL=True
QUANTIZATION=8bit

# Validation
VALIDATION_THRESHOLD=0.70
MAX_RETRIES=2

# Model
DEFAULT_MODEL=microsoft/phi-2
MAX_NEW_TOKENS=200
TEMPERATURE=0.3

# System
LOG_LEVEL=INFO
ENABLE_DASHBOARD=True
```

### In Code

```python
config = Config()
config.validation_threshold = 0.75
config.max_retries = 3
config.quantization = "4bit"
```

## Decision Types

### Strategic Decision
```python
helm.process_decision(
    "Should we expand into Southeast?",
    {
        'objectives': ['Expand', 'Increase revenue'],
        'constraints': ['Budget: $500K'],
        'resources': ['Team', 'Technology'],
        'timeline': 'Q2-Q3'
    },
    ['objectives', 'constraints']
)
# → Routes to StrategyAgent
```

### Financial Decision
```python
helm.process_decision(
    "Calculate ROI on $100K investment",
    {
        'revenue': 500000,
        'costs': 300000,
        'investment': 100000,
        'expected_returns': 180000,
        'timeframe_years': 3
    },
    ['revenue', 'costs', 'investment', 'expected_returns']
)
# → Routes to FinanceAgent
# → Calculates profit margin, ROI, payback period
```

## Decision Output

```python
decision = {
    'decision_id': 'abc123de',  # Unique ID
    'agent_used': 'finance',     # Which agent processed
    'decision_text': 'Strong recommendation...',  # The decision
    'confidence': 0.85,          # 0-1 confidence level
    'roi_estimate': 0.45,        # Estimated ROI
    'risk_level': 'low',         # low, medium, high
    'status': 'accepted',        # accepted, rejected, escalated
    'validation_score': 0.82,    # Validation score
    'reasoning': {...},          # Full reasoning dict
    'timestamp': '2026-03-02...' # ISO timestamp
}
```

## Validation Scoring

Decision passes if: **weighted_score ≥ 0.70**

```
Score = 20% schema + 20% fields + 20% numeric + 
         20% confidence + 20% roi
```

If rejected:
- Retry (max 2)
- Then escalate

## Common Patterns

### Get Statistics
```python
stats = helm.get_statistics()
print(stats['total_decisions'])
print(stats['acceptance_rate'])
print(stats['average_confidence'])
print(stats['average_roi'])
```

### Query Decision History
```python
# Recent decisions
recent = helm.get_decision_history(limit=10)

# By agent type
strategy = helm.db.get_decisions_by_agent('strategy')
finance = helm.db.get_decisions_by_agent('finance')

# By status
accepted = helm.db.get_decisions_by_status('accepted')
rejected = helm.db.get_decisions_by_status('rejected')
```

### Custom Validation
```python
from helm.validation import Validator

validator = Validator(config)

# Calculate score
score = validator.calculate_validation_score(
    {'revenue': 100000, 'confidence': 0.85},
    ['revenue']
)
print(f"Score: {score.weighted_score}")

# Validate decision
result = validator.validate_decision(
    data, required_fields, max_retries=2
)
print(f"Passed: {result.passed()}")
```

### Custom Agent
```python
from helm.agents import StrategyAgent

class CustomAgent(StrategyAgent):
    def process(self, decision_input):
        # Your custom logic
        return super().process(decision_input)

# Register
custom = CustomAgent()
helm.head_agent.register_agent(AgentType.STRATEGY, custom)
```

## Testing

```bash
# Full integration test
python helm\tests\scenario_1.py

# Model loading test  
python helm\tests\scenario_2.py

# Agent & validation test
python helm\tests\scenario_3.py

# GPU test
python model_test\test_llm_gpu.py
```

## Troubleshooting

### CUDA Not Available
```powershell
nvidia-smi  # Check drivers
# If needed: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Import Error
```powershell
# Make sure helm_gpu is activated
(helm_gpu) PS>

# Test import
python -c "from helm import HELM; print('OK')"
```

### Model Load Fails
```python
# Check VRAM
from helm.environment import SystemCheck
check = SystemCheck()
vram = check.get_available_vram()
print(f"Available VRAM: {vram}GB")

# Fallback to API will happen automatically
# Or try 4-bit quantization
```

### Database Error
```python
# Restart connection
helm.db.disconnect()
helm.db.connect()

# Or check file permissions
ls -la helm/storage/helm_decisions.db
```

## Performance Tips

### Faster Responses
1. Use 4-bit quantization: `QUANTIZATION=4bit`
2. Reduce tokens: `MAX_NEW_TOKENS=100`
3. Use API fallback exclusively
4. Cache prompts if repeated

### Better Quality
1. Use 8-bit quantization: `QUANTIZATION=8bit`
2. Increase tokens: `MAX_NEW_TOKENS=300`
3. Lower temperature: `TEMPERATURE=0.1`
4. Increase validation threshold: `VALIDATION_THRESHOLD=0.80`

### Production Ready
1. Set `DEBUG_MODE=False`
2. Use `LOG_LEVEL=INFO`
3. Enable `ENABLE_DASHBOARD=True`
4. Configure API backup
5. Set up monitoring

## File Locations

```
Agent/
├── helm/
│   ├── main.py                 # Main HELM class
│   ├── config.py               # Configuration
│   ├── agents/                 # Agent implementations
│   ├── models/                 # Model layer
│   ├── storage/                # Database
│   │   └── helm_decisions.db   # SQLite database
│   ├── tests/                  # Test scenarios
│   └── logs/                   # Log files (auto-created)
├── SETUP_GUIDE.md              # Initial setup
├── README_HELM_v2.md           # Full documentation
└── IMPLEMENTATION_SUMMARY.md   # Implementation details
```

## Resources

- **Full Docs**: README_HELM_v2.md
- **Setup Guide**: SETUP_GUIDE.md
- **Implementation**: IMPLEMENTATION_SUMMARY.md
- **Examples**: helm/tests/scenario_*.py

## Commands Reference

```powershell
# Activate environment
& helm_gpu\Scripts\Activate.ps1

# Run tests
python helm\tests\scenario_1.py  # System test
python helm\tests\scenario_2.py  # Model test
python helm\tests\scenario_3.py  # Agent test

# Enter Python
python

# Run main
python -m helm.main

# Check system
python -c "from helm.environment import SystemCheck; SystemCheck().check_environment()"
```

## Key Concepts

**Decision Authority**: Deterministic rule-based logic, not probabilistic  
**Validation Score**: Weighted 5-factor scoring (0-1)  
**Agents**: Specialized processors for strategic vs financial decisions  
**Models**: Optional LLM for explanation only  
**Fallback**: API model if local model unavailable  
**Storage**: All decisions persisted in SQLite  
**Retries**: Max 2 attempts to achieve passing validation  
**Escalation**: Unresolvable decisions marked as ESCALATED

## Success Criteria

✅ System initializes without errors
✅ All tests pass
✅ CUDA detected and working
✅ Database stores decisions
✅ Decisions have confidence scores
✅ Dashboard displays results
✅ Fallback works if VRAM insufficient

---

**Start Here**: `python helm\tests\scenario_1.py`
