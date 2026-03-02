# HELM v2.0 - Hierarchical Executive-Level Meta-Agent

**A Deterministic Supervisory Agentic AI System**

## Overview

HELM v2.0 is a production-grade decision authority system with deterministic logic at its core. Decision authority resides strictly in rule-based logic, while optional LLMs serve only as linguistic augmentation modules for explanation generation.

### Key Characteristics

✅ **Deterministic Decision Authority** - All decisions made through transparent rule-based logic  
✅ **Hierarchical Supervision** - HeadAgent orchestrates specialized agents  
✅ **Weighted Validation** - Deterministic scoring with configurable thresholds  
✅ **Bounded Retries** - Max 2 retries with escalation on failure  
✅ **LLM Augmentation** - Optional explanations, not decision-making  
✅ **GPU/CUDA Support** - VRAM-aware local model loading (RTX 3050 6GB tested)  
✅ **SQLite Persistence** - All decisions stored with complete audit trail  
✅ **Streamlit Dashboard** - Read-only visualization of decisions  

---

## Architecture

### Core Components

```
helm/
├── main.py                    # HELM class - Main orchestration
├── config.py                  # Configuration management
├── logger.py                  # Production-grade logging
├── schemas.py                 # Pydantic data models
│
├── agents/
│   ├── head_agent.py         # Deterministic routing & validation
│   ├── strategy_agent.py      # Strategic analysis (deterministic)
│   └── finance_agent.py       # Financial metrics & ROI calculation
│
├── validation/
│   └── validator.py           # Weighted scoring & rule-based validation
│
├── models/
│   ├── interface.py           # Abstract model interface
│   ├── local_model.py         # Local GPU inference (VRAM-aware)
│   └── api_model.py           # API fallback with error handling
│
├── environment/
│   └── system_check.py        # CUDA, GPU, dependencies check
│
├── storage/
│   └── database.py            # SQLite decision persistence
│
└── ui/
    └── dashboard.py           # Streamlit visualization
```

### Decision Flow

```
User Input
    ↓
HeadAgent (Deterministic Routing)
    ├─→ Validate Input (Weighted Scoring)
    │
    ├─→ Classify Task (Keyword-based Rules)
    │
    ├─→ Route to Specialized Agent
    │   ├─→ StrategyAgent (Strategic Analysis)
    │   └─→ FinanceAgent (Financial Metrics)
    │
    ├─→ Validate Output
    │
    ├─→ Generate Explanation (Optional LLM)
    │
    └─→ Store in Database
        ↓
    Structured Decision Object
```

---

## Configuration

### Environment Variables

```bash
# GPU/CUDA Settings
USE_GPU=True
USE_LOCAL_MODEL=True
GPU_MEMORY_FRACTION=0.9
DEVICE_MAP=auto

# Model Configuration
DEFAULT_MODEL=microsoft/phi-2
QUANTIZATION=8bit  # or 4bit, 16bit, none
MAX_NEW_TOKENS=200
CONTEXT_WINDOW=2048
TEMPERATURE=0.3

# Validation Thresholds
VALIDATION_THRESHOLD=0.70
CONFIDENCE_THRESHOLD=0.65
ROI_THRESHOLD=0.0

# Retry Logic
MAX_RETRIES=2
RETRY_BACKOFF=1.0

# System Settings
DEBUG_MODE=False
LOG_LEVEL=INFO
ENABLE_DASHBOARD=True
DASHBOARD_HOST=localhost
DASHBOARD_PORT=8501

# API Model (Fallback)
API_ENDPOINT=https://api.openai.com/v1/chat/completions
API_KEY=your_api_key
API_MODEL=gpt-3.5-turbo

# Currency
DEFAULT_CURRENCY=USD
```

### Configuration in Code

```python
from helm import Config

config = Config()
print(config.validation_threshold)  # 0.70
print(config.default_model)          # microsoft/phi-2
print(config.max_retries)            # 2
```

---

## Usage

### Basic Usage

```python
from helm import HELM

# Initialize HELM
helm = HELM(enable_local_model=True, enable_dashboard=False)

# Process a decision
decision = helm.process_decision(
    prompt="Should we expand into new market?",
    context={
        'objectives': ['Increase revenue', 'Grow market share'],
        'constraints': ['Budget limit: $500K', 'Timeline: 12 months'],
        'resources': ['Team of 5', 'Technology platform'],
        'revenue': 100000,
        'costs': 60000,
        'investment': 50000,
        'expected_returns': 80000,
        'timeframe_years': 2
    },
    required_fields=['revenue', 'costs', 'investment', 'expected_returns']
)

# Access decision
print(f"Decision ID: {decision['decision_id']}")
print(f"Agent: {decision['agent_used']}")
print(f"Status: {decision['status']}")
print(f"Confidence: {decision['confidence']:.2%}")
print(f"ROI Estimate: {decision['roi_estimate']:.2%}")

# Get statistics
stats = helm.get_statistics()
print(f"Total decisions: {stats['total_decisions']}")
print(f"Acceptance rate: {stats['accepted_decisions'] / stats['total_decisions']:.1%}")

# Shutdown
helm.shutdown()
```

### Advanced Usage: Custom Decision Processing

```python
from helm import HELM
from helm.schemas import DecisionInput

helm = HELM()

# Create detailed decision input
decision_input = DecisionInput(
    prompt="Complex business decision",
    context={
        'user_id': 'user_123',
        'session_id': 'session_001',
        'revenue': 500000,
        'costs': 300000,
        'investment': 150000,
        'expected_returns': 250000,
        'timeframe_years': 3,
        'objectives': ['Profitability', 'Market expansion'],
        'constraints': ['Limited budget', 'Competitive pressure'],
        'resources': ['Experienced team', 'Modern infrastructure']
    },
    user_id='user_123',
    session_id='session_001',
    required_fields=['revenue', 'costs', 'investment', 'expected_returns']
)

# Process through head agent
decision = helm.head_agent.process(decision_input)

# Access structured decision
print(f"Decision: {decision.decision_text}")
print(f"Reasoning: {decision.reasoning}")
print(f"Risk: {decision.risk_level}")
```

### Accessing Decision History

```python
from helm import HELM

helm = HELM()

# Get recent decisions
recent = helm.get_decision_history(limit=10)
for decision in recent:
    print(f"{decision['decision_id']}: {decision['status']}")

# Query database directly
from helm.storage.database import Database

db = Database()
db.connect()

# Get decisions by agent
strategy_decisions = db.get_decisions_by_agent('strategy')
print(f"Strategy decisions: {len(strategy_decisions)}")

# Get decisions by status
accepted = db.get_decisions_by_status('accepted')
print(f"Accepted decisions: {len(accepted)}")

db.disconnect()
```

---

## Validation System

### Deterministic Weighted Scoring

Validation score is calculated as:

$$\text{Score} = 0.20 \times s_1 + 0.20 \times s_2 + 0.20 \times s_3 + 0.20 \times s_4 + 0.20 \times s_5$$

Where:
- $s_1$ = Schema completeness (0-1)
- $s_2$ = Required fields present (0-1)
- $s_3$ = Numeric field validity (0-1)
- $s_4$ = Confidence level (0-1)
- $s_5$ = ROI viability (0-1)

**Decision Rules:**
- If Score ≥ threshold (default 0.70): **ACCEPT**
- If Score < threshold: **RETRY** (max 2)
- If retries exhausted: **ESCALATE**

### Custom Validation

```python
from helm import HELM
from helm.validation import Validator

helm = HELM()
validator = Validator(helm.config)

# Calculate validation score
data = {
    'revenue': 100000,
    'costs': 60000,
    'investment': 50000,
    'confidence': 0.85,
    'roi': 0.60
}

score = validator.calculate_validation_score(
    data,
    required_fields=['revenue', 'costs', 'investment']
)

print(f"Score: {score.weighted_score:.2f}")
print(f"Passed (≥0.70): {score.weighted_score >= 0.70}")

# Assess risk
risk = validator.assess_risk(data)
print(f"Risk level: {risk}")  # low, medium, high
```

---

## Agents

### HeadAgent - Orchestration

```python
from helm.agents import HeadAgent
from helm.schemas import DecisionInput

head_agent = HeadAgent(config=helm.config, validator=validator)

# Task classification (deterministic keyword-based)
agent_type = head_agent.classify_task("Should we expand into Southeast?")
# Returns: AgentType.STRATEGY

# Process decision
decision = head_agent.process(decision_input)
# Returns: StructuredDecision
```

**Task Classification Rules:**
- **FINANCE**: Keywords like "profit", "revenue", "ROI", "cashflow", "margin"
- **STRATEGY**: Keywords like "strategy", "plan", "objective", "goal", "roadmap"

### StrategyAgent - Strategic Analysis

```python
from helm.agents import StrategyAgent

strategy_agent = StrategyAgent(config=helm.config, llm=helm.local_model)

# Analyze strategic factors
analysis = strategy_agent.analyze({
    'objectives': ['Expand market', 'Increase revenue'],
    'constraints': ['Budget limit', 'Timeline pressure'],
    'resources': ['Team', 'Technology'],
    'timeline': 'Q2-Q3 2024'
})

print(f"Strategy score: {analysis['strategy_score']:.2f}")
print(f"Feasibility: {analysis['feasibility_score']:.2f}")
print(f"Resource score: {analysis['resource_score']:.2f}")

# Generate plan
plan = strategy_agent.generate_plan(
    objectives=['Increase market share', 'Launch new product']
)
print(f"Plan ID: {plan['plan_id']}")
print(f"Timeline: {plan['timeline']}")
```

### FinanceAgent - Financial Analysis

```python
from helm.agents import FinanceAgent

finance_agent = FinanceAgent(config=helm.config, llm=helm.local_model)

# Calculate financial metrics
metrics = finance_agent.calculate_metrics({
    'revenue': 500000,
    'costs': 300000,
    'investment': 100000,
    'expected_returns': 180000,
    'timeframe_years': 3
})

print(f"Profit Margin: {metrics['profit_margin']:.2%}")
print(f"ROI: {metrics['roi']:.2%}")
print(f"Annualized ROI: {metrics['annualized_roi']:.2%}")
print(f"Payback Period: {metrics['payback_period']:.1f} years")
print(f"Viability Score: {metrics['overall_score']:.2f}")

# Analyze financials
analysis = finance_agent.analyze_financials({...})
```

**Financial Metrics Calculated:**
- Profit Margin: `(Revenue - Costs) / Revenue`
- ROI: `(Expected Returns - Investment) / Investment`
- Annualized ROI: Compounded annual return
- Payback Period: Years to recover investment
- Contribution Margin: `(Revenue - Costs) / Revenue`
- Overall Viability Score: Weighted combination of above

---

## Model Layer

### Local Model (GPU)

```python
from helm.models import LocalModel
from helm.schemas import ModelConfig

# Configure model
config = ModelConfig(
    model_id="microsoft/phi-2",
    quantization="8bit",
    max_new_tokens=200,
    context_window=2048,
    temperature=0.3
)

# Load model
model = LocalModel(config)
if model.load():
    # Run inference
    output = model.infer("Explain profit margins in business")
    print(output)
    
    # Get config
    print(model.get_config())
    
    # Unload
    model.unload()
else:
    print("Failed to load model (insufficient VRAM or missing packages)")
```

**VRAM Management:**
- Checks available VRAM before loading
- Supports 4-bit and 8-bit quantization
- Automatic CUDA cache management
- Graceful fallback to CPU if needed

### API Model (Fallback)

```python
from helm.models import APIModel

# Configure API
model = APIModel(
    api_endpoint="https://api.openai.com/v1/chat/completions",
    api_key="your_api_key",
    model_name="gpt-3.5-turbo"
)

if model.load():
    output = model.infer("Your prompt here", max_tokens=200)
    print(output)
    model.unload()
```

**Fallback Strategy:**
1. Try to load local model
2. If VRAM insufficient → fallback to API
3. If API unavailable → return error message
4. System continues operation regardless

---

## Database

### SQLite Storage

```python
from helm.storage.database import Database
from helm.schemas import StructuredDecision

db = Database(db_path="path/to/helm_decisions.db")
db.connect()

# Insert decision
db.insert_decision(decision)

# Retrieve decision
decision = db.get_decision("decision_id_123")

# Query decisions
recent = db.get_recent_decisions(limit=10)
strategy_decisions = db.get_decisions_by_agent("strategy")
accepted = db.get_decisions_by_status("accepted")

# Statistics
stats = db.get_statistics()
print(f"Total: {stats['total_decisions']}")
print(f"Accepted: {stats['accepted_decisions']}")
print(f"Avg Confidence: {stats['average_confidence']:.2%}")

db.disconnect()
```

**Tables:**
- `decisions` - All decisions with full details
- `decision_history` - Decision status changes
- `metadata` - System metadata

---

## Testing

### Run All Scenarios

```bash
# Scenario 1: Complete System Integration
python helm/tests/scenario_1.py

# Scenario 2: Model Loading & LLM Integration
python helm/tests/scenario_2.py

# Scenario 3: Agent Orchestration & Validation
python helm/tests/scenario_3.py

# GPU Test
python model_test/test_llm_gpu.py
```

### Expected Output

```
================================================================
SCENARIO 1: COMPLETE SYSTEM INTEGRATION TEST
================================================================

[TEST 1] Initializing HELM v2.0...
✓ HELM initialized successfully

[TEST 2] Processing strategic decision...
✓ Strategic decision processed

[TEST 3] Processing financial decision...
✓ Financial decision processed

[TEST 4] Retrieving decision history...
✓ Retrieved 2 decisions from database

[TEST 5] Getting system statistics...
✓ Statistics retrieved:
  Total decisions: 2
  Accepted: 2
  Average confidence: 0.75
  Average ROI: 12.50%

[TEST 6] Shutting down HELM...
✓ HELM shutdown complete

================================================================
SCENARIO 1: ALL TESTS PASSED ✓
================================================================
```

---

## Troubleshooting

### CUDA Not Detected

```bash
# Check CUDA availability
nvidia-smi

# Verify PyTorch CUDA support
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Insufficient VRAM

```
⚠ Local model loading failed
→ System automatically falls back to API model
→ May experience slower responses but system continues
```

**Solutions:**
- Use 4-bit quantization instead of 8-bit
- Reduce max_new_tokens
- Switch to smaller model (e.g., microsoft/phi)
- Use API-only mode

### Import Errors

```bash
# Verify environment is activated
(helm_gpu) PS>

# Check PYTHONPATH
echo $PYTHONPATH

# Test imports
python -c "from helm import HELM; print('✓ Import successful')"
```

---

## Performance

### Benchmarks (RTX 3050 6GB)

| Task | Time | Memory |
|------|------|--------|
| System initialization | ~2s | 100MB |
| Model loading (8-bit) | ~5s | 4.2GB |
| Single inference | ~2-3s | +0.5GB |
| Decision processing | ~0.5s | +20MB |
| Database insert | ~10ms | +1MB |

---

## Security Considerations

1. **Decision Audit Trail** - All decisions stored with timestamps
2. **No Private LLM Calls** - Local model stays local
3. **Configurable Thresholds** - Control what gets accepted
4. **Bounded Retries** - Prevents infinite loops
5. **Error Escalation** - Failed decisions logged and escalated

---

## Production Deployment

### Checklist

- [ ] Test all scenarios pass
- [ ] CUDA verified working
- [ ] Database path configured
- [ ] Validation thresholds reviewed
- [ ] Logging level set to INFO
- [ ] API keys configured (if using API fallback)
- [ ] Performance benchmarks run
- [ ] Monitoring configured
- [ ] Backup strategy in place

### Production Config

```python
# Environment variables
export USE_GPU=True
export USE_LOCAL_MODEL=True
export VALIDATION_THRESHOLD=0.75
export LOG_LEVEL=INFO
export DEBUG_MODE=False
export ENABLE_DASHBOARD=True
export DASHBOARD_HOST=0.0.0.0  # Public access
export DASHBOARD_PORT=8501

# Run HELM
python -m helm.main
```

---

##System Requirements

- **Python**: ≥ 3.10
- **GPU**: NVIDIA (with CUDA support) - tested on RTX 3050 (6GB)
- **CUDA**: 12.1 or compatible
- **RAM**: 8GB minimum
- **Disk**: 20GB for models cache

### Required Packages

```
torch==2.5.1
transformers==4.35.0
pydantic==2.0.0
requests==2.31.0
streamlit==1.28.0 (optional, for dashboard)
```

---

## Architecture Design Decisions

### Why Deterministic?

- **Explainability**: Every decision can be traced to specific rules
- **Auditability**: No "black box" decision-making
- **Predictability**: Same input always produces same decision path
- **Efficiency**: No probabilistic sampling needed

### Why Optional LLM?

- **Scalability**: LLM calls are expensive, use only when needed
- **Reliability**: Core decisions don't depend on LLM availability
- **Control**: LLM only generates explanations, not decisions
- **Cost**: Reduces API calls significantly

### Why Bounded Retries?

- **Performance**: Avoids infinite loops
- **Cost**: Limits resources spent on failing decisions
- **Escalation**: Forces human review of problematic cases

### Why SQLite?

- **Zero Setup**: No separate database server
- **Portability**: Single file storage
- **Reliability**: ACID transactions
- **Queryability**: Full SQL support for analysis

---

## Future Extensions

### Research Roadmap

1. **Adaptive Weights** - Dynamic scoring weights based on decision history
2. **Multi-Agent Negotiation** - Agents debating decisions
3. **RL Arbitration** - Learning optimal arbitration strategies
4. **Explainability Metrics** - SHAP/LIME integration
5. **Real-time Monitoring** - WebSocket updates for dashboard
6. **A/B Testing** - Validation of different rule sets

### Extensibility

The architecture supports:
- Adding new specialized agents
- Custom validation rules
- Alternative model backends
- Different storage systems (PostgreSQL, MongoDB)
- Custom UI implementations

---

## License & Attribution

HELM v2.0 - Hierarchical Executive-Level Meta-Agent  
Built for deterministic decision authority with optional LLM augmentation.

---

## Support & Contact

For issues, questions, or contributions:
- Check the SETUP_GUIDE.md
- Review test scenarios for examples
- Examine logs in `/logs` directory

---

**HELM v2.0 - Where Determinism Meets Intelligence**
