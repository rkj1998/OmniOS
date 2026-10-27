import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import ParagraphStyle

# PolicyMe Brand-Aligned Visual Palette (Modern FinTech Navy & Emerald/Cyan Accent)
PRIMARY = colors.HexColor("#0d2137")        # Deep Trust Navy
TEAL_ACCENT = colors.HexColor("#0e9488")    # Modern InsurTech Teal
DARK_TEXT = colors.HexColor("#1f2937")      # Charcoal body text
MUTED_TEXT = colors.HexColor("#4b5563")     # Metadata grey
LIGHT_BG = colors.HexColor("#f0fdfa")       # Soft mint/cyan sidebar tint
LINE_COLOR = colors.HexColor("#cbd5e1")     # Structural Divider

def build_policyme_resume(filename="Rahul_Jha_PolicyMe_Senior_FullStack_AI_Resume.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=24,
        rightMargin=24,
        topMargin=22,
        bottomMargin=22
    )

    style_name = ParagraphStyle('Name', fontName='Helvetica-Bold', fontSize=18, leading=21, textColor=PRIMARY, spaceAfter=2)
    style_target_title = ParagraphStyle('TargetTitle', fontName='Helvetica-Bold', fontSize=8.8, leading=11, textColor=TEAL_ACCENT, spaceAfter=5)
    style_sidebar_h = ParagraphStyle('SidebarH', fontName='Helvetica-Bold', fontSize=9, leading=11.5, textColor=PRIMARY, spaceBefore=6, spaceAfter=2.5, textTransform='uppercase')
    style_main_h = ParagraphStyle('MainH', fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=PRIMARY, spaceBefore=6, spaceAfter=3, textTransform='uppercase')
    style_sidebar_body = ParagraphStyle('SidebarB', fontName='Helvetica', fontSize=7.5, leading=9.8, textColor=DARK_TEXT, spaceAfter=2.5)
    style_sidebar_meta = ParagraphStyle('SidebarM', fontName='Helvetica', fontSize=7.2, leading=9.2, textColor=MUTED_TEXT, spaceAfter=4)
    style_job_title = ParagraphStyle('JobTitle', fontName='Helvetica-Bold', fontSize=8.6, leading=10.5, textColor=PRIMARY)
    style_job_meta = ParagraphStyle('JobMeta', fontName='Helvetica-Bold', fontSize=7.6, leading=9.5, textColor=TEAL_ACCENT, spaceAfter=1.5)
    style_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=7.5, leading=9.8, textColor=DARK_TEXT, spaceAfter=2.5)
    style_bullet = ParagraphStyle('Bullet', fontName='Helvetica', fontSize=7.3, leading=9.4, textColor=DARK_TEXT, leftIndent=7, firstLineIndent=-7, spaceAfter=1.5)

    # Left Column (Sidebar)
    left_flow = []
    left_flow.append(Paragraph("CONTACT", style_sidebar_h))
    left_flow.append(Paragraph("<b>Email:</b> rahuljha190398@gmail.com", style_sidebar_body))
    left_flow.append(Paragraph("<b>Phone:</b> (782) 778-5607", style_sidebar_body))
    left_flow.append(Paragraph("<b>Location:</b> Canada (Remote)", style_sidebar_body))
    left_flow.append(Paragraph("<b>LinkedIn:</b> in/rahul-jha-480841168", style_sidebar_body))
    left_flow.append(Paragraph("<b>Work Auth:</b> Authorized in Canada (No Sponsorship)", style_sidebar_body))

    left_flow.append(Paragraph("EDUCATION", style_sidebar_h))
    left_flow.append(Paragraph("<b>M.Eng. Electrical & Computer</b>", style_sidebar_body))
    left_flow.append(Paragraph("University of Calgary | 2024<br/><b>GPA: 3.64 / 4.0</b> | Minor: Energy", style_sidebar_meta))
    left_flow.append(Paragraph("<b>B.Tech. Computer Science</b>", style_sidebar_body))
    left_flow.append(Paragraph("REVA University | 2022<br/><b>GPA: 8.70 / 10.0</b>", style_sidebar_meta))

    left_flow.append(Paragraph("TECHNICAL PROFICIENCIES", style_sidebar_h))
    left_flow.append(Paragraph("<b>Full Stack Web:</b><br/>Python, React, Redux, Node.js, TypeScript/JavaScript, REST APIs, Webhooks, Flask", style_sidebar_body))
    left_flow.append(Paragraph("<b>AI & Agentic Systems:</b><br/>LangChain, LangGraph, n8n automation, Agent Tool Calling, RAG Pipelines, Schema Enforcement, AST Verification", style_sidebar_body))
    left_flow.append(Paragraph("<b>Databases & Storage:</b><br/>PostgreSQL, SQLite, Firestore, Redis concepts, Data Integrity & Migrations", style_sidebar_body))
    left_flow.append(Paragraph("<b>Cloud & Security:</b><br/>AWS (Lambda, S3, API Gateway), GCP, Docker, Kubernetes, CI/CD, Linux/Unix, SLA Compliance (99.5%)", style_sidebar_body))
    left_flow.append(Paragraph("<b>Engineering Practices:</b><br/>Distributed Systems, AsyncIO, Multi-threading, Observability, Unit Testing, Agile/Scrum", style_sidebar_body))

    left_flow.append(Paragraph("CERTIFICATIONS", style_sidebar_h))
    left_flow.append(Paragraph("• AWS Fundamentals (2020)<br/>• Data Science Specialization (2020)<br/>• Google Cloud 30-Day Track (2020)<br/>• Blockchain Architecture (2020)", style_sidebar_body))

    # Right Column (Main Experience)
    right_flow = []
    right_flow.append(Paragraph("RAHUL JHA", style_name))
    right_flow.append(Paragraph("Senior Software Engineer | Full Stack Systems, Python/React, AI Agents & Cloud Infrastructure", style_target_title))

    right_flow.append(Paragraph("PROFESSIONAL SUMMARY", style_main_h))
    right_flow.append(Paragraph(
        "Full Stack and Systems Engineer with a Master’s degree in Electrical & Computer Engineering from the "
        "University of Calgary (GPA: 3.64). Demonstrated track record of architecting scalable web applications, "
        "integrating autonomous AI agentic workflows (LangChain, LangGraph concepts, AST validation), and operating "
        "high-reliability cloud services across AWS. Experienced in full lifecycle feature delivery—combining reactive "
        "frontend interfaces (React, Flutter) with asynchronous Python backend services and secure PostgreSQL datastores. "
        "Adept at taking ambiguous product requirements, designing secure and observable microservices, and mentoring engineering "
        "teams to modernize complex customer-facing workflows.",
        style_body
    ))

    right_flow.append(Paragraph("PROFESSIONAL EXPERIENCE", style_main_h))

    # 1. TR PRO
    right_flow.append(Paragraph("Lead Backend & AI Systems Developer (Full Stack Execution)", style_job_title))
    right_flow.append(Paragraph("TR PRO | Calgary, AB | Jan 2023 – Present", style_job_meta))
    tr_bullets = [
        "Architected a distributed execution engine utilizing multi-process Python and asynchronous task scheduling, boosting system processing throughput by 500% across concurrent broker data streams.",
        "Engineered sub-millisecond execution logic, incorporating rigorous thread safety, validation checks, and memory safeguards to prevent race conditions during real-time transactions.",
        "Engineered dynamic rules engines for 8 distinct webhook data streams, synchronizing low-latency analytics across real-time multi-threaded environments.",
        "Implemented production agentic AI tool-calling workflows and deterministic validation gateways (AST code verification, schema assertion), ensuring zero unauthorized executions on external APIs.",
        "Built responsive client GUIs in Flutter paired with a robust Flask microservices backend, cutting client technical support overhead by 35%."
    ]
    for b in tr_bullets:
        right_flow.append(Paragraph(f"• {b}", style_bullet))
    right_flow.append(Spacer(1, 2))

    # 2. Litus Inc.
    right_flow.append(Paragraph("Project Engineer | Software & Industrial Automation", style_job_title))
    right_flow.append(Paragraph("Litus Inc. | Calgary, AB | May 2024 – June 2025", style_job_meta))
    litus_bullets = [
        "Architected end-to-end telemetry and automated data pipelines, processing 500,000+ monthly sensor data points via Modbus TCP protocols with zero data loss.",
        "Engineered multi-threaded Python automation services for real-time instrument telemetry, achieving 1,440 automated logs per unit daily and eliminating manual overhead.",
        "Analyzed multi-variable time-series process data (Python, Pandas, NumPy) to isolate system bottlenecks, driving a 30% optimization in system recovery efficiency.",
        "Engineered specialized testing environments for analytical instrumentation (NMR equipment), creating robust REST APIs to synchronize edge analytics with central servers.",
        "Developed custom internal ERP modules, diagnostics suites, and data visualization interfaces, streamlining daily cross-functional workflows by 40%."
    ]
    for b in litus_bullets:
        right_flow.append(Paragraph(f"• {b}", style_bullet))
    right_flow.append(Spacer(1, 2))

    # 3. FIS
    right_flow.append(Paragraph("Software Engineer | Financial Reliability & Transaction Systems", style_job_title))
    right_flow.append(Paragraph("FIS | Bengaluru, India | Feb 2022 – Sept 2022", style_job_meta))
    fis_bullets = [
        "Maintained 99.5% operational precision in automated end-of-day transaction pipelines for tier-one global financial institutions including RBC, BMO, and PayPal.",
        "Reduced system downtime by 20% by authoring proactive health-check diagnostics and automated fault-recovery scripts in Python and Bash.",
        "Configured mission-critical enterprise workflows in ZENA and established distributed Big Data connectors, accelerating issue resolution cycles by 15%."
    ]
    for b in fis_bullets:
        right_flow.append(Paragraph(f"• {b}", style_bullet))
    right_flow.append(Spacer(1, 2))

    # 4. Codertech
    right_flow.append(Paragraph("Software Developer", style_job_title))
    right_flow.append(Paragraph("Codertech | Bengaluru, India | Aug 2020 – Jan 2022", style_job_meta))
    codertech_bullets = [
        "Engineered cross-platform applications (Flutter/Dart) integrating secure REST APIs, scaling to support 60+ concurrent active video/data sessions.",
        "Integrated Cloud Firestore architecture and secure payment pipelines, boosting transaction success rates by 25% with end-to-end data validation."
    ]
    for b in codertech_bullets:
        right_flow.append(Paragraph(f"• {b}", style_bullet))
    right_flow.append(Spacer(1, 2))

    # 5. REVA NEST Incubator
    right_flow.append(Paragraph("Mobile Application Intern", style_job_title))
    right_flow.append(Paragraph("REVA NEST Incubator | Bengaluru, India | Feb 2020 – May 2020", style_job_meta))
    reva_bullets = [
        "Developed native Android modules using Java and Android SDK, optimizing local SQLite database caching and UI thread responsiveness.",
        "Implemented asynchronous background services for real-time JSON payload parsing and conducted multi-device QA profiling."
    ]
    for b in reva_bullets:
        right_flow.append(Paragraph(f"• {b}", style_bullet))

    # Assemble into Clean 2-Column Table
    container_table = Table([[left_flow, right_flow]], colWidths=[165, 395])
    container_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), LIGHT_BG),
        ('RIGHTPADDING', (0,0), (0,0), 8),
        ('LEFTPADDING', (0,0), (0,0), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (1,0), (1,0), 12),
        ('RIGHTPADDING', (1,0), (1,0), 4),
        ('LINEAFTER', (0,0), (0,-1), 0.75, LINE_COLOR),
    ]))

    doc.build([container_table])
    print(f"Generated PolicyMe Resume: {filename}")

if __name__ == "__main__":
    build_policyme_resume()