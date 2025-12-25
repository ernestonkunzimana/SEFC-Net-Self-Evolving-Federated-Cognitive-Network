# SEFCNet: Enterprise-Grade Self-Evolving Federated Computing Network

SEFCNet is a cutting-edge, enterprise-grade federated learning system with built-in self-evolution capabilities. It provides a comprehensive solution for distributed machine learning with advanced monitoring, analytics, and visualization features.

## Enterprise Features

- **Advanced Federated Learning**
  - Dynamic model evolution
  - Adaptive learning strategies
  - Cross-silo federation support
  - Custom aggregation methods

- **Self-Evolution Capabilities**
  - Automated architecture optimization
  - Dynamic hyperparameter tuning
  - Adaptive resource allocation
  - Performance-based evolution

- **Enterprise Monitoring**
  - Real-time system metrics
  - Model performance tracking
  - Resource utilization monitoring
  - Custom metric support
  - Alert system

- **Advanced Analytics**
  - Model performance analytics
  - Training progress tracking
  - Resource utilization analysis
  - Network performance metrics
  - Custom analytics pipelines

- **Interactive Dashboard**
  - Real-time visualization
  - Model comparison tools
  - System health monitoring
  - Alert management
  - Explainable AI features

- **Security & Authentication**
  - Role-based access control
  - JWT authentication
  - Secure communication
  - Audit logging

## Features

- **Federated Averaging (FedAvg)**: Implements the FedAvg strategy for model aggregation.
- **Data Partitioning**: Supports IID (Independent and Identically Distributed) data partitioning for clients.
- **Model Pipeline**: Utilizes scikit-learn pipelines for preprocessing (StandardScaler) and classification (LogisticRegression).
- **Metrics Tracking**: Tracks and aggregates both training and evaluation accuracy, along with loss, across federated rounds.
- **Streamlit Dashboard**: Provides a dynamic web-based dashboard for visualizing federated learning metrics and history.
- **Structured Logging**: Implements a structured logging system for better insights into the training process.
- **Docker & Kubernetes Infrastructure**: Includes Dockerfiles and Kubernetes deployment configurations for scalable deployment.
- **Unit and Integration Tests**: Contains a basic testing suite for core components and end-to-end simulation.

## Project Structure

```
SEFCNet/
├── README.md
├── Dockerfile
├── SEFCNet.docx
│
├── SEFCNet/                          # Main package
│   ├── main.py                       # Entry point: start server + nodes simulation
│   ├── requirements.txt              # Project dependencies
│   │
│   ├── artifacts/                      # Saved models, history, checkpoints
│   │   └── federated_history.json  # Training history (for dashboard)
│   │   ├── global_model.pth           # Placeholder for global model
│   │   └── meta_state.pkl             # Placeholder for meta-learning state
│   │
│   ├── data/                           # Local datasets or simulated environments
│   │   └── sensor.csv
│   │
│   ├── logs/                           # Runtime logs
│   │   └── monitor.log
│   │
│   ├── dashboard/                      # Visualization & Monitoring
│   │   └── monitor.py                  # Streamlit-based dashboard
│   │
│   ├── central_controller/             # Federated server (Coordinator)
│   │   ├── server.py                   # Aggregation + Meta-Coordination
│   │   ├── aggregator.py               # FedAvg, FedProx, FedMeta operations
│   │   └── registry.py                 # Client registry + artifacts tracking
│   │
│   ├── nodes/                          # Federated clients (Edge nodes)
│   │   ├── client_template.py          # Generic client structure
│   │   ├── client_evolving.py          # Self-evolving RL + meta learner
│   │   ├── client1.py                  # Example client 1
│   │   ├── client2.py                  # Example client 2
│   │   ├── client3.py                  # Example client 3
│   │   └── clientN.py                  # Example client N
│   │
│   ├── models/                         # Deep learning + RL architectures
│   │   ├── base_model.py               # Core encoder/MLP/CNN
│   │   ├── rl_agent.py                 # RL policy + value networks
│   │   ├── meta_learner.py             # MAML/Reptile implementation
│   │   └── hybrid_model.py             # RL + supervised fusion model
│   │
│   ├── rl/                             # Reinforcement learning utilities
│   │   ├── self_evolving_agent.py      # RL training loop (PPO/SAC)
│   │   └── replay_buffer.py            # Experience management
│   │
│   ├── utils/                          # Shared utilities
│   │   ├── logger.py
│   │   ├── config_loader.py
│   │   ├── metrics.py
│   │   └── network_utils.py
│   │
│   ├── experiments/                    # Training configurations + scripts
│   │   ├── configs/
│   │   │   ├── default.yaml
│   │   │   └── fedmeta.yaml
│   │   └── run_federated.py
│   │
│   ├── infra/                          # Deployment configurations
│   │   ├── docker/
│   │   │   ├── Dockerfile.client
│   │   │   └── Dockerfile.server
│   │   └── k8s/
│   │       ├── deployment.yaml
│   │       └── service.yaml
│   │
│   └── tests/                          # Unit and integration tests
│       ├── test_trainer.py
│       ├── test_server.py
│       └── test_end_to_end.py
│
└── venv/                            # Python virtual environment (ignored by Git)
```

## Project Roadmap: Towards Self-Evolving Federated Learning

This roadmap outlines the planned evolution of SEFC-Net into a truly self-evolving and adaptive federated learning system, integrating advanced AI and IoT capabilities.

### Phase 1: Core Self-Evolving Intelligence

**Goal**: Make SEFC-Net truly self-evolving — not just federated.

| Add-On                  | Purpose                                                 | Implementation Plan                                                                                              |
| :---------------------- | :------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------- |
| **Meta-Optimizer Layer**  | Learns how to adjust learning hyperparameters over time. | Integrate Optuna + RL agent that tunes parameters (learning rate, aggregation weight, batch size) dynamically. |
| **Neuro-Evolution Module**| Mutates architectures based on performance (biological analogy). | Use DEAP or NEAT-Python to evolve model architectures.                                                           |
| **Autonomous Reward Engine**| Rewards nodes for stability, accuracy, or data novelty. | Reinforcement agent with reward = Δaccuracy + novelty_score.                                                     |

**🧩 Output**: You’ll have models that evolve without human tuning — true “machine evolution.”

### Phase 2: Federated + IoT Simulation Layer

**Goal**: Bring realism — simulate diverse IoT clients like drones, health sensors, SACCO nodes.

| Add-On                    | Purpose                                           | Library / Tool                                                              |
| :------------------------ | :------------------------------------------------ | :-------------------------------------------------------------------------- |
| **Data Streaming Simulation**| Mimic real-world IoT environments.                | Use paho-mqtt or Node-RED for live sensor data (temp, GPS, ECG, etc.).      |
| **Client Diversity**      | Heterogeneous clients with different compute & bandwidth. | Simulate using Ray Tune and PyTorch federated backends.                     |
| **Energy-Aware Edge AI**  | Optimize based on latency, battery, and connectivity. | Integrate SimPy or EnergyModel for energy-aware RL.                         |

**🧩 Output**: A realistic federated edge ecosystem that learns and adapts dynamically.

### Phase 3: Real-Time Visualization & Control

**Goal**: Give SEFC-Net a living dashboard — so people see it learning and evolving.

| Component                 | Purpose                                                 | Framework                                     |
| :------------------------ | :------------------------------------------------------ | :-------------------------------------------- |
| **Evolution Dashboard**   | Visualize nodes, performance, and communication graph.    | Plotly Dash / Streamlit                         |
| **Cognitive Map**         | Visualize agent attention and model evolution over time. | Bokeh / TensorBoard + embeddings                |
| **Federated Monitor API** | REST API for monitoring and node registration.            | FastAPI + WebSocket                             |

**🧩 Output**: Real-time intelligence dashboard showing model growth, learning rates, and evolution speed.

### Phase 4: RIS + Civic Intelligence Integration

**Goal**: Link SEFC-Net to smart cities, SACCOs, or public systems — creating self-adaptive civic infrastructure.

| Integration                       | Purpose                                           | Example Use                                       |
| :-------------------------------- | :------------------------------------------------ | :------------------------------------------------ |
| **Reconfigurable Intelligent Surfaces (RIS)**| Edge-assisted learning acceleration               | Smart transport, drone communications             |
| **Civic Data Adapters**           | Integrate finance, health, or environment datasets | SACCO learning nodes, health wearables          |
| **Cognitive Federation Cloud (Aetha Cloud)**| Long-term PhD layer                               | Scalable evolutionary intelligence network      |

**🧩 Output**: A full AI ecosystem that adapts socially, economically, and technically.

### Quick Start

### Package Migration Notes

1. **EnergyModel Package Migration**
   The deprecated `EnergyModel` package has been replaced with `powermodel`, a modern alternative that provides:
   - Better energy consumption modeling
   - Hardware-specific power profiles
   - Integration with monitoring tools
   - Real-time power estimation

   Usage example:
   ```python
   from powermodel import PowerModel, PowerProfile

   # Create model with custom power profile
   model = PowerModel(
       profile=PowerProfile.from_dataframe(your_data),
       sampling_rate=1.0  # 1 Hz sampling rate
   )

   # Estimate power consumption
   power = model.estimate_power(
       cpu_util=50.0,    # CPU utilization %
       mem_util=30.0,    # Memory utilization %
       network_io=1024   # Network I/O bytes/sec
   )
   ```

### Option 1: Automated Setup (Choose your platform)

Run the appropriate setup script to create a virtual environment and install all dependencies:

**Windows:**
```powershell
# From the repository root
.\scripts\setup_venv.ps1
```

**Linux/macOS:**
```bash
# From the repository root
chmod +x scripts/setup_venv.sh
./scripts/setup_venv.sh
```

This will:
1. Create a Python virtual environment (if not exists)
2. Install all required packages
3. Show activation/usage instructions

### Option 2: Manual Setup

1. Create and activate a virtual environment:
   ```powershell
   # Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   ```bash
   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r SEFCNet/requirements.txt
   ```

## Development Tools

### Code Quality Tools

The repository includes several tools for maintaining code quality:

1. Pre-commit hooks (run before each commit):
   ```bash
   pre-commit install    # First time setup
   ```
   This sets up automatic checks for:
   - Code formatting (black)
   - Import sorting (isort)
   - Type checking (mypy)
   - Linting (pylint)
   - Security checks (bandit)

2. Manual code quality checks:
   ```bash
   # Run formatters
   black .
   isort .

   # Run type checker
   mypy .

   # Run linter
   pylint SEFCNet/

   # Run security checks
   bandit -r SEFCNet/
   ```

### File Tracking

The repository includes tools to track and compare file changes:

1. Compare against PDF documentation:
   ```powershell
   python .\scripts\compare_with_pdf.py
   ```
   This generates reports in the `scripts/` directory:
   - `expected_manifest.txt`: Files mentioned in the PDF
   - `current_manifest.txt`: Current workspace files
   - `missing.txt`: Files listed in PDF but missing
   - `extra.txt`: Files present but not in PDF
   - `compare_report.txt`: Human-readable summary

2. Create a file manifest:
   ```powershell
   python .\scripts\track_files.py
   ```
   This creates:
   - `manifest.txt`: Current repository file list
   - `manifest_report.txt`: File categories and counts

Use these tools to:
- Track which files are missing vs documentation
- Monitor repository structure changes
- Ensure all required files are present

## Quick Start - Production Ready MVP

### 🚀 Fastest Way to Get Started

**Option 1: Docker Compose (Recommended)**
```bash
# 1. Copy environment configuration
cp .env.example .env

# 2. Generate a secure JWT secret (IMPORTANT!)
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy the output to SEFCNET_JWT_SECRET in .env

# 3. Start all services
docker-compose up -d

# 4. Access the API
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Dashboard: http://localhost:8501
```

**Option 2: Local Development**
```bash
# Windows
.\scripts\start_server.ps1

# Linux/macOS
./scripts/start_server.sh
```

### 📚 API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 🔐 First Steps

1. **Register a user:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@sefcnet.com",
       "password": "SecurePassword123!",
       "roles": ["admin"],
       "permissions": ["ADMIN", "MANAGE", "WRITE", "READ"]
     }'
   ```

2. **Login to get tokens:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@sefcnet.com",
       "password": "SecurePassword123!"
     }'
   ```

3. **Use the access token for authenticated requests:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/system/state" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

## Usage

### 1. Run the Federated Learning Simulation

Navigate to the `SEFCNet` directory (if not already there):

```bash
cd SEFCNet
```

Execute the main simulation script:

```bash
python main.py
```

This will start the federated learning process for 10 rounds with 5 clients, and save the training history to `artifacts/federated_history.json`.

### 2. View the Dashboard

After running the simulation (and generating the `federated_history.json` file), you can launch the Streamlit dashboard to visualize the results:

```bash
streamlit run .\dashboard\monitor.py
```

This will open the dashboard in your web browser, displaying plots for distributed loss, training accuracy, and evaluation accuracy over the training rounds. You can manually input the path to `federated_history.json` if it's not automatically detected.

### 3. Use the REST API

The complete REST API is available at `http://localhost:8000/api/v1/` with full authentication and authorization support.

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

## Development & Contribution

- **Tests**: Run unit tests using `pytest` from the project root.
- **Docker**: Build client and server Docker images from `infra/docker`.
- **Kubernetes**: Deploy the federated learning system using the configurations in `infra/k8s`.

---