# Deep Research Multi-Agent System

A sophisticated multi-agent system for deep research using Agno (Python framework) and Parallel.ai APIs. This system implements the architecture shown in your diagram with four specialized agents working together to perform comprehensive research tasks.

## Architecture Overview

The system implements a multi-agent architecture with direct Parallel.ai API integration. See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture information.

The system consists of:

### Core Agents (Direct Parallel.ai Integration)
1. **Search Agent** - Direct integration with Parallel.ai Search API for web research
2. **Analyst Agent** - Direct integration with Parallel.ai Task API for data analysis  
3. **Critic Agent** - Direct integration with Parallel.ai Task API for verification
4. **Writer Agent** - Direct integration with Parallel.ai Chat API for content generation

### Memory System
- **Search Memory** - Stores web search results and API data
- **Analysis Memory** - Stores processed data and analytics results
- **Verification Memory** - Stores fact-checking and validation results
- **Content Memory** - Stores generated content and templates
- **Shared Knowledge Repository** - Central persistent storage

### Coordination System
- **Workflow Engine** - Manages multi-agent workflows
- **Task Coordinator** - Coordinates tasks between agents
- **Agent Orchestrator** - Main system orchestrator

## Features

- **Multi-Agent Architecture**: Four specialized agents working in coordination
- **Direct Parallel.ai Integration**: Each agent directly uses the appropriate Parallel.ai API suite
- **Memory System**: Comprehensive memory management for all agent data
- **Workflow Management**: Sophisticated workflow orchestration
- **REST API**: Full REST API for system interaction
- **Async Processing**: Support for both synchronous and asynchronous task processing
- **Knowledge Management**: Centralized knowledge repository with search capabilities

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- pip package manager
- API keys for Parallel.ai and OpenAI

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd deep-research
```

2. **Create virtual environment (recommended):**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# Get your API keys from:
# - Parallel.ai: https://parallel.ai
# - OpenAI: https://platform.openai.com
```

5. **Run the system:**
```bash
# Option 1: Use the startup script (recommended)
python run.py

# Option 2: Direct FastAPI server
python main.py

# Option 3: With uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Verify the installation:**
```bash
# Check system health
curl http://localhost:8000/health

# View API documentation
# Visit: http://localhost:8000/docs
```

### 🌐 Access the System

Once running, you can access:
- **API Documentation**: http://localhost:8000/docs
- **System Status**: http://localhost:8000/status  
- **Health Check**: http://localhost:8000/health

## Configuration

Create a `.env` file with the following variables:

```env
# Parallel.ai API Configuration
PARALLEL_API_KEY=your_parallel_api_key_here

# OpenAI Configuration (for Agno)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./deep_research.db

# Redis Configuration (for caching)
REDIS_URL=redis://localhost:6379

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
```

## Usage

### Direct Agent Usage (Python)

#### Complete Research Pipeline
```python
from coordination.agent_orchestrator import AgentOrchestrator

# Initialize the system
orchestrator = AgentOrchestrator()
await orchestrator.start_system()

# Perform research
result = await orchestrator.research(
    "Latest developments in artificial intelligence",
    processor_config={
        "search": "pro",
        "analysis": "ultra", 
        "verification": "pro",
        "content": "base"
    }
)
```

#### Individual Agent Operations
```python
# Direct agent access
search_agent = orchestrator.agents["SearchAgent"]
analyst_agent = orchestrator.agents["AnalystAgent"]
critic_agent = orchestrator.agents["CriticAgent"]
writer_agent = orchestrator.agents["WriterAgent"]

# Use agents directly
search_result = await search_agent.search_web("AI trends")
analysis_result = await analyst_agent.analyze_data(search_result)
```

### REST API Endpoints

#### Research
```bash
curl -X POST "http://localhost:8000/research" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI developments", "processor_config": {"search": "pro"}}'
```

#### System Status
```bash
curl -X GET "http://localhost:8000/status"
curl -X GET "http://localhost:8000/agents"
```

#### Knowledge Management
```bash
curl -X GET "http://localhost:8000/knowledge/search?q=artificial intelligence"
```

## Agent Configuration

### Processor Selection

The system supports different processors for different tasks:

- **Search Agent**: `base` (fast) or `pro` (comprehensive search)
- **Analyst Agent**: `core` (standard) or `ultra` (complex analysis)
- **Critic Agent**: `pro` (fact-checking) or `ultra` (complex validation)
- **Writer Agent**: `lite` (fast) or `base` (quality content)

**Available Processors**: `lite`, `base`, `core`, `pro`, `ultra`, `ultra2x`, `ultra4x`, `ultra8x`

### Workflow Types

1. **Research Workflow**: Complete research pipeline (Search → Analysis → Verification → Content)
2. **Analysis Workflow**: Data analysis only (Analysis → Verification)
3. **Content Workflow**: Content generation only (Content)

## 📜 Available Scripts

- **`python run.py`** - 🚀 **Recommended** - Start with environment validation and pretty output
- **`python main.py`** - Direct FastAPI application startup (basic)
- **`python examples/basic_usage.py`** - Basic usage examples and tutorials (if available)

## Development

### Project Structure

```
deep-research/
├── agents/                 # Agent implementations with direct Parallel.ai integration
│   ├── base_agent.py      # Base agent class
│   ├── search_agent.py    # Search agent → Parallel.ai Search API
│   ├── analyst_agent.py   # Analyst agent → Parallel.ai Task API
│   ├── critic_agent.py    # Critic agent → Parallel.ai Task API
│   └── writer_agent.py    # Writer agent → Parallel.ai Chat API
├── memory/                # Memory system
│   ├── base.py           # Base memory class
│   ├── search_memory.py  # Search memory
│   ├── analysis_memory.py # Analysis memory
│   ├── verification_memory.py # Verification memory
│   ├── content_memory.py # Content memory
│   └── shared_knowledge.py # Shared knowledge repository
├── coordination/          # Coordination system
│   ├── workflow_engine.py # Workflow engine
│   ├── task_coordinator.py # Task coordinator
│   └── agent_orchestrator.py # Agent orchestrator
├── examples/              # Usage examples
│   └── basic_usage.py    # Basic usage examples
├── config.py             # Configuration
├── main.py              # Main application
├── run.py               # Startup script with environment validation
├── ARCHITECTURE.md      # Detailed architecture documentation
└── requirements.txt     # Dependencies
```

### Adding New Agents

1. Create a new agent class inheriting from `BaseAgent`
2. Implement the required methods (`_get_instructions`, `process_task`)
3. Add the agent to the orchestrator
4. Create workflows that use the new agent

### Extending Memory System

1. Create a new memory class inheriting from `BaseMemory`
2. Implement the required methods (`store`, `retrieve`, `search`)
3. Add the memory to the shared knowledge repository

## 🐛 Troubleshooting

### Common Issues

#### Installation Issues
```bash
# If you get dependency conflicts
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# If agno installation fails
pip install agno --no-cache-dir

# If parallel-web installation fails
pip install parallel-web --upgrade
```

#### API Key Issues
```bash
# Verify your .env file exists and has correct format
cat .env

# Check if environment variables are loaded
python -c "import os; print(os.getenv('PARALLEL_API_KEY'))"
```

#### Runtime Issues
```bash
# Check system status
curl http://localhost:8000/health

# View system logs
python run.py  # Will show detailed startup logs

# Test the research endpoint
curl -X POST "http://localhost:8000/research" \
  -H "Content-Type: application/json" \
  -d '{"query": "test research query"}'
```

#### Empty Results Issue (FIXED)
If you get empty results like `"results": {}`, this was a known issue that has been resolved:
- ✅ **Fixed**: Corrected API method calls to use `client.task_run.execute()`
- ✅ **Fixed**: Updated processor configurations to use valid processors
- ✅ **Fixed**: Completed full 4-agent workflow pipeline

### Environment Variables

Required environment variables in `.env`:
```env
# Required - Get from https://parallel.ai
PARALLEL_API_KEY=your_parallel_api_key_here

# Required - Get from https://platform.openai.com  
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Database configuration
DATABASE_URL=sqlite:///./deep_research.db

# Optional - Redis for caching
REDIS_URL=redis://localhost:6379

# Optional - Application settings
DEBUG=True
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### Performance Tips

1. **Processor Selection**: Use appropriate processors for your needs
   - `lite/base` for speed
   - `pro/ultra` for quality
   
2. **Caching**: Enable Redis for better performance
   
3. **Concurrent Requests**: The system supports multiple concurrent research requests

## 📊 Monitoring and Debugging

The system provides comprehensive monitoring capabilities:

- **Agent Status**: Real-time agent health and activity logs
- **Task History**: Complete execution history with timestamps  
- **Workflow Tracking**: Step-by-step workflow progress monitoring
- **Knowledge Stats**: Repository statistics and search capabilities
- **Performance Metrics**: Response times and resource usage
- **API Monitoring**: Built-in FastAPI monitoring at `/docs`

### Monitoring Endpoints
```bash
# System health
GET /health

# Detailed system status  
GET /status

# Individual agent status
GET /agents
GET /agents/{agent_name}

# Task monitoring
GET /task/{task_id}

# Knowledge repository stats
GET /knowledge
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with proper documentation
4. **Add** tests for new functionality
5. **Ensure** all tests pass (`pytest`)
6. **Submit** a pull request with detailed description

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Install optional development tools
pip install black flake8 mypy pre-commit

# Run tests
pytest

# Run linting
black . && flake8 . && mypy .
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system information
- **Issues**: Open an issue in the repository for bugs or feature requests  
- **Discussions**: Use GitHub Discussions for questions and community support
- **API Docs**: Visit `/docs` endpoint when running for interactive API documentation

## 🔄 Updates & Changelog

### Recent Fixes (v1.1.0)
- ✅ **Fixed empty results issue** - Corrected Parallel.ai API integration
- ✅ **Updated processors** - Fixed invalid "speed" processor, now uses "lite"  
- ✅ **Enhanced workflow** - Complete 4-agent pipeline now working
- ✅ **Improved error handling** - Better debugging and error messages
- ✅ **Updated documentation** - Comprehensive architecture and setup guides
