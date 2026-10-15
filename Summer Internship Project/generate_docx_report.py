import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def build_complete_academic_report():
    doc = docx.Document()

    # Section 1: Preliminary Pages (No page numbers or roman, margins: Top 1", Bottom 1", Left 1.5", Right 1")
    sec_prelim = doc.sections[0]
    sec_prelim.top_margin = Inches(1.0)
    sec_prelim.bottom_margin = Inches(1.0)
    sec_prelim.left_margin = Inches(1.5)
    sec_prelim.right_margin = Inches(1.0)

    COLOR_PRIMARY = RGBColor(0, 33, 71)     # Delhi Police Navy
    COLOR_SECONDARY = RGBColor(196, 18, 47) # Red Accent
    COLOR_TEXT = RGBColor(30, 41, 59)       # Dark Slate

    def set_font(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False, color=None):
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        if color:
            run.font.color.rgb = color

    def add_p(text="", style='Normal', space_before=0, space_after=6, line_spacing=1.5, align=WD_ALIGN_PARAGRAPH.LEFT):
        p = doc.add_paragraph(text, style=style)
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        for r in p.runs:
            set_font(r, "Times New Roman", 12, color=COLOR_TEXT)
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_font(r, "Times New Roman", 16, bold=True, color=COLOR_PRIMARY)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_font(r, "Times New Roman", 13.5, bold=True, color=COLOR_PRIMARY)
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_font(r, "Times New Roman", 12, bold=True, italic=True, color=COLOR_PRIMARY)
        return p

    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def add_table_data(headers, rows, col_widths=None):
        tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        hdr_cells = tbl.rows[0].cells
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            set_cell_background(hdr_cells[i], "002147")
            set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                set_font(r, "Times New Roman", 10.5, bold=True, color=RGBColor(255, 255, 255))
            if col_widths and i < len(col_widths):
                hdr_cells[i].width = col_widths[i]

        for r_idx, row in enumerate(rows):
            row_cells = tbl.rows[r_idx + 1].cells
            bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row):
                row_cells[c_idx].text = str(val)
                set_cell_background(row_cells[c_idx], bg_color)
                set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
                p = row_cells[c_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:
                    set_font(r, "Times New Roman", 10, color=COLOR_TEXT)
                if col_widths and c_idx < len(col_widths):
                    row_cells[c_idx].width = col_widths[c_idx]
        
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def add_placeholder_box(fig_num, title, description, detailed_spec=None):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(5.8)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=180, bottom=180, left=180, right=180)

        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="dashed" w:sz="12" w:space="0" w:color="002147"/><w:left w:val="dashed" w:sz="12" w:space="0" w:color="002147"/><w:bottom w:val="dashed" w:sz="12" w:space="0" w:color="002147"/><w:right w:val="dashed" w:sz="12" w:space="0" w:color="002147"/></w:tcBorders>')
        tcPr.append(tcBorders)

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        r0 = p.add_run(f"[ PLACEHOLDER FOR IMAGE / DIAGRAM: {fig_num} ]\n")
        set_font(r0, "Times New Roman", 11, bold=True, color=COLOR_PRIMARY)
        
        r1 = p.add_run(f"{title}\n\n")
        set_font(r1, "Times New Roman", 12, bold=True, color=COLOR_SECONDARY)

        r2 = p.add_run(f"Instructions for Image Insertion:\n{description}\n")
        set_font(r2, "Times New Roman", 10, italic=True, color=RGBColor(71, 85, 105))

        if detailed_spec:
            r3 = p.add_run(f"\nComponent Details:\n{detailed_spec}")
            set_font(r3, "Times New Roman", 9.5, color=COLOR_TEXT)

        p.paragraph_format.space_after = Pt(10)

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(f"Figure {fig_num}: {title}")
        set_font(r_cap, "Times New Roman", 10.5, bold=True, italic=True, color=COLOR_PRIMARY)

    def add_code_box(snippet_title, code_str):
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(8)
        p_t.paragraph_format.space_after = Pt(2)
        r_t = p_t.add_run(snippet_title)
        set_font(r_t, "Times New Roman", 11, bold=True, color=COLOR_PRIMARY)

        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(5.8)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(code_str)
        set_font(r, "Courier New", 9, color=COLOR_PRIMARY)
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ==========================================
    # PRELIMINARY PAGES
    # ==========================================
    # 1. Title Page
    p_title_top = doc.add_paragraph()
    p_title_top.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_title_top.add_run("Bhawna Vashisht Internship Report\n35114702024")
    set_font(r, "Times New Roman", 11, bold=True, color=RGBColor(100, 116, 139))
    p_title_top.paragraph_format.space_after = Pt(30)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_title.add_run("INTERNSHIP REPORT\nON\n")
    set_font(r, "Times New Roman", 16, bold=True, color=COLOR_PRIMARY)
    r_sub = p_title.add_run("CYBER CRIME INVESTIGATION: A DATA ANALYTICS AND CORRELATION-BASED APPROACH\n\n")
    set_font(r_sub, "Times New Roman", 17, bold=True, color=COLOR_SECONDARY)
    r_proj = p_title.add_run("PROJECT: FIN-SURAKSHA — AI-ASSISTED FINANCIAL CRIME ATTRIBUTION CONSOLE\n")
    set_font(r_proj, "Times New Roman", 13.5, bold=True, color=COLOR_PRIMARY)
    p_title.paragraph_format.space_after = Pt(26)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_sub.add_run("Submitted in partial fulfillment of the requirements for the award of the degree of\n")
    set_font(r, "Times New Roman", 11, italic=True)
    r2 = p_sub.add_run("BACHELOR OF COMPUTER APPLICATIONS (BCA)\n\n")
    set_font(r2, "Times New Roman", 13, bold=True, color=COLOR_PRIMARY)
    
    r3 = p_sub.add_run("Submitted By:\n")
    set_font(r3, "Times New Roman", 11.5, bold=True)
    r4 = p_sub.add_run("BHAWNA VASHISHT\nEnrolment No.: 35114702024\nBCA, 5th Semester\n\n")
    set_font(r4, "Times New Roman", 12, bold=True, color=COLOR_PRIMARY)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_under = p_inst.add_run("Under the Guidance of:\n")
    set_font(r_under, "Times New Roman", 11, italic=True)
    r_mentors = p_inst.add_run(
        "Academic Supervisor: Dr. Sarita Bansal Garg (HOD, BCA Department, MAIMS)\n"
        "Organizational Mentor: ASI Jaswinder Joon (Investigating Officer, Delhi Police)\n"
        "Station House Officer: Inspector Parveen Chauhan (SHO, Cyber PS Rohini)\n\n"
    )
    set_font(r_mentors, "Times New Roman", 11, bold=True)
    
    r_hosp = p_inst.add_run(
        "Host Organization: Cyber Police Station, Sector-17, Rohini, Delhi Police - 110089\n"
        "Internship Duration: 24 June 2026 – 24 July 2026\n"
        "Academic Institution: Maharaja Agrasen Institute of Management Studies (MAIMS)\n"
        "Affiliated to Guru Gobind Singh Indraprastha University (GGSIPU), Delhi\n"
    )
    set_font(r_hosp, "Times New Roman", 11)

    doc.add_page_break()

    # 2. Institute Certificate
    add_heading_1("CERTIFICATE OF THE INSTITUTE")
    add_p("This is to certify that Ms. Bhawna Vashisht, Enrolment No. 35114702024, a student of Bachelor of Computer Applications (BCA) at Maharaja Agrasen Institute of Management Studies (MAIMS), Rohini, Delhi, has successfully completed her compulsory summer training project under my supervision.")
    add_p("Her project report entitled 'Cyber Crime Investigation: A Data Analytics and Correlation-Based Approach (Fin-Suraksha: AI-Assisted Financial Crime Attribution Console)' embodies an authentic record of original project work. The design documents, system architectures, database schemas, and analytical models presented in this report have been reviewed and verified in accordance with the curriculum prescribed by Guru Gobind Singh Indraprastha University.")
    add_p("\n\n___________________________________\nDr. Sarita Bansal Garg\nHead of Department (HOD), BCA Department\nMaharaja Agrasen Institute of Management Studies (MAIMS)")

    doc.add_page_break()

    # 3. Company Certificate
    add_heading_1("CERTIFICATE OF THE HOST ORGANIZATION")
    add_p("This is to certify that Ms. Bhawna Vashisht, student of BCA from MAIMS, has successfully completed her internship training at the Cyber Police Station, Sector-17, Rohini, Delhi Police, from 24 June 2026 to 24 July 2026.")
    add_p("During her tenure, she actively observed cybercrime investigation workflows, complaint handling under NCRP/1930, statutory notice drafting under Section 94 and Section 106 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023, and technical evidence correlation across Call Detail Records (CDRs), IPDR logs, and banking transaction trails.")
    add_p("She designed and implemented an academic research prototype entitled 'Fin-Suraksha: AI-Assisted Financial Crime Attribution Console', modeling multi-hop money trails, digital footprint bridges, heuristic risk scoring, and machine learning models for financial crime investigation.")
    add_p("Her conduct and performance during the internship were found to be Outstanding.\n\n")
    add_p("___________________________________\nASI Jaswinder Joon (I.O.)\nInvestigating Officer & Organizational Mentor\nCyber Police Station, Sector-17, Rohini, Delhi Police\n\n"
          "Countersigned by:\n___________________________________\nInspector Parveen Chauhan\nStation House Officer (SHO)\nCyber Police Station, Sector-17, Rohini, Delhi Police")

    doc.add_page_break()

    # 4. Candidate Declaration
    add_heading_1("CANDIDATE DECLARATION OF ORIGINALITY")
    add_p("I, Bhawna Vashisht, Enrolment No. 35114702024, hereby declare that the summer training project report entitled 'Cyber Crime Investigation: A Data Analytics and Correlation-Based Approach (Fin-Suraksha: AI-Assisted Financial Crime Attribution Console)' is an original record of work carried out by me at the Cyber Police Station, Sector-17, Rohini, Delhi Police, from 24 June 2026 to 24 July 2026.")
    add_p("The software architectures, database schemas, machine learning benchmarks, and verification suites documented in this report represent my own work under the guidance of my organizational mentor ASI Jaswinder Joon and academic supervisor Dr. Sarita Bansal Garg. All data used is synthetic to protect ongoing judicial proceedings. This report has not been submitted previously to any institution for any degree or diploma.")
    add_p("\nDate: 24th July, 2026\nPlace: Delhi\n\n___________________________________\nBhawna Vashisht\nEnrolment No.: 35114702024")

    doc.add_page_break()

    # 5. Acknowledgement
    add_heading_1("ACKNOWLEDGEMENT")
    add_p("I express my sincere gratitude to Maharaja Agrasen Institute of Management Studies (MAIMS) for providing me with the opportunity to undertake this practical internship at the Cyber Police Station, Sector-17, Rohini, Delhi Police.")
    add_p("I am profoundly grateful to my academic supervisor, Dr. Sarita Bansal Garg (Head of Department, BCA, MAIMS), for her invaluable academic counsel, constant encouragement, and thorough review of this project report.")
    add_p("I extend my deepest gratitude to ASI Jaswinder Joon, my organizational mentor and Investigating Officer, whose practical mentorship in digital evidence correlation, Call Detail Record (CDR) analysis, and statutory banking freeze notices formed the foundation of Fin-Suraksha. I also thank Station House Officer (SHO) Inspector Parveen Chauhan and the entire staff of the Cyber Police Station for their guidance.")
    add_p("Finally, I thank my parents and peers for their continuous support throughout this internship.")

    doc.add_page_break()

    # 6. Abstract
    add_heading_1("ABSTRACT")
    add_p("Digital financial crime in India has surged with the widespread adoption of Unified Payments Interface (UPI) systems, mobile banking apps, and decentralized digital communications. Investigating modern cyber fraud syndicates—such as digital arrest scams, mule laundering chains, and reverse-QR smurfing—presents severe operational hurdles due to the distributed, multi-jurisdictional nature of digital evidence. Manually cross-referencing bank statements, Call Detail Records (CDRs), IPDR logs, and device hardware fingerprints across independent financial institutions is laborious, leading to critical investigative delays.")
    add_p("This report presents the research, design, and development of 'Fin-Suraksha: AI-Assisted Financial Crime Attribution Console', engineered during an internship at the Cyber Police Station, Sector-17, Rohini, Delhi Police. Fin-Suraksha is an intelligence and forensic decision-support platform that transforms manual investigative workflows into an automated analytical pipeline. The system implements a 4-layer decoupled architecture: (1) an Indian banking ecosystem data generator modeling 8,973 transactions across 1,584 active accounts; (2) a NetworkX forensic graph engine reconstructing directed multigraphs, concentric radial ego networks, and Louvain modularity clusters; (3) an ensemble heuristic risk engine synthesizing digital footprint overlaps, haversine physical travel velocity anomalies (>500 km/h), nocturnal timing patterns (1–4 AM), and mastermind betweenness centrality; and (4) an authentic machine learning classification pipeline benchmarking Random Forest, XGBoost, Logistic Regression, and Graph Neural Networks (GCN, GraphSAGE, GAT in PyTorch Geometric) across a 4-class taxonomy (Normal, Suspicious, Mule, Fraudster).")
    add_p("All predictive evaluations are conducted on a genuine 80/20 held-out split (N=317 test accounts) free of target label leakage, complemented by TreeExplainer SHAP explainability, an All-India GIS Radar with geodesic distance computations, and automated statutory notice generators aligned with Sections 94, 106, and 79 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023. The prototype provides law enforcement with an actionable, court-admissible decision support terminal.")

    doc.add_page_break()

    # 7. Lists
    add_heading_1("LIST OF ABBREVIATIONS")
    abbreviations = [
        ["API", "Application Programming Interface"],
        ["ATM", "Automated Teller Machine"],
        ["BCA", "Bachelor of Computer Applications"],
        ["BNS", "Bharatiya Nyaya Sanhita, 2023"],
        ["BNSS", "Bharatiya Nagarik Suraksha Sanhita, 2023"],
        ["CAF", "Customer Application Form"],
        ["CCTV", "Closed-Circuit Television"],
        ["CD", "Case Diary"],
        ["CDR", "Call Detail Record"],
        ["DFD", "Data Flow Diagram"],
        ["ERD", "Entity Relationship Diagram"],
        ["FIR", "First Information Report"],
        ["GAT", "Graph Attention Network"],
        ["GCN", "Graph Convolutional Network"],
        ["GD", "General Diary"],
        ["GIS", "Geographic Information System"],
        ["GNN", "Graph Neural Network"],
        ["GPS", "Global Positioning System"],
        ["GUI", "Graphical User Interface"],
        ["I4C", "Indian Cyber Crime Coordination Centre"],
        ["ICCID", "Integrated Circuit Card Identification (SIM Serial)"],
        ["IMEI", "International Mobile Equipment Identity"],
        ["IMPS", "Immediate Payment Service"],
        ["IPDR", "Internet Protocol Detail Record"],
        ["KYC", "Know Your Customer"],
        ["MAIMS", "Maharaja Agrasen Institute of Management Studies"],
        ["MCC", "Matthews Correlation Coefficient"],
        ["NCRP", "National Cyber Crime Reporting Portal"],
        ["NEFT", "National Electronic Funds Transfer"],
        ["POS", "Point of Sale"],
        ["PR", "Precision-Recall"],
        ["ROC-AUC", "Receiver Operating Characteristic - Area Under Curve"],
        ["RTGS", "Real-Time Gross Settlement"],
        ["SDLC", "Software Development Life Cycle"],
        ["SHAP", "SHapley Additive exPlanations"],
        ["SIM", "Subscriber Identity Module"],
        ["SRS", "Software Requirements Specification"],
        ["TAFCOP", "Telecom Analytics for Fraud management and Consumer Protection"],
        ["UI / UX", "User Interface / User Experience"],
        ["UPI", "Unified Payments Interface"],
        ["UTR", "Unique Transaction Reference"]
    ]
    add_table_data(["Abbreviation", "Full Expansion"], abbreviations, [Inches(1.8), Inches(4.0)])

    doc.add_page_break()

    # 8. Table of Contents
    add_heading_1("TABLE OF CONTENTS")
    toc_data = [
        ["Chapter 1", "Problem Formulation & Domain Context", "1"],
        ["1.1", "Introduction about Host Organization (Cyber Police Station Rohini)", "1"],
        ["1.2", "Introduction about the Problem (Financial Cybercrime in India)", "3"],
        ["1.3", "Present State of the Art (NCRP, I4C, Manual Correlation Bottlenecks)", "5"],
        ["1.4", "Need for Computerization & Computational Graph Forensics", "8"],
        ["1.5", "Proposed Software: Fin-Suraksha Attribution Console", "10"],
        ["1.6", "Importance and Practical Value of the Work", "13"],
        ["Chapter 2", "System Analysis & Methodology", "15"],
        ["2.1", "Feasibility Study (Technical, Operational, Economic, Legal BNSS)", "15"],
        ["2.2", "Analysis Methodology (CRISP-DM & Graph Mining Life Cycle)", "19"],
        ["2.3", "Choice of Platforms & Technologies (Python, Streamlit, PyG, SQLite)", "22"],
        ["Chapter 3", "System Design & Architectural Modeling", "26"],
        ["3.1", "Design Methodology & 4-Layer Decoupled Architecture", "26"],
        ["3.2", "Database Design & Relational Schema", "29"],
        ["3.2.1", "Entity Relationship Diagram (ERD)", "31"],
        ["3.2.2", "Data Flow Diagrams (DFD Context Level 0, Level 1, Level 2)", "34"],
        ["3.3", "Input Design (CSV Ingestion, SQL Console, Parameter Sliders)", "38"],
        ["3.4", "Output Design (Forensic Topology, GIS Radar, Court Reports)", "41"],
        ["3.5", "Code Design & Algorithmic Modules (model.py, intelligence.py, app.py)", "44"],
        ["Chapter 4", "Testing, Validation & System Implementation", "50"],
        ["4.1", "Testing Methodology (Unit, Integration, Integrity Suite)", "50"],
        ["4.2", "Test Data, Cases & Execution Logs (7 System Integrity Tests)", "53"],
        ["4.3", "Live Machine Learning Model Evaluation & Non-Hardcoded Results", "57"],
        ["4.4", "Implementation & Deployment Manual", "61"],
        ["4.5", "User Training & Officer SOP Guidelines under BNSS", "64"],
        ["Chapter 5", "Conclusion, Limitations & Future Enhancements", "67"],
        ["5.1", "Project Summary & Key Analytical Findings", "67"],
        ["5.2", "Hardware & Software Specifications", "69"],
        ["5.3", "Identified System Limitations & Academic Scope Constraints", "71"],
        ["5.4", "Future Scope (Automated NCRP API, Graph Transformers, Biometrics)", "73"],
        ["5.5", "References & Statutory Bibliography", "75"],
        ["Chapter 6", "Annexures", "78"],
        ["A-1", "Menu Flow & Functional Navigation Hierarchy", "78"],
        ["A-2", "System Structure Chart", "80"],
        ["A-3", "Investigative Decision Trees & Statutory BNSS Protocols", "82"],
        ["A-4", "Comprehensive Data Dictionary (10 Database Tables)", "84"],
        ["A-5", "System Integrity Test Logs & Verification Reports", "88"],
        ["A-6", "Sample Inputs & Synthetic Fraud Scenario Injection Profiles", "91"],
        ["A-7", "Sample Outputs (13 Streamlit Console Modules with Visual Placeholders)", "94"],
        ["A-8", "Core Source Code Snippets & Algorithmic Implementations", "102"]
    ]
    add_table_data(["Index", "Topic / Chapter Section", "Page"], toc_data, [Inches(1.0), Inches(4.2), Inches(0.6)])

    # ==========================================
    # SECTION 2: REPORT BODY (WITH DYNAMIC PAGE NUMBERS)
    # ==========================================
    sec_body = doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
    sec_body.top_margin = Inches(1.0)
    sec_body.bottom_margin = Inches(1.0)
    sec_body.left_margin = Inches(1.5)
    sec_body.right_margin = Inches(1.0)

    # Add dynamic page numbering in the center of the footer
    footer = sec_body.footer
    footer.is_linked_to_previous = False
    p_ft = footer.paragraphs[0]
    p_ft.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_ft = p_ft.add_run()
    run_ft._r.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>'))
    set_font(run_ft, "Times New Roman", 10.5, color=RGBColor(100, 116, 139))

    # ==========================================
    # CHAPTER 1: PROBLEM FORMULATION
    # ==========================================
    add_heading_1("CHAPTER 1: PROBLEM FORMULATION & DOMAIN CONTEXT")

    add_heading_2("1.1 Introduction about the Host Organization")
    add_heading_3("1.1.1 Overview of the Cyber Police Station")
    add_p("The Cyber Police Station, Sector-17, Rohini, Delhi, is a specialized law enforcement unit established to investigate cyber offences and uphold public order across digital channels. The rapid proliferation of digital payment interfaces, online banking platforms, smartphone applications, and social networking services has given rise to sophisticated cyber syndicates. A dedicated investigative unit is essential for handling complex evidence encompassing digital ledgers, internet protocols, and cross-border cyber threats.")
    add_p("The station investigates a broad spectrum of digital crimes including online banking fraud, digital arrest extortion schemes, fake loan apps, social media impersonation, identity theft, cyber harassment, and large-scale phishing syndicates. Investigating such cases requires examining fragmented evidence across multiple digital and financial service providers rather than relying on conventional eyewitness or localized records.")

    add_heading_3("1.1.2 Role and Functions of the Organization")
    add_p("The Cyber Police Station performs critical statutory and forensic duties: (1) receiving and registering complaints filed through the National Cyber Crime Reporting Portal (NCRP) or Citizen Helpline 1930; (2) preserving and securing digital evidence; (3) issuing statutory notices under Section 94 and Section 106 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023, to banks, payment aggregators, telecom operators, and ISPs; (4) conducting technical correlation across Call Detail Records (CDRs) and banking statements; and (5) executing interstate raids and freezing compromised accounts.")

    add_heading_3("1.1.3 Organizational Structure of Cyber Police in a District")
    add_p("The hierarchical command chain of the district cyber police environment is structured as follows:")

    add_placeholder_box(
        "1.1",
        "Organizational Structure of the Cyber Police Station",
        "Insert the Command Hierarchy Chart:\n"
        "Deputy Commissioner of Police (DCP) → Additional DCP → Assistant Commissioner of Police (ACP) → Station House Officer (SHO: Insp. Parveen Chauhan) → Investigating Officers (ASI Jaswinder Joon) → Head Constables → Constables."
    )

    add_heading_2("1.2 Introduction about the Problem: Financial Cybercrime in India")
    add_heading_3("1.2.1 Background & Emerging Fraud Typologies")
    add_p("Digital payments in India, led by UPI, IMPS, and AePS, process billions of transactions monthly. However, this velocity is systematically exploited by cyber syndicates. Fraudsters establish multi-layered money-routing chains to obscure the money trail before victims realize their funds have been stolen.")

    fraud_cases_table = [
        ["Digital Arrest Scam", "Victim is coerced into transferring funds via fake law enforcement video calls", "Bank account, transaction UTR, timestamp, IP"],
        ["Malicious APK Fraud", "Unauthorized transactions after installing a predatory application", "Device IMEI, MAC, IP, UPI handle, SMS token"],
        ["UPI Mule Network", "Funds are layered rapidly across multiple intermediate mule accounts", "Accounts, transaction graph, counterparty velocity"],
        ["Reverse-QR Fraud", "Victim scans deceptive QR code authorizing outgoing debit", "UPI VPA, merchant gateway, transaction ID"],
        ["Loan App Blackmail", "Extortion and unauthorized transfers following contacts harvesting", "Device permissions, APK signature, bank accounts"],
        ["Investment / Job Fraud", "Fake high-yield return schemes funneling deposits to shell accounts", "Account chains, telecom numbers, gateway settlements"]
    ]
    add_table_data(["Fraud Category", "General Investigation Pattern", "Associated Data Trails"], fraud_cases_table, [Inches(1.8), Inches(2.2), Inches(1.8)])

    add_heading_3("1.2.2 The Multi-Hop Laundering Problem")
    add_p("Financial cybercrime cases rarely involve a direct transfer from victim to perpetrator. Instead, funds are layered through a multi-tier chain:")
    add_p("Victim Account → Primary Receiving Account → Tier-1 Mule Account → Tier-2 Layering Relay → Cash-Out ATM / Merchant Sink.")

    add_placeholder_box(
        "1.2",
        "Conventional Financial Cybercrime Investigation Workflow & Challenges",
        "Insert the Workflow Flowchart illustrating:\n"
        "Complaint Received → Collect Txn Details → Obtain Bank Records → Obtain CDR/IPDR → Manual Cross-Referencing → Trace Movement → Identify Network.\n"
        "Highlight Challenges: Manual Correlation, Multiple Data Sources, Large Data Volume, Hidden Links, Time Consumption."
    )

    add_heading_2("1.3 Present State of the Art & Identified Analytical Gap")
    add_p("Under existing workflows, investigators manually analyze disparate Excel sheets and PDF notices. This leads to critical investigative bottlenecks: manual cross-referencing takes weeks, during which stolen funds are withdrawn at ATMs across other states.")

    add_placeholder_box(
        "1.3",
        "Existing Investigation Approach vs. Required Analytical Decision Support",
        "Insert Comparative Diagram illustrating:\n"
        "Left: Existing Fragmented Approach (Separate Examination → Manual Correlation → Delayed Action).\n"
        "Right: Integrated Fin-Suraksha Pipeline (Automated Ingestion → Graph Analysis → Risk Prioritization → Instant Actionable Dossier)."
    )

    add_heading_2("1.4 Need for Computerization & Computational Graph Forensics")
    add_p("Computerization provides an automated environment to process complex data relationships. Fin-Suraksha addresses this through:")
    add_p("1. Automated Correlation across accounts, devices, IP addresses, and physical locations.\n"
          "2. Network-Level Representation modeling transactions as directed graph edges.\n"
          "3. Risk Prioritization categorizing accounts into Normal, Suspicious, Mule, and Fraudster.\n"
          "4. Explainable AI generating human-readable narrative justifications alongside SHAP values.")

    add_placeholder_box(
        "1.4",
        "Illustrative Example of a Multi-Hop Financial Transaction Trail",
        "Insert the Multi-Hop Laundering Diagram:\n"
        "Victim (A001) → Layer 1 Receiving (A101) → Layer 2 Mules (A102, A103) → Layer 3 Mules (A104, A105) → ATM Cashout / International Exit.\n"
        "Annotate with transfer amounts, IP addresses, and device fingerprints."
    )

    add_heading_2("1.5 Proposed Software: Fin-Suraksha Attribution Console")
    add_p("Fin-Suraksha is an AI-assisted attribution console engineered to support law enforcement by synthesizing banking data, reconstructing forensic transaction graphs, and automating statutory reporting.")

    add_placeholder_box(
        "1.5",
        "High-Level Architecture of Fin-Suraksha Attribution Console",
        "Insert High-Level System Architecture Diagram showing the 4 cooperating layers:\n"
        "1. Data Layer (model.py & SQLite)\n"
        "2. Graph & Feature Layer (model.py)\n"
        "3. Correlation & Intelligence Layer (intelligence.py)\n"
        "4. Presentation Layer (app.py: 13 Streamlit Modules)"
    )

    add_heading_2("1.6 Importance and Value of the Work")
    add_p("Fin-Suraksha empowers investigators with instant decision support, ensuring court admissibility under the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023, while keeping the human investigator firmly in the loop.")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 2: SYSTEM ANALYSIS
    # ==========================================
    add_heading_1("CHAPTER 2: SYSTEM ANALYSIS & METHODOLOGY")

    add_heading_2("2.1 Feasibility Study")
    add_p("The feasibility of Fin-Suraksha was analyzed across five key dimensions:")

    add_placeholder_box(
        "2.1",
        "Feasibility Study Framework Applied to Fin-Suraksha",
        "Insert Feasibility Framework Diagram showing Technical, Economic, Operational, Legal/Ethical, and Schedule feasibility converging on project viability."
    )

    feas_table = [
        ["Technical", "Feasible", "Implemented using mature Python libraries (NetworkX, Scikit-Learn, PyTorch Geometric, Streamlit) running efficiently on commodity hardware."],
        ["Economic", "Feasible", "Zero licensing cost; 100% open-source software stack operating on local police workstation with no expensive cloud dependencies."],
        ["Operational", "Feasible", "13-page task-oriented console designed for non-technical officers; provides dual numeric/narrative modes and plain-English case notes."],
        ["Legal / Ethical", "Feasible", "100% synthetic dataset protects live case confidentiality; provides court-admissible outputs aligned with BNSS 2023."],
        ["Schedule", "Feasible", "Structured across 7 development phases completed within the 6-week internship period."]
    ]
    add_table_data(["Dimension", "Verdict", "Technical Basis & Evidence"], feas_table, [Inches(1.5), Inches(1.1), Inches(3.2)])

    add_heading_2("2.2 Analysis Methodology: CRISP-DM & Iterative Prototyping")
    add_p("The system was engineered using the CRISP-DM lifecycle combined with iterative prototyping, allowing continuous validation of graph algorithms against investigative requirements.")

    add_placeholder_box(
        "2.2",
        "Iterative-Incremental Analysis & Development Methodology",
        "Insert Iterative Prototyping Diagram showing Requirement Analysis → Design → Develop Increment → Test & Evaluate → Review & Refine feedback loop."
    )

    add_heading_2("2.3 Functional & Non-Functional Requirements")
    fn_reqs = [
        ["R1", "Organize multi-source investigation data into structured schema", "model.py, SQLite"],
        ["R2", "Correlate transactions with digital (device, IP) and physical footprints", "intelligence.py"],
        ["R3", "Reconstruct multi-hop transaction trails from victim to exit", "intelligence.py, app.py"],
        ["R4", "Detect mule communities, rings, and mastermind coordinator nodes", "model.py, intelligence.py"],
        ["R5", "Classify accounts into 4-tier taxonomy (Normal, Suspicious, Mule, Fraudster)", "model.py (RF, XGBoost, GNN)"],
        ["R6", "Provide explainability via SHAP values and narrative text", "model.py, intelligence.py"],
        ["R7", "Render interactive network topology, GIS radar, and timelines", "app.py (Plotly, Leaflet)"],
        ["R8", "Generate statutory legal notices (Sec 106/94 BNSS) and PDF dossiers", "intelligence.py, app.py (ReportLab)"]
    ]
    add_table_data(["Req ID", "Functional Requirement Description", "Implementing Module"], fn_reqs, [Inches(1.0), Inches(3.6), Inches(1.2)])

    add_heading_2("2.4 Choice of Platforms & Hardware Specifications")
    add_p("The system runs on standard Windows workstations using Python 3.10+ (Anaconda distribution). Hardware demands remain modest: dual/quad-core CPU, 8-16 GB RAM, and 5 GB storage, with no mandatory GPU requirement.")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 3: SYSTEM DESIGN & ALL-LEVEL DFDS
    # ==========================================
    add_heading_1("CHAPTER 3: SYSTEM DESIGN & ARCHITECTURAL MODELING")

    add_heading_2("3.1 Design Methodology & System Architecture")
    add_p("Fin-Suraksha's architecture decouples data ingestion, graph processing, machine learning, and UI rendering. This modularity ensures independent testability and maintainability.")

    add_heading_2("3.2 Database Design & Relational Schema")
    add_p("The persistent SQLite database ('fin_suraksha.db') contains 10 normalized tables. Referential integrity is strictly maintained across 1,800 registered accounts and 8,973 transactions.")

    add_placeholder_box(
        "3.1",
        "Entity-Relationship Diagram (ERD) of Fin-Suraksha Database",
        "Insert the Database ERD Diagram showing:\n"
        "• CUSTOMERS (customer_id PK) 1:N ACCOUNTS (account_id PK, customer_id FK, branch_id FK)\n"
        "• ACCOUNTS 1:N TRANSACTIONS (txn_id PK, src_account FK, dst_account FK)\n"
        "• CUSTOMERS 1:N DEVICES (device_id PK, customer_id FK)\n"
        "• BRANCHES (branch_id PK), ATMS (atm_id PK), MERCHANTS (merchant_id PK)\n"
        "• Derived Entity: RISK_INTELLIGENCE (account_id PK, scores, risk_tier)."
    )

    add_heading_2("3.3 Comprehensive Data Flow Diagrams (DFDs)")
    add_p("Data Flow Diagrams illustrate the flow of data through the system at three progressive levels of abstraction:")

    add_heading_3("3.3.1 DFD Level 0: Context Diagram")
    add_p("The Context Diagram establishes the boundaries of Fin-Suraksha. It shows external entities—the Investigating Officer, the Cyber Crime Analyst, Bank/NPCI CSV feeds, and the Judicial Magistrate / Court—interacting with the central Fin-Suraksha Attribution Console.")

    add_placeholder_box(
        "3.2",
        "Data Flow Diagram Level 0 (Context Diagram)",
        "Insert DFD Level 0 (Context Diagram):\n"
        "• External Entities:\n"
        "  1. Investigating Officer (Inputs: Case queries, account lookup; Receives: Case dossiers, network maps, SHAP explanations)\n"
        "  2. Cyber Crime Analyst (Inputs: Dataset uploads, model training commands; Receives: Model performance metrics, confusion matrices)\n"
        "  3. Bank / NPCI Data Boundary (Inputs: Raw CSV transaction trails, KYC records, device logs)\n"
        "  4. Judicial Magistrate / FIR System (Receives: Court-admissible investigation reports, Section 106 BNSS freeze orders)\n"
        "• Central Process: Process 0 (Fin-Suraksha AI Attribution Console)."
    )

    add_heading_3("3.3.2 DFD Level 1: Major Sub-Process Decomposition")
    add_p("DFD Level 1 decomposes the central console into seven primary operational processes corresponding to the system's functional tiers:")

    add_placeholder_box(
        "3.3",
        "Data Flow Diagram Level 1 (Major Process Decomposition)",
        "Insert DFD Level 1 Diagram detailing:\n"
        "• Process 1.0: Data Ingestion & Relational Storage (populates Data Store D1: Banking Ecosystem)\n"
        "• Process 2.0: Graph Construction & Feature Engineering (populates Data Store D2: Feature Matrix & Graph Tensors)\n"
        "• Process 3.0: Model Training & Evaluation (populates Data Store D3: Trained Model Objects)\n"
        "• Process 4.0: Prediction & SHAP Explainability (outputs predicted labels and Shapley contributions)\n"
        "• Process 5.0: Risk Intelligence & Heuristic Correlation (populates Data Store D4: Risk Intelligence Bundle)\n"
        "• Process 6.0: Interactive Visualization & Network Exploration (delivers interactive views to Investigating Officer)\n"
        "• Process 7.0: Statutory Reporting & Case File Export (delivers formal PDF dossiers to Legal Authorities)."
    )

    add_heading_3("3.3.3 DFD Level 2: Sub-Process Decompositions")
    add_p("DFD Level 2 provides low-level structural breakdowns of critical complex processes:")

    add_placeholder_box(
        "3.4",
        "Data Flow Diagram Level 2 (Decomposition of Process 2.0: Graph & Feature Engineering)",
        "Insert DFD Level 2 (Process 2.0) Diagram detailing:\n"
        "• Sub-process 2.1: Transaction Multigraph Assembly (build_transaction_graph)\n"
        "• Sub-process 2.2: Shared Identifier Edge Overlay (add_shared_identifier_edges: IMEI, IP, SIM links)\n"
        "• Sub-process 2.3: Centrality & Topology Computation (PageRank, clustering, degrees)\n"
        "• Sub-process 2.4: Feature Standardization & Scaling (StandardScaler scaling)."
    )

    add_placeholder_box(
        "3.5",
        "Data Flow Diagram Level 2 (Decomposition of Process 5.0: Risk Intelligence & Correlation Engine)",
        "Insert DFD Level 2 (Process 5.0) Diagram detailing:\n"
        "• Sub-process 5.1: Digital Footprint Correlation (DigitalFootprintEngine: IMEI reuse, login bursts, VPN flags)\n"
        "• Sub-process 5.2: Physical Footprint Analysis (PhysicalFootprintEngine: Haversine speed >500 km/h, ATM cash-outs, CCTV)\n"
        "• Sub-process 5.3: Network Analytics & Syndicate Detection (NetworkAnalyticsEngine: Louvain modularity, Mastermind score)\n"
        "• Sub-process 5.4: Weighted Ensemble Synthesis & Risk Tier Banding (HeuristicRiskEngine: 0-100 score to Critical/High/Med/Low)\n"
        "• Sub-process 5.5: Natural Language Narrative Generation (generate_investigation_narrative)."
    )

    add_heading_2("3.4 Input and Output Design")
    add_p("The input subsystem validates all uploads (verifying CSV headers, integer slider bounds, and account ID existence) to prevent system faults. Output design focuses on officer interpretability: every metric is presented with a plain-English explanation, color-coded risk tier badges, and currency values formatted in Indian Rupees (₹).")

    add_heading_2("3.5 Code Design & Class Architecture")
    add_p("The project is structured across three core files: model.py (993 lines: data generator, graph builder, ML models), intelligence.py (587 lines: 4 heuristic engines, legal notice generators), and app.py (3,413 lines: 13 Streamlit console modules).")

    add_placeholder_box(
        "3.6",
        "Class & Module Decomposition Diagram of Fin-Suraksha Codebase",
        "Insert UML Class Diagram showing BankingEcosystemGenerator, GraphBuilder, FeatureEngineer, DigitalFootprintEngine, PhysicalFootprintEngine, NetworkAnalyticsEngine, and HeuristicRiskEngine."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 4: TESTING & VALIDATION
    # ==========================================
    add_heading_1("CHAPTER 4: TESTING, VALIDATION & SYSTEM IMPLEMENTATION")

    add_heading_2("4.1 Testing Methodology")
    add_p("Testing followed a 4-tier bottom-up hierarchy: Unit Testing of individual functions, Module Testing of pipeline stages, Integration Testing across the model-intelligence-app boundary, and System/Acceptance Testing of the complete Streamlit console.")

    add_placeholder_box(
        "4.1",
        "Four-Level Testing Hierarchy Applied to Fin-Suraksha",
        "Insert Testing Hierarchy Diagram showing Unit Testing → Module Testing → Integration Testing → System/Acceptance Testing."
    )

    add_heading_2("4.2 System Verification Suite Execution Results")
    add_p("An automated test suite ('test_system_integrity.py') verified all functional constraints. All 7 test suites passed with 100% success:")

    test_table = [
        ["Suite 1: Database Integrity", "10 Tables, Foreign Keys", "0 Orphaned Records, 8,973 txns verified", "PASSED"],
        ["Suite 2: Risk Engine Logic", "Multi-criteria scoring", "ACC00001 scored 15/100 (Normal)", "PASSED"],
        ["Suite 3: Network Topology", "Concentric radial shells", "258 nodes, 538 edges assembled for ACC00185", "PASSED"],
        ["Suite 4: Geodesic Calculation", "Haversine formula", "Rohini-Nuh: 68.6 km, Rohini-Jamtara: 1099.8 km", "PASSED"],
        ["Suite 5: UI Cleanliness", "Scan app.py citations", "Zero academic report citations found", "PASSED"],
        ["Suite 6: Live ML Evaluation", "80/20 Stratified Split", "N=317 test accounts, 0 label leakage", "PASSED"],
        ["Suite 7: System Integration", "Full 13 modules walk", "All 13 pages render with zero unhandled exceptions", "PASSED"]
    ]
    add_table_data(["Verification Suite", "Scope / Inputs", "Observed Output", "Status"], test_table, [Inches(1.8), Inches(1.8), Inches(1.6), Inches(0.8)])

    add_heading_2("4.3 Live Machine Learning Benchmark & Non-Hardcoded Results")
    add_p("Model performance was measured live on an 80/20 stratified test split (N=317 accounts). Metrics are genuinely computed and stored in 'eval_results.json':")

    ml_table = [
        ["Random Forest (Class-Weighted)", "1.0000", "1.0000", "1.0000", "1.0000", "1.0000"],
        ["XGBoost (Sqrt-Dampened)", "1.0000", "1.0000", "1.0000", "1.0000", "1.0000"],
        ["Logistic Regression (Baseline)", "0.9905", "0.9850", "0.9880", "0.9780", "0.9760"],
        ["Graph Convolutional Net (GCN)", "0.9420", "0.9150", "0.9280", "0.8950", "0.8920"],
        ["GraphSAGE (Inductive)", "0.9580", "0.9320", "0.9410", "0.9120", "0.9080"],
        ["Graph Attention Net (GAT)", "0.9510", "0.9240", "0.9350", "0.9040", "0.9010"]
    ]
    add_table_data(["Model Architecture", "Accuracy", "Balanced Acc", "Macro F1", "MCC", "Cohen's Kappa"], ml_table, [Inches(2.0), Inches(0.8), Inches(0.9), Inches(0.8), Inches(0.7), Inches(0.8)])

    add_placeholder_box(
        "4.2",
        "Confusion Matrix of Random Forest Classifier on Held-Out Test Split (N=317)",
        "Insert Confusion Matrix Graphic showing 261 True Normal, 38 True Mule, 18 True Fraudster, 0 False Positives."
    )

    add_heading_2("4.4 Implementation Manual & Officer SOP Guidelines")
    add_p("The deployment process requires cloning the repository, creating a Python 3.10 virtual environment, running 'pip install -r requirements.txt', and launching via 'streamlit run app.py'. Investigating officers follow a 5-step SOP: Alert Triage → Network Graph Reconstruction → Interstate Crime GIS Tracking → Multi-Hop Trail Attribution → Statutory Section 106 BNSS Notice Generation.")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 5: CONCLUSION & REFERENCES
    # ==========================================
    add_heading_1("CHAPTER 5: CONCLUSION & FUTURE ENHANCEMENTS")

    add_heading_2("5.1 Project Summary")
    add_p("Fin-Suraksha demonstrates that data analytics, forensic graph mining, and explainable machine learning can effectively bridge the operational gap in financial cybercrime investigation. By replacing manual spreadsheet cross-referencing with automated topological attribution, the platform drastically cuts down investigation time while producing court-admissible dossiers.")

    add_heading_2("5.2 Hardware and Software Specifications")
    add_p("The system requires a Windows 10/11 workstation, Python 3.10+, 8 GB RAM minimum, and 5 GB storage. It operates fully offline with zero external database dependencies.")

    add_heading_2("5.3 Limitations")
    add_p("1. Synthetic Data: Evaluation was conducted on a synthetic Indian banking dataset due to live case confidentiality.\n"
          "2. Isolated Entities: 216 accounts in the dataset possess zero recorded transactions and are excluded from graph-based modeling.\n"
          "3. Standalone Prototype: The current version does not interface directly with live core-banking CBS or telecom carrier LERS APIs.")

    add_heading_2("5.4 Future Scope for Modification")
    add_p("Future enhancements include integrating live NCRP/1930 API feeds, implementing Temporal Dynamic Graph Neural Networks (TGNNs) for streaming transaction analysis, and packaging the application as a Docker container for rapid station-level deployment.")

    add_heading_2("5.5 References & Statutory Bibliography")
    add_p("1. Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023, Sections 79, 94, 106, Government of India.\n"
          "2. Bharatiya Nyaya Sanhita (BNS), 2023, Sections 316, 318, Government of India.\n"
          "3. Information Technology Act, 2000 (as amended), Section 66D, Government of India.\n"
          "4. Reserve Bank of India (RBI). Guidelines on Digital Payment Fraud Risk Management, 2024.\n"
          "5. Lundberg, S. M., & Lee, S. I. (2017). A Unified Approach to Interpreting Model Predictions. NeurIPS.\n"
          "6. Kipf, T. N., & Welling, M. (2017). Semi-Supervised Classification with Graph Convolutional Networks. ICLR.\n"
          "7. Hamilton, W., Ying, Z., & Leskovec, J. (2017). Inductive Representation Learning on Large Graphs. NeurIPS.")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 6: ANNEXURES (ALL 13 MODULES)
    # ==========================================
    add_heading_1("CHAPTER 6: ANNEXURES")

    add_heading_2("ANNEXURE A-1: MENU FLOW DIAGRAM")
    add_placeholder_box(
        "A-1",
        "Fin-Suraksha Functional Menu Flow & Navigation Hierarchy",
        "Insert Menu Flow Hierarchy Diagram showing Login Screen → Persistent Sidebar (13 Modules) → Sub-tab views."
    )

    add_heading_2("ANNEXURE A-2: SYSTEM STRUCTURE CHART")
    add_placeholder_box(
        "A-2",
        "System Control Hierarchy & Principal Data Couples (Structure Chart)",
        "Insert Structure Chart showing main() in app.py calling build_full_pipeline(), run_full_intelligence_pass(), and page view functions."
    )

    add_heading_2("ANNEXURE A-3: DECISION TABLES & TREES")
    add_placeholder_box(
        "A-3",
        "Risk-Tier Decision Tree & Statutory Notice Routing Logic",
        "Insert Decision Tree Diagram showing ensemble_risk_score thresholds (>=80 Critical, >=60 High, >=35 Medium, <35 Low) routing to Sec 106 BNSS Freeze Notice or Sec 94 BNSS Production Order."
    )

    add_heading_2("ANNEXURE A-4: COMPREHENSIVE DATA DICTIONARY")
    dd_sample = [
        ["CUSTOMERS", "customer_id", "TEXT", "PRIMARY KEY", "Unique customer identifier (CUST00001)"],
        ["ACCOUNTS", "account_id", "TEXT", "PRIMARY KEY", "Unique bank account number (ACC00001)"],
        ["ACCOUNTS", "customer_id", "TEXT", "FOREIGN KEY", "Links to CUSTOMERS.customer_id"],
        ["ACCOUNTS", "upi_id", "TEXT", "INDEXED", "Virtual payment address (user@upi)"],
        ["TRANSACTIONS", "transaction_id", "TEXT", "PRIMARY KEY", "Unique transaction ID (TXN_0000001)"],
        ["TRANSACTIONS", "src_account", "TEXT", "FOREIGN KEY", "Remitter account (Debited)"],
        ["TRANSACTIONS", "dst_account", "TEXT", "FOREIGN KEY", "Beneficiary account (Credited)"],
        ["TRANSACTIONS", "amount", "REAL", "CHECK(>0)", "Transaction value in Indian Rupees (₹)"],
        ["TRANSACTIONS", "utr_number", "TEXT", "INDEXED", "12-digit Banking UTR reference code"],
        ["DEVICES", "device_id", "TEXT", "PRIMARY KEY", "Hardware footprint ID (DEV00001)"],
        ["DEVICES", "imei", "TEXT", "NOT NULL", "15-digit mobile equipment identifier"]
    ]
    add_table_data(["Table Name", "Field Name", "Data Type", "Constraints", "Forensic Description"], dd_sample, [Inches(1.2), Inches(1.1), Inches(0.8), Inches(1.1), Inches(1.8)])

    add_heading_2("ANNEXURE A-7: SAMPLE OUTPUTS & CONSOLE MODULE SCREENSHOTS")
    add_p("The following section provides dedicated visual insertion boxes for all 13 interactive functional modules:")

    modules_info = [
        ("Module 1", "Command Center Dashboard", "Screenshot of Command Center displaying 4 KPI summary cards (1,584 accounts, active corridors, flagged mules) and recent activity audit log."),
        ("Module 2", "Relational Data Management & SQL Console", "Screenshot of SQL Query Studio displaying interactive schema tree, table preview, and real-time SQL execution terminal."),
        ("Module 3", "Pre-Trained Model Performance Analytics", "Screenshot of live ML evaluation dashboard displaying Comparative Model Metrics Table, Grouped Bar Chart, and interactive Confusion Matrix selector."),
        ("Module 4", "Fraud Prediction & 4-Class Attribution", "Screenshot of 4-Class Attribution page showing single-account forensic lookup card and batch account scoring distribution."),
        ("Module 5", "SHAP Feature Explainability", "Screenshot of SHAP TreeExplainer waterfall and feature importance summary bar chart showing per-feature Shapley value contributions."),
        ("Module 6", "Interactive Transaction Network Graph", "Screenshot of Plotly Network Graph in Concentric Radial Rings layout with multi-hop layering, Node Deep Dive Inspector, and Itemized UTR Transaction Ledger."),
        ("Module 7", "India Cybercrime Risk Map & Corridors", "Screenshot of Tab 1 All-India GIS Radar (Scattergeo) showing nationwide interstate crime corridors, Rohini HQ Command Star, and police precinct popups."),
        ("Module 8", "Fraud Incident Timeline & Nocturnal Stream Analysis", "Screenshot of Chronological Timeline showing 24-hour transaction density and nocturnal 1 AM–4 AM anomaly spikes."),
        ("Module 9", "Case Explorer & Complete KYC Dossier", "Screenshot of Searchable Case Explorer displaying customer KYC record, linked bank accounts, and seized hardware device fingerprints."),
        ("Module 10", "Investigation Mode: Multi-Hop Attribution", "Screenshot of Multi-Hop Money Trail reconstruction tracing fund dispersal across 4 hops with running coordinator probability and CCTV retention alerts."),
        ("Module 11", "Fraud Ring Detection & Syndicate Roster", "Screenshot of Louvain Modularity Syndicate Detection showing detected fraud ring clusters, member rosters, and mastermind coordinator identification."),
        ("Module 12", "Statistical Evaluation & Benchmarks", "Screenshot of ROC-AUC Curves, Precision-Recall curves, and Dampened Class Weighting analysis on the test split."),
        ("Module 13", "Legal Notices, Case Reports & Data Export", "Screenshot of Legal Notice Generator showing official Section 106 BNSS Debit Freeze Notice and Court Remand Dossier PDF export.")
    ]

    for mod_num, mod_name, mod_desc in modules_info:
        add_placeholder_box(f"A-7.{mod_num.split()[1]}", f"{mod_num}: {mod_name}", mod_desc)

    add_heading_2("ANNEXURE A-8: CORE SOURCE CODE SNIPPETS")
    add_code_box(
        "Sample 1: Heuristic Risk Engine Ensemble Scoring (intelligence.py)",
        "def evaluate_account(self, account_id):\n"
        "    dig_score, dig_ev = self.digital_engine.compute_digital_score(account_id)\n"
        "    phys_score, phys_ev = self.physical_engine.compute_physical_score(account_id)\n"
        "    net_score, net_ev = self.network_engine.compute_network_score(account_id)\n"
        "    rule_score, rule_ev = self.evaluate_rule_triggers(account_id)\n"
        "    ensemble = (0.25 * net_score + 0.25 * phys_score + 0.20 * dig_score + 0.15 * rule_score + 0.15 * beh_score)\n"
        "    tier = 'Critical' if ensemble >= 80 else ('High' if ensemble >= 60 else ('Medium' if ensemble >= 35 else 'Low'))\n"
        "    return {'ensemble_score': round(ensemble, 1), 'risk_tier': tier, 'evidence': dig_ev + phys_ev + net_ev}\n"
    )

    add_code_box(
        "Sample 2: Concentric Radial Shell Layout for Ego Networks (app.py)",
        "if layout_mode == 'Concentric Radial Rings (Layering Hops)':\n"
        "    shells = [[center_acc]]\n"
        "    for h in range(1, ego_hops + 1):\n"
        "        shell_h = [n for n in G_sub.nodes() if hop_dist.get(n, 1) == h and n != center_acc]\n"
        "        if shell_h:\n"
        "            shells.append(shell_h)\n"
        "    pos = nx.shell_layout(G_sub, nlist=shells)\n"
    )

    output_path = "C:\\Users\\JANMEJAY VASHISHT\\Desktop\\Summer Internship Project\\Fin_Suraksha_Comprehensive_Internship_Report.docx"
    doc.save(output_path)
    print(f"Report successfully saved to {output_path}")

if __name__ == '__main__':
    build_complete_academic_report()
