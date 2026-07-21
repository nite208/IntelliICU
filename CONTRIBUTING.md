# Contributing to IntelliICU

Thank you for your interest in contributing to IntelliICU! This guide outlines the development workflow, coding standards, and architectural guidelines to help you build stable, enterprise-grade clinical decision support systems.

## 🏢 Architectural Principles

1. **Role-Based Separation**: Keep features and visual assistants scoped strictly within role boundaries (`Doctor`, `Nurse`, `ICU Manager`, `Admin`). Never leak diagnostic capabilities into non-clinical workflows.
2. **WebSocket Stability**: Use the shared singleton `websocketService.js` for subscribing to dashboard or patient channels. Avoid setting up parallel duplicate connections.
3. **AI Fallbacks**: Prompt templates and LLM providers should handle connectivity outages gracefully. Always fall back to the dynamic `MockLLMProvider` rather than letting the application crash.
4. **Idempotence**: Database seeders and migrations must be idempotent, allowing repeated runs against PostgreSQL/Neon instances without generating duplicate entries.

## 🛠 Development Workflow

### 1. Setup Environment
Ensure your environment contains the required configuration flags:
```bash
# Clone the repository
git clone https://github.com/Sumeet2005/IntelliICU.git
cd IntelliICU

# Setup virtual environment
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup frontend dependencies
cd ../frontend
npm install
```

### 2. Check Compatibility & Builds
Before committing, make sure the frontend builds cleanly and the backend parses correctly:
```bash
# Backend syntax compile check
python -m py_compile backend/app/main.py

# Frontend production compile check
cd frontend
npm run build
```

## 📝 Pull Request Guidelines

* Provide a clear problem statement and description of changes.
* Link to the issue being resolved.
* Clean up any debugging print statements or console log points.
* Verify your changes against the checklist inside the Pull Request Template.
