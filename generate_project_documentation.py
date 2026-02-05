"""
Generate detailed PDF documentation for AI Code Intelligence & Risk Analyzer
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime


def create_styles():
    """Create custom styles for the PDF"""
    styles = getSampleStyleSheet()

    # Title style
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=28,
        spaceAfter=30,
        textColor=colors.HexColor('#1a365d'),
        alignment=TA_CENTER
    ))

    # Subtitle style
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=20,
        textColor=colors.HexColor('#4a5568'),
        alignment=TA_CENTER
    ))

    # Section header style
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading1'],
        fontSize=18,
        spaceBefore=25,
        spaceAfter=15,
        textColor=colors.HexColor('#2c5282'),
        borderPadding=5
    ))

    # Subsection header style
    styles.add(ParagraphStyle(
        name='SubsectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#2b6cb0')
    ))

    # Body text style
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        leading=16
    ))

    # Code style
    styles.add(ParagraphStyle(
        name='CustomCode',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Courier',
        backColor=colors.HexColor('#f7fafc'),
        borderPadding=8,
        spaceAfter=10
    ))

    # Bullet style
    styles.add(ParagraphStyle(
        name='BulletText',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=5,
        bulletIndent=10
    ))

    return styles


def create_table_style():
    """Create a styled table"""
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f7fafc'), colors.white]),
    ])


def generate_pdf():
    """Generate the project documentation PDF"""

    doc = SimpleDocTemplate(
        "AI_Code_Intelligence_Documentation.pdf",
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = create_styles()
    story = []

    # ===== COVER PAGE =====
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("AI Code Intelligence", styles['CustomTitle']))
    story.append(Paragraph("& Risk Analyzer", styles['CustomTitle']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Comprehensive Project Documentation", styles['Subtitle']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Subtitle']))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Version 1.0.0", styles['Subtitle']))
    story.append(PageBreak())

    # ===== TABLE OF CONTENTS =====
    story.append(Paragraph("Table of Contents", styles['SectionHeader']))
    story.append(Spacer(1, 0.2*inch))

    toc_items = [
        "1. Executive Summary",
        "2. Project Overview",
        "3. Key Features & Capabilities",
        "4. Technology Stack",
        "5. System Architecture",
        "6. Analysis Pipeline",
        "7. Security Analysis Module",
        "8. Code Quality Metrics",
        "9. Technical Debt Calculation",
        "10. AI Integration",
        "11. API Reference",
        "12. Database Schema",
        "13. Installation Guide",
        "14. Configuration",
        "15. Usage Guide",
        "16. Future Enhancements"
    ]

    for item in toc_items:
        story.append(Paragraph(item, styles['CustomBody']))

    story.append(PageBreak())

    # ===== 1. EXECUTIVE SUMMARY =====
    story.append(Paragraph("1. Executive Summary", styles['SectionHeader']))

    story.append(Paragraph(
        """The AI Code Intelligence & Risk Analyzer is a comprehensive code governance platform
        designed to help development teams understand, assess, and improve their codebase quality.
        By combining static code analysis with AI-powered insights, the platform provides actionable
        intelligence about security vulnerabilities, code maintainability, architectural patterns,
        and technical debt.""",
        styles['CustomBody']
    ))

    story.append(Paragraph(
        """The platform addresses the growing need for automated code quality assessment in modern
        software development. With the increasing complexity of software systems and the pressure
        to deliver faster, teams need tools that can quickly identify potential issues and provide
        clear guidance on how to address them.""",
        styles['CustomBody']
    ))

    story.append(Paragraph("Key Value Propositions:", styles['SubsectionHeader']))

    benefits = [
        "<b>Security First:</b> Identifies 20+ categories of security vulnerabilities with severity ratings and remediation guidance",
        "<b>Actionable Metrics:</b> Provides quantified scores (0-100) for security, maintainability, and architecture",
        "<b>AI-Powered Insights:</b> Leverages LLM technology to generate human-readable explanations and recommendations",
        "<b>Technical Debt Visibility:</b> Calculates and tracks technical debt with urgency classification",
        "<b>Professional Reporting:</b> Generates detailed PDF reports for stakeholder communication",
        "<b>User-Friendly Interface:</b> Modern React-based dashboard for easy interaction"
    ]

    for benefit in benefits:
        story.append(Paragraph(f"• {benefit}", styles['BulletText']))

    story.append(PageBreak())

    # ===== 2. PROJECT OVERVIEW =====
    story.append(Paragraph("2. Project Overview", styles['SectionHeader']))

    story.append(Paragraph("Project Information", styles['SubsectionHeader']))

    project_info = [
        ["Attribute", "Value"],
        ["Project Name", "AI Code Intelligence & Risk Analyzer"],
        ["Version", "1.0.0"],
        ["License", "MIT License"],
        ["Primary Language", "Python (Backend), TypeScript (Frontend)"],
        ["Target Users", "Developers, Tech Leads, Security Teams"],
        ["Repository Type", "Monorepo (Backend + Frontend)"]
    ]

    table = Table(project_info, colWidths=[2*inch, 4*inch])
    table.setStyle(create_table_style())
    story.append(table)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("Problem Statement", styles['SubsectionHeader']))
    story.append(Paragraph(
        """Modern software development faces several challenges that this platform addresses:""",
        styles['CustomBody']
    ))

    problems = [
        "Security vulnerabilities often go undetected until production deployment",
        "Technical debt accumulates silently, making future development harder",
        "Code quality metrics are often ignored due to lack of actionable insights",
        "Manual code reviews cannot scale with rapid development cycles",
        "Lack of standardized metrics makes it difficult to track improvement over time"
    ]

    for problem in problems:
        story.append(Paragraph(f"• {problem}", styles['BulletText']))

    story.append(Paragraph("Solution Approach", styles['SubsectionHeader']))
    story.append(Paragraph(
        """The platform combines multiple analysis techniques to provide comprehensive insights:""",
        styles['CustomBody']
    ))

    solutions = [
        "<b>Static Analysis:</b> Examines code without execution to find issues early",
        "<b>Pattern Matching:</b> Uses regex and AST analysis to detect anti-patterns",
        "<b>Metric Calculation:</b> Computes industry-standard metrics for objective assessment",
        "<b>AI Augmentation:</b> Uses LLM to translate technical findings into actionable recommendations",
        "<b>Visualization:</b> Presents data through intuitive dashboards and reports"
    ]

    for solution in solutions:
        story.append(Paragraph(f"• {solution}", styles['BulletText']))

    story.append(PageBreak())

    # ===== 3. KEY FEATURES =====
    story.append(Paragraph("3. Key Features & Capabilities", styles['SectionHeader']))

    story.append(Paragraph("3.1 Security Analysis", styles['SubsectionHeader']))
    story.append(Paragraph(
        """The security module performs comprehensive vulnerability detection using multiple techniques:""",
        styles['CustomBody']
    ))

    security_features = [
        ["Feature", "Description"],
        ["Bandit Integration", "Industry-standard Python security linter for vulnerability detection"],
        ["Pattern-Based Detection", "Custom regex patterns for common security anti-patterns"],
        ["Severity Classification", "Issues rated as CRITICAL, HIGH, MEDIUM, or LOW"],
        ["CWE Mapping", "Vulnerabilities mapped to Common Weakness Enumeration IDs"],
        ["Remediation Guidance", "Specific recommendations for fixing each issue"]
    ]

    table = Table(security_features, colWidths=[2*inch, 4*inch])
    table.setStyle(create_table_style())
    story.append(table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("3.2 Code Quality Analysis", styles['SubsectionHeader']))
    story.append(Paragraph(
        """The platform measures code quality through multiple dimensions:""",
        styles['CustomBody']
    ))

    quality_features = [
        ["Metric", "Description"],
        ["Cyclomatic Complexity", "Measures decision complexity with grades A-F"],
        ["Cognitive Complexity", "Measures how hard code is to understand"],
        ["Maintainability Index", "Composite score for code maintainability (0-100)"],
        ["Lines of Code", "LOC, SLOC, and logical LOC counts"],
        ["Comment Ratio", "Documentation coverage percentage"],
        ["Halstead Metrics", "Program length, difficulty, and effort calculations"]
    ]

    table = Table(quality_features, colWidths=[2*inch, 4*inch])
    table.setStyle(create_table_style())
    story.append(table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("3.3 Architecture Analysis", styles['SubsectionHeader']))

    arch_features = [
        ["Analysis", "Description"],
        ["Dependency Graphs", "Visualizes module dependencies and identifies circular references"],
        ["Modularity Score", "Measures coupling and cohesion between modules"],
        ["Pattern Detection", "Identifies architectural patterns (MVC, MVVM, layered)"],
        ["Hub Analysis", "Finds highly connected central modules"],
        ["Layer Violations", "Detects improper cross-layer dependencies"]
    ]

    table = Table(arch_features, colWidths=[2*inch, 4*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(PageBreak())

    # ===== 4. TECHNOLOGY STACK =====
    story.append(Paragraph("4. Technology Stack", styles['SectionHeader']))

    story.append(Paragraph("4.1 Backend Technologies", styles['SubsectionHeader']))

    backend_stack = [
        ["Technology", "Version", "Purpose"],
        ["FastAPI", "0.109.0", "Modern async web framework"],
        ["SQLAlchemy", "2.0.25", "ORM for database operations"],
        ["SQLite", "-", "Lightweight database storage"],
        ["Radon", "6.0.1", "Code complexity analysis"],
        ["Bandit", "1.7.7", "Security vulnerability scanning"],
        ["NetworkX", "3.2.1", "Graph analysis for dependencies"],
        ["Groq API", "0.4.2", "LLM integration for AI insights"],
        ["ReportLab", "4.1.0", "PDF report generation"],
        ["GitPython", "3.1.41", "Git repository operations"],
        ["python-jose", "-", "JWT token handling"],
        ["bcrypt", "-", "Password hashing"]
    ]

    table = Table(backend_stack, colWidths=[1.5*inch, 1*inch, 3.5*inch])
    table.setStyle(create_table_style())
    story.append(table)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("4.2 Frontend Technologies", styles['SubsectionHeader']))

    frontend_stack = [
        ["Technology", "Version", "Purpose"],
        ["React", "18.2.0", "UI component library"],
        ["TypeScript", "5.2.2", "Type-safe JavaScript"],
        ["Vite", "5.0.8", "Fast build tool and dev server"],
        ["Tailwind CSS", "3.4.0", "Utility-first CSS framework"],
        ["React Router", "6.21.0", "Client-side routing"],
        ["Axios", "1.6.5", "HTTP client for API calls"],
        ["Lucide React", "0.303.0", "Icon library"]
    ]

    table = Table(frontend_stack, colWidths=[1.5*inch, 1*inch, 3.5*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(PageBreak())

    # ===== 5. SYSTEM ARCHITECTURE =====
    story.append(Paragraph("5. System Architecture", styles['SectionHeader']))

    story.append(Paragraph("5.1 High-Level Architecture", styles['SubsectionHeader']))
    story.append(Paragraph(
        """The system follows a modern three-tier architecture with clear separation of concerns:""",
        styles['CustomBody']
    ))

    story.append(Paragraph(
        """<b>Presentation Layer (Frontend):</b> React-based single-page application that provides
        the user interface. Communicates with the backend via REST API calls. Handles authentication
        state, form validation, and result visualization.""",
        styles['CustomBody']
    ))

    story.append(Paragraph(
        """<b>Application Layer (Backend):</b> FastAPI-based REST API server that handles business
        logic. Includes authentication, analysis orchestration, score calculation, LLM integration,
        and report generation.""",
        styles['CustomBody']
    ))

    story.append(Paragraph(
        """<b>Data Layer:</b> SQLite database for persistent storage of user accounts and analysis
        results. Uses SQLAlchemy ORM for database operations.""",
        styles['CustomBody']
    ))

    story.append(Paragraph("5.2 Backend Module Structure", styles['SubsectionHeader']))

    modules = [
        ["Module", "Responsibility"],
        ["app/analyzers/", "Code analysis logic (security, complexity, architecture)"],
        ["app/api/", "REST API endpoint definitions"],
        ["app/auth/", "User authentication and authorization"],
        ["app/core/", "Configuration and security utilities"],
        ["app/db/", "Database models and session management"],
        ["app/ingestion/", "GitHub repository cloning and loading"],
        ["app/llm/", "Groq LLM integration and prompt building"],
        ["app/reports/", "PDF report generation"],
        ["app/scoring/", "Score calculation algorithms"],
        ["app/utils/", "Shared utility functions"]
    ]

    table = Table(modules, colWidths=[2*inch, 4*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(PageBreak())

    # ===== 6. ANALYSIS PIPELINE =====
    story.append(Paragraph("6. Analysis Pipeline", styles['SectionHeader']))

    story.append(Paragraph(
        """The analysis pipeline processes repositories through a series of well-defined stages:""",
        styles['CustomBody']
    ))

    pipeline_stages = [
        ["Stage", "Process", "Output"],
        ["1. Authentication", "Validate JWT token", "User context"],
        ["2. Repository Ingestion", "Clone GitHub repo via GitPython", "Local repository files"],
        ["3. File Discovery", "Scan for analyzable files", "File list with metadata"],
        ["4. Structure Analysis", "Parse AST for Python/JS files", "Code structure data"],
        ["5. Complexity Analysis", "Calculate via Radon", "Complexity metrics"],
        ["6. Security Analysis", "Run Bandit + pattern matching", "Vulnerability list"],
        ["7. Maintainability Analysis", "Compute quality metrics", "Maintainability data"],
        ["8. Architecture Analysis", "Build dependency graph", "Architecture metrics"],
        ["9. Score Calculation", "Apply weighted algorithms", "Numeric scores"],
        ["10. AI Explanation", "Generate via Groq LLM", "Markdown summary"],
        ["11. Storage", "Save to database", "Analysis record"],
        ["12. Cleanup", "Delete cloned repository", "Clean temp directory"]
    ]

    table = Table(pipeline_stages, colWidths=[1.5*inch, 2.5*inch, 2*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Pipeline Characteristics:", styles['SubsectionHeader']))

    characteristics = [
        "<b>Deterministic Scoring:</b> All scores are calculated using rule-based algorithms, ensuring consistent and reproducible results",
        "<b>LLM for Explanation Only:</b> AI is used solely for generating human-readable explanations, never for decision-making",
        "<b>Graceful Degradation:</b> System works without LLM, using fallback explanations if API is unavailable",
        "<b>Automatic Cleanup:</b> Temporary files are always cleaned up, even on failure"
    ]

    for char in characteristics:
        story.append(Paragraph(f"• {char}", styles['BulletText']))

    story.append(PageBreak())

    # ===== 7. SECURITY ANALYSIS MODULE =====
    story.append(Paragraph("7. Security Analysis Module", styles['SectionHeader']))

    story.append(Paragraph("7.1 Vulnerability Categories", styles['SubsectionHeader']))
    story.append(Paragraph(
        """The security analyzer detects the following categories of vulnerabilities:""",
        styles['CustomBody']
    ))

    vuln_categories = [
        ["Category", "Severity", "Example Pattern"],
        ["Hardcoded Credentials", "CRITICAL", "pwd = '[hidden]'"],
        ["SQL Injection", "CRITICAL", "execute('SELECT * FROM ' + input)"],
        ["Command Injection", "CRITICAL", "os.system(input)"],
        ["Unsafe Deserialization", "HIGH", "pickle load(data)"],
        ["Dynamic Code Execution", "HIGH", "dynamic code execution"],
        ["Weak Cryptography", "MEDIUM", "hashlib.md5(data)"],
        ["Debug Mode", "MEDIUM", "DEBUG = True"],
        ["XSS Vulnerabilities", "HIGH", "innerHTML = input"],
        ["Path Traversal", "HIGH", "open('../' + filename)"],
        ["Insecure Random", "MEDIUM", "random.random() for crypto"]
    ]

    table = Table(vuln_categories, colWidths=[1.8*inch, 1.2*inch, 3*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("7.2 Security Score Calculation", styles['SubsectionHeader']))

    story.append(Paragraph(
        """The security score (0-100) is calculated based on vulnerability severity and count:""",
        styles['CustomBody']
    ))

    story.append(Paragraph(
        """<font face="Courier">
        Security Score = 100 - (CRITICAL × 25) - (HIGH × 15) - (MEDIUM × 8) - (LOW × 3)
        </font>""",
        styles['CustomCode']
    ))

    story.append(Paragraph(
        """The score is capped at 0 (minimum) and additional factors like vulnerability density
        (issues per KLOC) may further adjust the score.""",
        styles['CustomBody']
    ))

    story.append(PageBreak())

    # ===== 8. CODE QUALITY METRICS =====
    story.append(Paragraph("8. Code Quality Metrics", styles['SectionHeader']))

    story.append(Paragraph("8.1 Cyclomatic Complexity", styles['SubsectionHeader']))
    story.append(Paragraph(
        """Cyclomatic complexity measures the number of independent paths through code.
        It's calculated by analyzing decision points (if, for, while, etc.).""",
        styles['CustomBody']
    ))

    complexity_grades = [
        ["Grade", "Complexity Range", "Risk Level"],
        ["A", "1-5", "Low - simple, well-structured"],
        ["B", "6-10", "Low - reasonable complexity"],
        ["C", "11-20", "Moderate - more complex"],
        ["D", "21-30", "High - difficult to test"],
        ["E", "31-40", "Very High - error prone"],
        ["F", "41+", "Critical - untestable"]
    ]

    table = Table(complexity_grades, colWidths=[1*inch, 2*inch, 3*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("8.2 Maintainability Index", styles['SubsectionHeader']))
    story.append(Paragraph(
        """The Maintainability Index (MI) is a composite metric that considers volume,
        complexity, and lines of code:""",
        styles['CustomBody']
    ))

    story.append(Paragraph(
        """<font face="Courier">
        MI = 171 - 5.2 × ln(V) - 0.23 × G - 16.2 × ln(LOC)

        Where:
        V = Halstead Volume
        G = Cyclomatic Complexity
        LOC = Lines of Code
        </font>""",
        styles['CustomCode']
    ))

    mi_interpretation = [
        ["MI Range", "Interpretation"],
        ["85-100", "Highly maintainable"],
        ["65-84", "Moderately maintainable"],
        ["0-64", "Difficult to maintain"]
    ]

    table = Table(mi_interpretation, colWidths=[2*inch, 4*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(PageBreak())

    # ===== 9. TECHNICAL DEBT =====
    story.append(Paragraph("9. Technical Debt Calculation", styles['SectionHeader']))

    story.append(Paragraph("9.1 Debt Index Formula", styles['SubsectionHeader']))
    story.append(Paragraph(
        """Technical debt is calculated as a weighted combination of multiple factors:""",
        styles['CustomBody']
    ))

    story.append(Paragraph(
        """<font face="Courier">
        Tech Debt Index = (0.35 × Security Debt) +
                          (0.30 × Maintainability Debt) +
                          (0.25 × Architecture Debt) +
                          (0.10 × Code Smell Debt)

        Where each debt component = 100 - respective score
        </font>""",
        styles['CustomCode']
    ))

    story.append(Paragraph("9.2 Refactoring Urgency Levels", styles['SubsectionHeader']))

    urgency_levels = [
        ["Level", "Debt Range", "Recommended Action"],
        ["LOW", "0-25", "Continue normal development, address issues opportunistically"],
        ["MEDIUM", "26-50", "Plan dedicated refactoring time in upcoming sprints"],
        ["HIGH", "51-75", "Prioritize debt reduction before new features"],
        ["CRITICAL", "76-100", "Immediate action required, consider feature freeze"]
    ]

    table = Table(urgency_levels, colWidths=[1.2*inch, 1.2*inch, 3.6*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(PageBreak())

    # ===== 10. AI INTEGRATION =====
    story.append(Paragraph("10. AI Integration", styles['SectionHeader']))

    story.append(Paragraph("10.1 Groq LLM Integration", styles['SubsectionHeader']))
    story.append(Paragraph(
        """The platform integrates with Groq's fast LLM inference API to generate
        human-readable analysis explanations. Key characteristics:""",
        styles['CustomBody']
    ))

    ai_features = [
        "<b>Model:</b> Uses llama3-8b-8192 by default (configurable)",
        "<b>Purpose:</b> Explanation generation only - never used for scoring decisions",
        "<b>Temperature:</b> Low (0.2) for consistent, focused outputs",
        "<b>Max Tokens:</b> 600 tokens for concise summaries",
        "<b>Fallback:</b> Template-based explanations when LLM unavailable"
    ]

    for feature in ai_features:
        story.append(Paragraph(f"• {feature}", styles['BulletText']))

    story.append(Paragraph("10.2 Prompt Engineering", styles['SubsectionHeader']))
    story.append(Paragraph(
        """The LLM receives structured prompts containing:""",
        styles['CustomBody']
    ))

    prompt_components = [
        "Repository name and analysis context",
        "Calculated scores (security, maintainability, architecture)",
        "Top security vulnerabilities with severity",
        "Complexity hotspots and code quality issues",
        "Technical debt index and urgency level",
        "Instructions to provide actionable recommendations"
    ]

    for component in prompt_components:
        story.append(Paragraph(f"• {component}", styles['BulletText']))

    story.append(PageBreak())

    # ===== 11. API REFERENCE =====
    story.append(Paragraph("11. API Reference", styles['SectionHeader']))

    story.append(Paragraph("11.1 Authentication Endpoints", styles['SubsectionHeader']))

    auth_endpoints = [
        ["Method", "Endpoint", "Description"],
        ["POST", "/api/auth/signup", "Register new user account"],
        ["POST", "/api/auth/login", "Authenticate and get JWT token"],
        ["POST", "/api/auth/verify", "Verify JWT token validity"],
        ["GET", "/api/auth/me", "Get current user information"]
    ]

    table = Table(auth_endpoints, colWidths=[1*inch, 2.5*inch, 2.5*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("11.2 Analysis Endpoints", styles['SubsectionHeader']))

    analysis_endpoints = [
        ["Method", "Endpoint", "Description"],
        ["POST", "/api/analyze/", "Analyze a GitHub repository"],
        ["GET", "/api/analyze/", "List user's analysis history"],
        ["GET", "/api/analyze/{id}", "Get specific analysis details"],
        ["DELETE", "/api/analyze/{id}", "Delete an analysis"]
    ]

    table = Table(analysis_endpoints, colWidths=[1*inch, 2.5*inch, 2.5*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("11.3 Report Endpoints", styles['SubsectionHeader']))

    report_endpoints = [
        ["Method", "Endpoint", "Description"],
        ["GET", "/api/reports/{id}/pdf", "Download PDF report"],
        ["GET", "/api/reports/{id}/summary", "Get analysis summary"]
    ]

    table = Table(report_endpoints, colWidths=[1*inch, 2.5*inch, 2.5*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(PageBreak())

    # ===== 12. DATABASE SCHEMA =====
    story.append(Paragraph("12. Database Schema", styles['SectionHeader']))

    story.append(Paragraph("12.1 Users Table", styles['SubsectionHeader']))

    users_schema = [
        ["Column", "Type", "Description"],
        ["id", "INTEGER (PK)", "Auto-incrementing primary key"],
        ["email", "VARCHAR (unique)", "User email address"],
        ["username", "VARCHAR (unique)", "Username for display"],
        ["hashed_password", "VARCHAR", "bcrypt hashed password"],
        ["is_active", "BOOLEAN", "Account active status"],
        ["is_admin", "BOOLEAN", "Admin privileges flag"],
        ["created_at", "DATETIME", "Account creation timestamp"],
        ["updated_at", "DATETIME", "Last update timestamp"]
    ]

    table = Table(users_schema, colWidths=[1.8*inch, 1.7*inch, 2.5*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("12.2 AnalysisReports Table", styles['SubsectionHeader']))

    reports_schema = [
        ["Column", "Type", "Description"],
        ["id", "INTEGER (PK)", "Auto-incrementing primary key"],
        ["user_id", "INTEGER (FK)", "Reference to users table"],
        ["repo_url", "VARCHAR", "GitHub repository URL"],
        ["repo_name", "VARCHAR", "Repository name"],
        ["branch", "VARCHAR", "Analyzed branch"],
        ["metrics", "JSON", "Detailed analysis metrics"],
        ["security_score", "FLOAT", "Security score (0-100)"],
        ["maintainability_score", "FLOAT", "Maintainability score (0-100)"],
        ["architecture_score", "FLOAT", "Architecture score (0-100)"],
        ["tech_debt_index", "FLOAT", "Technical debt index (0-100)"],
        ["refactor_urgency", "VARCHAR", "LOW/MEDIUM/HIGH/CRITICAL"],
        ["llm_explanation", "TEXT", "AI-generated explanation"],
        ["files_analyzed", "INTEGER", "Number of files analyzed"],
        ["total_lines", "INTEGER", "Total lines of code"],
        ["analysis_duration", "FLOAT", "Time taken in seconds"],
        ["created_at", "DATETIME", "Analysis timestamp"]
    ]

    table = Table(reports_schema, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(PageBreak())

    # ===== 13. INSTALLATION GUIDE =====
    story.append(Paragraph("13. Installation Guide", styles['SectionHeader']))

    story.append(Paragraph("13.1 Prerequisites", styles['SubsectionHeader']))

    prerequisites = [
        "Python 3.9 or higher",
        "Node.js 16 or higher with npm",
        "Git (for repository cloning functionality)"
    ]

    for prereq in prerequisites:
        story.append(Paragraph(f"• {prereq}", styles['BulletText']))

    story.append(Paragraph("13.2 Backend Installation", styles['SubsectionHeader']))

    story.append(Paragraph(
        """<font face="Courier">
# Clone repository
git clone &lt;repository-url&gt;
cd "AI Code Intelligence &amp; Risk Analyzer"

# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows: venv\\Scripts\\activate
# Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Run server
python main.py
        </font>""",
        styles['CustomCode']
    ))

    story.append(Paragraph("13.3 Frontend Installation", styles['SubsectionHeader']))

    story.append(Paragraph(
        """<font face="Courier">
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
        </font>""",
        styles['CustomCode']
    ))

    story.append(PageBreak())

    # ===== 14. CONFIGURATION =====
    story.append(Paragraph("14. Configuration", styles['SectionHeader']))

    story.append(Paragraph("14.1 Environment Variables", styles['SubsectionHeader']))

    env_vars = [
        ["Variable", "Required", "Default", "Description"],
        ["JWT_SECRET_KEY", "Yes", "-", "Secret for JWT token generation"],
        ["GROQ_API_KEY", "No", "-", "Groq API key for AI explanations"],
        ["GROQ_MODEL", "No", "llama3-8b-8192", "LLM model to use"],
        ["GROQ_MAX_TOKENS", "No", "600", "Max tokens for response"],
        ["GROQ_TEMPERATURE", "No", "0.2", "LLM temperature"],
        ["DEBUG", "No", "false", "Enable debug mode"]
    ]

    table = Table(env_vars, colWidths=[1.8*inch, 0.8*inch, 1.4*inch, 2*inch])
    table.setStyle(create_table_style())
    story.append(table)

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("14.2 Getting Groq API Key", styles['SubsectionHeader']))

    groq_steps = [
        "Visit https://console.groq.com",
        "Create a free account",
        "Navigate to API Keys section",
        "Generate a new API key",
        "Add key to .env file as GROQ_API_KEY"
    ]

    for i, step in enumerate(groq_steps, 1):
        story.append(Paragraph(f"{i}. {step}", styles['BulletText']))

    story.append(PageBreak())

    # ===== 15. USAGE GUIDE =====
    story.append(Paragraph("15. Usage Guide", styles['SectionHeader']))

    story.append(Paragraph("15.1 Getting Started", styles['SubsectionHeader']))

    usage_steps = [
        "<b>Create Account:</b> Navigate to the signup page and create a new account with email, username, and password",
        "<b>Login:</b> Use your credentials to log in and receive a JWT token",
        "<b>Submit Repository:</b> Enter a public GitHub repository URL (e.g., https://github.com/owner/repo) and optionally specify a branch",
        "<b>Wait for Analysis:</b> The system will clone the repository, analyze the code, and calculate scores",
        "<b>View Results:</b> Review security, maintainability, and architecture scores on the dashboard",
        "<b>Read AI Insights:</b> Check the AI-generated explanation for actionable recommendations",
        "<b>Download Report:</b> Generate a PDF report for documentation or stakeholder communication"
    ]

    for i, step in enumerate(usage_steps, 1):
        story.append(Paragraph(f"{i}. {step}", styles['BulletText']))

    story.append(Paragraph("15.2 Interpreting Results", styles['SubsectionHeader']))

    story.append(Paragraph(
        """<b>Security Score:</b> Higher is better. Focus on CRITICAL and HIGH severity issues first.
        A score below 60 indicates significant security concerns that should be addressed before
        deployment.""",
        styles['CustomBody']
    ))

    story.append(Paragraph(
        """<b>Maintainability Score:</b> Higher is better. Scores below 65 suggest the codebase
        may be difficult to maintain. Focus on reducing complexity in flagged modules.""",
        styles['CustomBody']
    ))

    story.append(Paragraph(
        """<b>Architecture Score:</b> Higher is better. Low scores may indicate circular dependencies,
        poor modularity, or architectural anti-patterns. Consider refactoring highly-coupled modules.""",
        styles['CustomBody']
    ))

    story.append(Paragraph(
        """<b>Technical Debt:</b> Lower is better (it's debt!). Use the refactoring urgency level
        to prioritize remediation efforts.""",
        styles['CustomBody']
    ))

    story.append(PageBreak())

    # ===== 16. FUTURE ENHANCEMENTS =====
    story.append(Paragraph("16. Future Enhancements", styles['SectionHeader']))

    story.append(Paragraph(
        """The following enhancements are planned or under consideration for future releases:""",
        styles['CustomBody']
    ))

    future_features = [
        "<b>Language Support Expansion:</b> Add support for Java, Go, Rust, and other languages",
        "<b>CI/CD Integration:</b> GitHub Actions, GitLab CI, and Jenkins plugins",
        "<b>Trend Analysis:</b> Track code quality metrics over time across multiple analyses",
        "<b>Team Features:</b> Organization accounts, shared dashboards, and role-based access",
        "<b>Custom Rules:</b> Allow users to define custom security patterns and thresholds",
        "<b>Private Repository Support:</b> Authentication for private GitHub repositories",
        "<b>Real-time Monitoring:</b> Webhook-based analysis on push events",
        "<b>IDE Extensions:</b> VS Code and JetBrains extensions for in-editor analysis",
        "<b>Automated Fix Suggestions:</b> AI-powered code fix recommendations",
        "<b>Docker Support:</b> Containerized deployment option"
    ]

    for feature in future_features:
        story.append(Paragraph(f"• {feature}", styles['BulletText']))

    story.append(Spacer(1, 0.5*inch))

    # ===== CLOSING =====
    story.append(Paragraph("Document Information", styles['SectionHeader']))

    doc_info = [
        ["Attribute", "Value"],
        ["Document Title", "AI Code Intelligence & Risk Analyzer - Documentation"],
        ["Version", "1.0.0"],
        ["Generated Date", datetime.now().strftime('%B %d, %Y at %H:%M')],
        ["Total Pages", "16+"],
        ["Author", "Auto-generated Documentation"]
    ]

    table = Table(doc_info, colWidths=[2*inch, 4*inch])
    table.setStyle(create_table_style())
    story.append(table)

    # Build PDF
    doc.build(story)
    print("PDF documentation generated successfully: AI_Code_Intelligence_Documentation.pdf")


if __name__ == "__main__":
    generate_pdf()
