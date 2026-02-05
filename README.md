# AI Code Intelligence & Risk Analyzer

An AI-powered code governance platform that analyzes GitHub repositories for security vulnerabilities, code quality, maintainability, and technical debt. Get actionable insights with AI-generated explanations and professional PDF reports.

## Features

### Code Analysis
- **Security Vulnerability Detection** - Uses Bandit and pattern-based analysis to identify 20+ security risks including SQL injection, XSS, hardcoded credentials, and more
- **Complexity Analysis** - Measures cyclomatic and cognitive complexity using Radon
- **Maintainability Assessment** - Calculates maintainability index and code quality metrics
- **Architecture Analysis** - Evaluates project structure, dependencies, circular dependencies, and architectural patterns
- **Technical Debt Tracking** - Computes tech debt index with refactoring urgency levels (Low/Medium/High/Critical)

### Score Metrics (0-100 scale)
| Metric | Description |
|--------|-------------|
| Security Score | Based on vulnerability severity and count |
| Maintainability Score | Based on complexity, code smells, and structure |
| Architecture Score | Based on modularity, coupling, and cohesion |
| Tech Debt Index | Weighted combination of all scores (higher = more debt) |

### AI-Powered Insights
- LLM-powered analysis explanations using Groq API (free tier available)
- Rule-based scoring ensures consistent, deterministic results
- AI generates human-readable summaries and recommendations
- Fallback explanations when LLM is unavailable

### Additional Features
- User authentication with JWT tokens
- Analysis history tracking and management
- Professional PDF report generation
- Repository caching and automatic cleanup

## Tech Stack

### Backend
- **Framework:** FastAPI
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** JWT (python-jose), bcrypt
- **Code Analysis:** Radon, Bandit, NetworkX
- **LLM Integration:** Groq API
- **PDF Generation:** ReportLab
- **Version Control:** GitPython

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **HTTP Client:** Axios
- **Router:** React Router DOM

## Project Structure

```
AI Code Intelligence & Risk Analyzer/
├── backend/
│   ├── app/
│   │   ├── analyzers/          # Code analysis modules
│   │   │   ├── architecture.py # Project structure analysis
│   │   │   ├── complexity.py   # Cyclomatic complexity
│   │   │   ├── maintainability.py
│   │   │   ├── security.py     # Vulnerability detection
│   │   │   └── structure.py    # AST-based analysis
│   │   ├── api/                # REST API endpoints
│   │   │   ├── analyze.py      # Analysis endpoints
│   │   │   └── reports.py      # PDF report endpoints
│   │   ├── auth/               # Authentication
│   │   ├── core/               # Configuration & security
│   │   ├── db/                 # Database models & session
│   │   ├── ingestion/          # GitHub repository loader
│   │   ├── llm/                # Groq LLM integration
│   │   ├── reports/            # PDF generation
│   │   ├── scoring/            # Score calculators
│   │   └── utils/              # Utility functions
│   ├── requirements.txt
│   ├── main.py
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── context/            # React context (Auth)
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   └── styles/             # Global styles
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+ & npm
- Git

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your configuration
# Required: JWT_SECRET_KEY
# Optional: GROQ_API_KEY (for AI explanations)

# Initialize database (optional - creates admin user)
python create_superuser.py

# Run the server
python main.py
```

The backend runs on `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend runs on `http://localhost:5173`

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | Yes | - | Secret key for JWT token generation |
| `GROQ_API_KEY` | No | - | Groq API key for AI explanations |
| `GROQ_MODEL` | No | `llama3-8b-8192` | Groq model to use |
| `GROQ_MAX_TOKENS` | No | `600` | Max tokens for LLM response |
| `GROQ_TEMPERATURE` | No | `0.2` | LLM temperature setting |
| `DEBUG` | No | `false` | Enable debug mode |

### Getting a Groq API Key

1. Visit [Groq Console](https://console.groq.com)
2. Sign up for a free account
3. Generate an API key
4. Add it to your `.env` file

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/verify` | Verify JWT token |
| GET | `/api/auth/me` | Get current user info |

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze/` | Analyze a GitHub repository |
| GET | `/api/analyze/` | List user's analysis history |
| GET | `/api/analyze/{id}` | Get specific analysis |
| DELETE | `/api/analyze/{id}` | Delete analysis |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/{id}/pdf` | Download PDF report |
| GET | `/api/reports/{id}/summary` | Get analysis summary |

## Usage

1. **Sign Up/Login** - Create an account or log in
2. **Submit Repository** - Enter a public GitHub repository URL
3. **View Analysis** - See security, maintainability, and architecture scores
4. **Read AI Insights** - Get AI-generated explanations of findings
5. **Download Report** - Generate a professional PDF report

## Security Patterns Detected

The analyzer detects various security vulnerabilities including:

- Hardcoded credentials (passwords, API keys, tokens)
- SQL Injection vulnerabilities
- Command Injection risks
- Unsafe deserialization (pickle, YAML)
- Dangerous eval()/exec() usage
- Weak cryptography (MD5, SHA1)
- Debug mode in production
- XSS vulnerabilities
- Path traversal
- And 20+ more patterns

Each issue includes severity level, confidence, file location, CWE identifier, and remediation recommendations.

## Technical Debt Calculation

```
Debt Index = (35% × Security Debt) + (30% × Maintainability Debt) +
             (25% × Architecture Debt) + (10% × Code Smell Debt)

Refactoring Urgency:
- Low: 0-25
- Medium: 25-50
- High: 50-75
- Critical: 75-100
```

## Analysis Workflow

1. **Authentication** - User logs in with JWT token
2. **Repository Submission** - User provides GitHub URL and branch
3. **Repository Cloning** - GitPython clones the repository
4. **File Scanning** - Identifies analyzable files (Python, JavaScript, TypeScript, etc.)
5. **Multi-Stage Analysis**:
   - Structure analysis via AST parsing
   - Complexity analysis via Radon
   - Security analysis via Bandit + pattern matching
   - Architecture analysis via dependency graphs
6. **Score Calculation** - Weighted algorithms compute scores
7. **AI Explanation** - Groq API generates insights (if configured)
8. **Storage** - Results saved to database
9. **Cleanup** - Temporary repository files deleted

## Development

### Running Tests
```bash
# Backend tests (when available)
cd backend
pytest

# Frontend tests (when available)
cd frontend
npm test
```

### Building for Production

```bash
# Backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
# Output in frontend/dist/
```

## Database Schema

### Users Table
- `id`, `email`, `username`, `hashed_password`
- `is_active`, `is_admin`
- `created_at`, `updated_at`

### AnalysisReports Table
- `id`, `user_id`, `repo_url`, `repo_name`, `branch`
- `metrics` (JSON), `security_score`, `maintainability_score`
- `architecture_score`, `tech_debt_index`, `refactor_urgency`
- `llm_explanation`, `files_analyzed`, `total_lines`
- `analysis_duration_seconds`, `created_at`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Radon](https://radon.readthedocs.io/) - Python code metrics
- [Bandit](https://bandit.readthedocs.io/) - Python security linter
- [Groq](https://groq.com/) - Fast LLM inference
- [ReportLab](https://www.reportlab.com/) - PDF generation
