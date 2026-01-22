import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
from io import BytesIO
import re

def parse_resume_text(text):
    """Parse the input text into resume sections"""
    sections = {
        'name': '',
        'contact': '',
        'summary': '',
        'experience': [],
        'education': [],
        'skills': [],
        'projects': []
    }
    
    lines = text.strip().split('\n')
    current_section = None
    current_item = []
    
    # First line is usually the name
    if lines:
        sections['name'] = lines[0].strip()
    
    for i, line in enumerate(lines[1:], 1):
        line = line.strip()
        if not line:
            continue
            
        # Detect section headers
        lower_line = line.lower()
        if any(keyword in lower_line for keyword in ['email', 'phone', 'linkedin', 'github', '@']):
            if current_section == 'contact':
                sections['contact'] += ' | ' + line
            else:
                sections['contact'] = line
                current_section = 'contact'
        elif any(keyword in lower_line for keyword in ['summary', 'objective', 'about']):
            current_section = 'summary'
        elif any(keyword in lower_line for keyword in ['experience', 'work history', 'employment']):
            current_section = 'experience'
        elif any(keyword in lower_line for keyword in ['education', 'academic']):
            current_section = 'education'
        elif any(keyword in lower_line for keyword in ['skills', 'technical skills', 'competencies']):
            current_section = 'skills'
        elif any(keyword in lower_line for keyword in ['projects', 'personal projects']):
            current_section = 'projects'
        else:
            # Add content to current section
            if current_section == 'summary':
                sections['summary'] += ' ' + line
            elif current_section in ['experience', 'education', 'projects']:
                # Check if it's a new item (job title, degree, etc.)
                if line and (line[0].isupper() or re.match(r'^\d', line)):
                    if current_item:
                        sections[current_section].append('\n'.join(current_item))
                        current_item = []
                current_item.append(line)
            elif current_section == 'skills':
                sections['skills'].append(line)
    
    # Add last item
    if current_item and current_section in ['experience', 'education', 'projects']:
        sections[current_section].append('\n'.join(current_item))
    
    return sections

def create_resume_pdf(sections):
    """Generate ATS-friendly PDF from parsed sections"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles for ATS compatibility
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#000000'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#000000'),
        spaceAfter=6,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#000000'),
        borderPadding=0,
        backColor=None
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#000000'),
        spaceAfter=6,
        leading=14
    )
    
    # Add name
    if sections['name']:
        story.append(Paragraph(sections['name'], title_style))
    
    # Add contact info
    if sections['contact']:
        story.append(Paragraph(sections['contact'], contact_style))
    
    # Add summary
    if sections['summary']:
        story.append(Paragraph('<b>PROFESSIONAL SUMMARY</b>', heading_style))
        story.append(Paragraph(sections['summary'].strip(), body_style))
    
    # Add experience
    if sections['experience']:
        story.append(Paragraph('<b>WORK EXPERIENCE</b>', heading_style))
        for exp in sections['experience']:
            story.append(Paragraph(exp.replace('\n', '<br/>'), body_style))
            story.append(Spacer(1, 6))
    
    # Add education
    if sections['education']:
        story.append(Paragraph('<b>EDUCATION</b>', heading_style))
        for edu in sections['education']:
            story.append(Paragraph(edu.replace('\n', '<br/>'), body_style))
            story.append(Spacer(1, 6))
    
    # Add skills
    if sections['skills']:
        story.append(Paragraph('<b>SKILLS</b>', heading_style))
        skills_text = ' • '.join([s.strip('•-').strip() for s in sections['skills'] if s.strip()])
        story.append(Paragraph(skills_text, body_style))
    
    # Add projects
    if sections['projects']:
        story.append(Paragraph('<b>PROJECTS</b>', heading_style))
        for proj in sections['projects']:
            story.append(Paragraph(proj.replace('\n', '<br/>'), body_style))
            story.append(Spacer(1, 6))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Streamlit App
st.set_page_config(page_title="ATS Resume Generator", page_icon="📄")

st.title("📄 ATS-Friendly Resume Generator")
st.markdown("Paste your resume text below and generate a clean, ATS-friendly PDF")

# Text input
resume_text = st.text_area(
    "Enter your resume content:",
    height=400,
    placeholder="""Example format:

John Doe
Email: john@example.com | Phone: (123) 456-7890 | LinkedIn: linkedin.com/in/johndoe

Professional Summary
Experienced software engineer with 5+ years in full-stack development...

Work Experience
Senior Software Engineer | Tech Company | 2020 - Present
• Led development of microservices architecture
• Improved system performance by 40%

Education
Bachelor of Science in Computer Science | University Name | 2018
GPA: 3.8/4.0

Skills
Python, JavaScript, React, Node.js, AWS, Docker, SQL

Projects
E-commerce Platform
Built a scalable platform serving 10k+ users using React and Node.js"""
)

# Generate button
if st.button("Generate ATS Resume PDF", type="primary"):
    if resume_text.strip():
        with st.spinner("Generating your resume..."):
            # Parse the text
            sections = parse_resume_text(resume_text)
            
            # Generate PDF
            pdf_buffer = create_resume_pdf(sections)
            
            # Download button
            st.success("✅ Resume generated successfully!")
            st.download_button(
                label="📥 Download Resume PDF",
                data=pdf_buffer,
                file_name="ATS_Resume.pdf",
                mime="application/pdf"
            )
    else:
        st.error("Please enter your resume content first!")

# Tips section
with st.expander("💡 Tips for ATS-Friendly Resumes"):
    st.markdown("""
    - **Use clear section headers**: Summary, Experience, Education, Skills, Projects
    - **Include keywords** from the job description
    - **Use standard fonts** (the PDF uses Helvetica)
    - **Avoid tables, images, and graphics** in the original text
    - **Use bullet points** for achievements (•)
    - **Include contact information** at the top
    - **Quantify achievements** with numbers and percentages
    - **Keep formatting simple** - ATS systems prefer clean, structured text
    """)
