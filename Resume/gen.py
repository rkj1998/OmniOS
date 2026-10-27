import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf(filename, track_data):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=26,
        rightMargin=26,
        topMargin=26,
        bottomMargin=26
    )

    PRIMARY = colors.HexColor("#0f2c42")    # Deep Navy
    TEAL = colors.HexColor("#007791")       # Accent Teal
    DARK_TEXT = colors.HexColor("#1f2937")  # Charcoal body
    MUTED_TEXT = colors.HexColor("#4b5563") # Subtitles/meta
    LIGHT_BG = colors.HexColor("#f4f7f9")   # Sidebar tint
    LINE_COLOR = colors.HexColor("#cbd5e1") # Divider line

    style_name = ParagraphStyle('Name', fontName='Helvetica-Bold', fontSize=20, leading=23, textColor=PRIMARY, spaceAfter=2)
    style_target_title = ParagraphStyle('TargetTitle', fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=TEAL, spaceAfter=7)
    style_sidebar_h = ParagraphStyle('SidebarH', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=PRIMARY, spaceBefore=8, spaceAfter=3, textTransform='uppercase')
    style_main_h = ParagraphStyle('MainH', fontName='Helvetica-Bold', fontSize=10.5, leading=13.5, textColor=PRIMARY, spaceBefore=8, spaceAfter=4, textTransform='uppercase')
    style_sidebar_body = ParagraphStyle('SidebarB', fontName='Helvetica', fontSize=8.2, leading=11, textColor=DARK_TEXT, spaceAfter=3.5)
    style_sidebar_meta = ParagraphStyle('SidebarM', fontName='Helvetica', fontSize=7.8, leading=10, textColor=MUTED_TEXT, spaceAfter=5)
    style_job_title = ParagraphStyle('JobTitle', fontName='Helvetica-Bold', fontSize=9.2, leading=11.5, textColor=PRIMARY)
    style_job_meta = ParagraphStyle('JobMeta', fontName='Helvetica-Bold', fontSize=8.2, leading=10.5, textColor=TEAL, spaceAfter=2.5)
    style_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8.2, leading=11, textColor=DARK_TEXT, spaceAfter=3.5)
    style_bullet = ParagraphStyle('Bullet', fontName='Helvetica', fontSize=8, leading=10.6, textColor=DARK_TEXT, leftIndent=8, firstLineIndent=-8, spaceAfter=2)

    # ------------------- LEFT COLUMN -------------------
    left_flow = []
    left_flow.append(Paragraph("CONTACT", style_sidebar_h))
    left_flow.append(Paragraph("<b>Email:</b> rahuljha190398@gmail.com", style_sidebar_body))
    left_flow.append(Paragraph("<b>Phone:</b> (782) 778-5607", style_sidebar_body))
    left_flow.append(Paragraph("<b>Location:</b> Calgary, AB", style_sidebar_body))
    left_flow.append(Paragraph("<b>LinkedIn:</b> in/rahul-jha-480841168", style_sidebar_body))

    left_flow.append(Paragraph("EDUCATION", style_sidebar_h))
    left_flow.append(Paragraph("<b>M.Eng. Electrical & Computer</b>", style_sidebar_body))
    left_flow.append(Paragraph("University of Calgary | 2024<br/><b>GPA: 3.64 / 4.0</b> | Minor: Energy", style_sidebar_meta))
    left_flow.append(Paragraph("<b>B.Tech. Computer Science</b>", style_sidebar_body))
    left_flow.append(Paragraph("REVA University | 2022<br/><b>GPA: 8.70 / 10.0</b>", style_sidebar_meta))

    left_flow.append(Paragraph("TECHNICAL SKILLS", style_sidebar_h))
    for cat_title, cat_skills in track_data["skills"]:
        left_flow.append(Paragraph(f"<b>{cat_title}:</b><br/>{cat_skills}", style_sidebar_body))

    left_flow.append(Paragraph("CERTIFICATIONS", style_sidebar_h))
    left_flow.append(Paragraph("• AWS Fundamentals (2020)<br/>• Data Science Specialization (2020)<br/>• Google Cloud 30-Day Track (2020)<br/>• Blockchain Architecture (2020)", style_sidebar_body))

    # ------------------- RIGHT COLUMN -------------------
    right_flow = []
    right_flow.append(Paragraph("RAHUL JHA", style_name))
    right_flow.append(Paragraph(track_data["headline"], style_target_title))

    right_flow.append(Paragraph("PROFESSIONAL SUMMARY", style_main_h))
    right_flow.append(Paragraph(track_data["summary"], style_body))

    right_flow.append(Paragraph("PROFESSIONAL EXPERIENCE", style_main_h))
    for job in track_data["experience"]:
        right_flow.append(Paragraph(job["title"], style_job_title))
        right_flow.append(Paragraph(job["meta"], style_job_meta))
        for bullet in job["bullets"]:
            right_flow.append(Paragraph(f"• {bullet}", style_bullet))
        right_flow.append(Spacer(1, 3))

    # Two Column Layout (170pt sidebar + 390pt main = 560pt total printable width)
    container_table = Table([[left_flow, right_flow]], colWidths=[170, 390])
    container_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), LIGHT_BG),
        ('RIGHTPADDING', (0,0), (0,0), 9),
        ('LEFTPADDING', (0,0), (0,0), 9),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (1,0), (1,0), 13),
        ('RIGHTPADDING', (1,0), (1,0), 4),
        ('LINEAFTER', (0,0), (0,-1), 0.75, LINE_COLOR),
    ]))

    doc.build([container_table])
    print(f"Generated: {filename}")


# ==============================================================================
# DATA FOR THE 3 SPECIALIZED PROFILES
# ==============================================================================

# TRACK A: APPLIED AI / ML PLATFORM (AltaML & Tailscale AI Automation)
track_a = {
    "headline": "Applied AI Engineer | Autonomous Agents & ML Platform Systems",
    "summary": (
        "Applied AI & Systems Engineer with an M.Eng. in Electrical & Computer Engineering from U of C. "
        "Specialized in architecting agentic workflows, deterministic verification gateways for autonomous tool-calling "
        "agents, and scalable model serving pipelines. Experienced in fine-tuning open-weights models (DeepSeek, GLM), "
        "multiprocessing backend orchestration, and bridging time-series ML models with enterprise cloud infrastructure."
    ),
    "skills": [
        ("AI & Orchestration", "Agentic Workflows, LangChain/LangGraph, DeepSeek, GLM, Prompt Optimization, AST Verification, Function Calling"),
        ("Languages", "Python (NumPy, Pandas, AsyncIO, PyTorch), C++, SQL, Bash, Dart"),
        ("Data & Serving", "FastAPI, Flask, InfluxDB, PostgreSQL, Redis, High-Throughput REST APIs"),
        ("Cloud & Ops", "Docker, Kubernetes, AWS, GCP, CI/CD, Linux/Unix, Git"),
        ("Testing & Quality", "Deterministic Verification, Schema Assertions, Model Evals, Benchmark Profiling")
    ],
    "experience": [
        {
            "title": "Lead AI & Backend Systems Developer",
            "meta": "TR PRO | Calgary, AB | Jan 2023 – Present",
            "bullets": [
                "Engineered agentic tool-use pipelines integrating fine-tuned DeepSeek and open-weights reasoning models, maintaining >99% parsing accuracy on unstructured financial signals.",
                "Architected a deterministic verification gateway intercepting autonomous tool calls, enforcing strict parameter schemas, AST validation, and dry-run sandboxing before external execution.",
                "Built an asynchronous Python task-execution engine handling multi-timeframe regime analysis across distributed workers, boosting processing throughput by 500%.",
                "Designed dynamic webhook rule evaluators mapping continuous feature vectors to optimal execution states with sub-millisecond dispatch latency."
            ]
        },
        {
            "title": "Project Engineer | Process Telemetry & ML Automation",
            "meta": "Litus Inc. | Calgary, AB | May 2024 – June 2026",
            "bullets": [
                "Architected automated time-series data pipelines ingesting 500,000+ monthly sensor points via Modbus TCP, synchronizing edge telemetry with central cloud analytics.",
                "Engineered multivariate anomaly detection models in Python (NumPy/Pandas) analyzing pH, flow, and residence times, driving a 30% increase in lithium extraction yield.",
                "Integrated automated test environments and REST APIs for analytical instrumentation (NMR spectrometers), eliminating manual logging overhead.",
                "Built custom data-visualization and automated telemetry reporting dashboards in Python, accelerating R&D validation cycles by 40%."
            ]
        },
        {
            "title": "Software Engineer",
            "meta": "FIS | Bengaluru, India | Feb 2022 – Sept 2022",
            "bullets": [
                "Maintained 99.5% accuracy in enterprise automated data processing for global financial clients including RBC, BMO, and PayPal.",
                "Authored proactive health-monitoring scripts in Python and Bash, decreasing system downtime by 20% across high-volume transaction environments.",
                "Configured distributed Big Data pipeline connectors in ZENA, ensuring 100% SLA compliance for production job schedules."
            ]
        },
        {
            "title": "Software Developer",
            "meta": "Codertech | Bengaluru, India | Aug 2020 – Jan 2022",
            "bullets": [
                "Engineered scalable backend REST endpoints and Flutter UI modules, supporting concurrent live sessions for 60+ users.",
                "Integrated Firebase Cloud Firestore rules and payment workflows, increasing transaction completion rates by 25%."
            ]
        },
        {
            "title": "Mobile Application Intern",
            "meta": "REVA NEST Incubator | Bengaluru, India | Feb 2020 – May 2020",
            "bullets": [
                "Developed native Android modules using Java, implementing background thread schedulers and local SQLite caching.",
                "Executed automated unit and integration tests across target Android OS builds to prevent UI latency and memory leaks."
            ]
        }
    ]
}

# TRACK B: SYSTEMS, NETWORKING & SECURITY (Chainguard & Tailscale Infrastructure)
track_b = {
    "headline": "Systems & Infrastructure Engineer | Networking, Security & Cloud Runtimes",
    "summary": (
        "Systems Engineer with a Master’s degree in Electrical & Computer Engineering from the University of Calgary. "
        "Experienced in network boundary enforcement, socket-level communication (TCP/IP, Modbus), Linux container runtimes "
        "(Docker, K8s), and runtime sandboxing. Proven track record in building fault-tolerant data pipelines, AST code "
        "verification, and enforcing zero-trust data integrity standards across high-throughput enterprise infrastructure."
    ),
    "skills": [
        ("Systems & Network", "Socket Programming, TCP/IP, Modbus TCP, Zero-Trust Architecture, Linux Internals, POSIX, AST Code Analysis"),
        ("Languages", "C++, Python (Multi-proc, AsyncIO), C#, Java, Bash, SQL"),
        ("Cloud & Containers", "Docker, Kubernetes, AWS, GCP, Container Hardening, CI/CD Security"),
        ("Data & Storage", "PostgreSQL, SQLite, Redis, Edge-to-Cloud Telemetry Synchronization"),
        ("Security & Testing", "Runtime Policy Enforcement, Sandbox Dry-Runs, Health Diagnostics, Strict SLA Compliance")
    ],
    "experience": [
        {
            "title": "Systems Automation & Network Engineer",
            "meta": "Litus Inc. | Calgary, AB | May 2024 – June 2026",
            "bullets": [
                "Designed and deployed secure edge-to-cloud telemetry pipelines, streaming 500,000+ monthly data points over Modbus TCP and encrypted network sockets with zero packet loss.",
                "Engineered multi-threaded Python daemon services for continuous instrument polling, logging 1,440 data points per unit daily while enforcing rigorous data integrity checks.",
                "Configured hardened Linux runtime environments and secure REST APIs for specialized NMR analytical equipment to isolate proprietary data from public networks.",
                "Engineered real-time process monitoring tools in Python, optimizing resource utilization and system stability across pilot facilities."
            ]
        },
        {
            "title": "Lead Systems & Infrastructure Developer",
            "meta": "TR PRO | Calgary, AB | Jan 2023 – Present",
            "bullets": [
                "Architected a distributed execution backend in multi-process Python and AsyncIO, scaling concurrent socket throughput by 500% under high-frequency workloads.",
                "Built an AST-based code analysis sandbox that inspects and validates dynamically generated code payloads, preventing unauthorized system calls and privilege escalation.",
                "Implemented network egress boundary policies and webhook validation layers, isolating untrusted inputs and mitigating containment escape vulnerabilities.",
                "Optimized core execution algorithms for sub-millisecond execution, implementing strict memory validation and thread-safe locks to eliminate race conditions."
            ]
        },
        {
            "title": "Software Engineer | Infrastructure Reliability",
            "meta": "FIS | Bengaluru, India | Feb 2022 – Sept 2022",
            "bullets": [
                "Enforced strict infrastructure security and SLA compliance for mission-critical banking partners including RBC, BMO, and PayPal.",
                "Developed proactive health-check scripts in Bash and Python to detect memory anomalies and network dropouts, reducing infrastructure downtime by 20%.",
                "Managed automated job orchestration in ZENA and validated data integrity across distributed production databases."
            ]
        },
        {
            "title": "Software Developer",
            "meta": "Codertech | Bengaluru, India | Aug 2020 – Jan 2022",
            "bullets": [
                "Architected authenticated REST APIs and client-server workflows using Flutter and Cloud Firestore, securing sensitive client transactions.",
                "Hardened mobile payment integrations and referral tracking logic, boosting transaction success rates by 25%."
            ]
        },
        {
            "title": "Mobile Application Intern",
            "meta": "REVA NEST Incubator | Bengaluru, India | Feb 2020 – May 2020",
            "bullets": [
                "Engineered secure local storage logic using SQLite and validated network request payloads across native Android applications in Java.",
                "Conducted security profiling and memory leak audits across diverse mobile configurations prior to deployment."
            ]
        }
    ]
}

# TRACK C: CORE BACKEND & DISTRIBUTED SYSTEMS (Tailscale Product / General Backend)
track_c = {
    "headline": "Backend & Distributed Systems Engineer | High-Throughput Services & APIs",
    "summary": (
        "Backend Systems Engineer with an M.Eng. in Electrical & Computer Engineering from the University of Calgary. "
        "Track record of designing scalable microservices, low-latency multi-process architectures, and asynchronous data "
        "pipelines. Experienced in bridging high-throughput backend services with interactive desktop/web frontends, database "
        "optimization, and automated end-to-end integration testing."
    ),
    "skills": [
        ("Backend & Systems", "Multi-processing, AsyncIO, RESTful APIs, Microservices, Sockets (TCP/IP), High-Throughput Ingestion"),
        ("Languages", "Python, C++, Java, Dart, SQL, Bash"),
        ("Databases & Storage", "PostgreSQL, SQLite, Firestore, Redis, Time-Series Data Stores"),
        ("Cloud & Tools", "Docker, Kubernetes, AWS, GCP, CI/CD, Git, Linux/Unix, JIRA"),
        ("Full-Stack & GUI", "Flask, Flutter (Desktop/Mobile), Qt/UI Principles, Automated Unit/Integration Testing")
    ],
    "experience": [
        {
            "title": "Lead Backend & Systems Developer",
            "meta": "TR PRO | Calgary, AB | Jan 2023 – Present",
            "bullets": [
                "Architected a distributed backend engine utilizing multi-process Python and asynchronous task scheduling, boosting request throughput by 500%.",
                "Engineered high-throughput execution logic optimized for sub-millisecond latency, incorporating strict thread-safety and validation safeguards.",
                "Designed and deployed a dynamic rules engine supporting 8 distinct webhook strategies and real-time state synchronization.",
                "Spearheaded development of a modern desktop/web GUI using Flutter paired with Flask microservices, reducing customer support tickets by 35%."
            ]
        },
        {
            "title": "Project Engineer | Systems & Software Automation",
            "meta": "Litus Inc. | Calgary, AB | May 2024 – June 2026",
            "bullets": [
                "Architected automated telemetry data pipelines synchronizing 500,000+ monthly sensor points via Modbus TCP to centralized cloud storage.",
                "Engineered multi-threaded Python services for automated logging, generating 1,440 reliable data points per instrument daily.",
                "Analyzed high-frequency operational time-series data using Python (Pandas/NumPy), identifying bottlenecks and optimizing recovery by 30%.",
                "Developed proprietary internal ERP tools and diagnostic visualization software, accelerating engineering team workflows by 40%."
            ]
        },
        {
            "title": "Software Engineer",
            "meta": "FIS | Bengaluru, India | Feb 2022 – Sept 2022",
            "bullets": [
                "Ensured 99.5% accuracy in end-of-day data batch processing for tier-one global financial institutions including RBC and PayPal.",
                "Built automated health-monitoring and recovery scripts in Python and Bash, reducing production downtime by 20%.",
                "Configured mission-critical enterprise workflows in ZENA and established high-availability Big Data connections."
            ]
        },
        {
            "title": "Software Developer",
            "meta": "Codertech | Bengaluru, India | Aug 2020 – Jan 2022",
            "bullets": [
                "Developed cross-platform applications using Dart/Flutter and REST APIs, supporting concurrent live sessions for 60+ users.",
                "Integrated Firebase and Cloud Firestore for real-time state persistence and hardened user payment workflows."
            ]
        },
        {
            "title": "Mobile Application Intern",
            "meta": "REVA NEST Incubator | Bengaluru, India | Feb 2020 – May 2020",
            "bullets": [
                "Built native Android client services using Java, optimizing background thread performance and SQLite data caching.",
                "Conducted automated unit testing and API contract validation across multi-device test suites."
            ]
        }
    ]
}

if __name__ == "__main__":
    generate_pdf("Rahul_Jha_TrackA_AppliedAI_AltaML.pdf", track_a)
    generate_pdf("Rahul_Jha_TrackB_SystemsSecurity_Chainguard_Tailscale.pdf", track_b)
    generate_pdf("Rahul_Jha_TrackC_CoreBackend_Product.pdf", track_c)
    print("\nAll 3 PDF resumes successfully built!")