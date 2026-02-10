from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

# Create PDF
pdf_path = "resume.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
story = []
styles = getSampleStyleSheet()

# Define custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#2c3e50'),
    spaceAfter=6,
    alignment=1  # Center
)

subtitle_style = ParagraphStyle(
    'Subtitle',
    parent=styles['Normal'],
    fontSize=11,
    textColor=colors.HexColor('#333'),
    spaceAfter=3,
    alignment=1
)

section_heading = ParagraphStyle(
    'SectionHeading',
    parent=styles['Heading2'],
    fontSize=12,
    textColor=colors.HexColor('#2c3e50'),
    spaceAfter=8,
    spaceBefore=4,
    borderPadding=3,
    borderColor=colors.HexColor('#3498db'),
    borderWidth=0,
    borderBottom=2
)

job_title_style = ParagraphStyle(
    'JobTitle',
    parent=styles['Heading3'],
    fontSize=11,
    textColor=colors.HexColor('#2c3e50'),
    spaceAfter=2,
    borderPadding=0
)

date_style = ParagraphStyle(
    'DateStyle',
    parent=styles['Normal'],
    fontSize=9,
    textColor=colors.HexColor('#666'),
    spaceAfter=4,
    italic=True
)

body_style = ParagraphStyle(
    'BodyStyle',
    parent=styles['Normal'],
    fontSize=9.5,
    textColor=colors.HexColor('#555'),
    spaceAfter=4,
    leading=11
)

# Header with name and contact
story.append(Paragraph("BRAD OSWALD", title_style))
story.append(Paragraph("Revenue-Owning Systems Builder | B2B E-commerce | AI / ML &amp; Analytics", subtitle_style))
story.append(Spacer(1, 0.1*inch))

contact_text = "Annapolis, MD • <a href='mailto:bradoswald@msn.com'>bradoswald@msn.com</a> • 410.662.2165 • linkedin.com/in/bradoswald"
story.append(Paragraph(contact_text, date_style))
story.append(Spacer(1, 0.15*inch))

# Professional Summary
story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
summary_text = """Revenue-owning systems builder who now speaks AI fluently. Senior operator and technical leader with 15+ years building and scaling growth engines across renewable energy and logistics &amp; distribution. Architected and managed a B2B e-commerce platform generating <b>$28M+ annually</b>, including ERP integrations, API-connected services, and customer and sales portals. Owns full sales data since platform launch and applies analytics, statistical modeling, and machine learning to optimize decisions and scale revenue impact."""
story.append(Paragraph(summary_text, body_style))
story.append(Spacer(1, 0.08*inch))

# Core Skills
story.append(Paragraph("CORE SKILLS", section_heading))
skills_text = """<b>Programming:</b> Python, R, SQL, JavaScript<br/>
<b>ML / AI:</b> Supervised Learning, Unsupervised Learning, Deep Learning, Natural Language Processing<br/>
<b>Libraries &amp; Tools:</b> Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, Matplotlib, Seaborn<br/>
<b>Analytics:</b> Data Analysis, Statistical Modeling, Data Visualization, Business Intelligence<br/>
<b>Systems:</b> B2B E-commerce, ERP (P21), APIs, Sales Portals, Customer Account Platforms"""
story.append(Paragraph(skills_text, body_style))
story.append(Spacer(1, 0.08*inch))

# Experience
story.append(Paragraph("EXPERIENCE", section_heading))

jobs = [
    {
        "title": "S. Freedman &amp; Sons, Inc. — Marketing Director",
        "dates": "Oct 2016 – Present • Landover, MD",
        "bullets": [
            "Hired to lead all marketing and digital initiatives for a 110-year-old logistics and distribution company.",
            "<b>Architected and scaled a B2B e-commerce platform generating $28M+ in annual revenue</b>, now a core revenue engine.",
            "Built and operated a <b>12,000+ SKU</b> online catalog supporting complex B2B pricing and account structures.",
            "Led <b>end-to-end integration with P21 ERP</b>, enabling real-time inventory, pricing, customer, and order data synchronization.",
            "Designed and managed <b>API-connected systems</b>, customer portals, and sales-rep portals used daily by internal teams.",
            "Own and analyze <b>complete sales data since platform launch</b>, using reporting and analytics to guide pricing and growth strategy.",
            "Recruited and managed marketing talent and external partners across brand, demand, and platform initiatives."
        ]
    },
    {
        "title": "ImpactOffice — Director of Marketing",
        "dates": "Sep 2012 – Oct 2016 • Washington, DC–Baltimore Area",
        "bullets": [
            "Led company-wide marketing strategy focused on engagement, demand generation, and revenue enablement.",
            "Partnered with national brands including Keurig, BiC, Energizer, Honest Tea, and 3M on campaigns supporting sales growth.",
            "Built repeatable systems across social, email, sales outreach, and vendor promotions.",
            "Implemented ROI-focused reporting to improve campaign performance and inbound lead flow."
        ]
    },
    {
        "title": "SunEdison — Sr. Marketing Communications Manager",
        "dates": "Jan 2011 – Jun 2012 • Beltsville, MD",
        "bullets": [
            "Promoted to lead public relations strategy in a fast-scaling renewable energy environment.",
            "Managed trade show and event budgets exceeding <b>$250K</b>.",
            "Developed sales enablement tools including mobile applications, webinars, and digital collateral."
        ]
    },
    {
        "title": "SunEdison — Marketing Manager",
        "dates": "Jan 2007 – Dec 2010 • Beltsville, MD",
        "bullets": [
            "Supported brand growth through website launch, SEO strategy, and enterprise-facing marketing assets.",
            "Built tradeshow and speaking strategies and delivered ROI reporting.",
            "Supported launch of SunEdison's first utility-scale solar deployment with Xcel Energy (8.2MW, Alamosa, CO)."
        ]
    },
    {
        "title": "Oswald Consulting — Owner / Principal",
        "dates": "Jan 2005 – Jan 2007 • Northern Virginia",
        "bullets": [
            "Provided market research, competitive analysis, website development, rebranding, and business development strategy."
        ]
    }
]

for job in jobs:
    story.append(Paragraph(job["title"], job_title_style))
    story.append(Paragraph(job["dates"], date_style))
    for bullet in job["bullets"]:
        bullet_text = f"• {bullet}"
        story.append(Paragraph(bullet_text, body_style))
    story.append(Spacer(1, 0.06*inch))

# Education
story.append(Paragraph("EDUCATION", section_heading))
story.append(Paragraph("University of South Carolina–Columbia — Bachelor of Arts (BA), Media Arts", body_style))

# Build PDF
doc.build(story)
print(f"Resume PDF created: {pdf_path}")
