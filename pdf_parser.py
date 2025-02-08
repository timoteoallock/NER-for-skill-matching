# Description: This script contains functions to parse a PDF resume and extract relevant sections of content. 
# It also includes a function to check if the education level in the resume meets the required level for a job description. 
# The `parse_pdf` function extracts text from each page of a PDF file, sanitizes it, and groups lines into sections based on known keywords. 
# The `generate_grouped_content_string` function converts the grouped content dictionary into a formatted string. 
# The `check_education_match` function extracts degree information from text using regular expressions and compares the highest degree in the resume with the required degree in the job description.
# This script can be imported into the main Streamlit app script to handle PDF parsing and education level matching functionality.

import re
import pdfplumber
from collections import defaultdict
from unidecode import unidecode

# Define your section keywords
section_keywords = {
    "Summary": ["summary", "objective", "about me", "profile"],
    "Education": ["education", "academic background", "qualifications"],
    "Skills": ["skills", "technical skills", "key skills", "leadership skills", "soft skills", "skill"],
    "Experience": ["experience", "history", "employment", "professional experience", "work experience", "experiences"],
    "Extracurricular": ["extracurricular", "activities", "volunteering", "leadership"], 
    "Projects": ["projects", "portfolio", "publications", "awards", "patents", "publications", "research", "papers"], 
    "Additional Information": ["certifications", "languages", "interests", "references"]
}

def sanitize_line(line: str) -> str:
    """
    Removes or converts unwanted characters, reduces multiple spaces,
    and strips leading/trailing whitespace.
    """
    sanitized = unidecode(line)
    sanitized = re.sub(r'https?://\S+', '', sanitized)  # Remove URLs
    sanitized = re.sub(r'[^\w\s\.,;:\-\'"()/&]', ' ', sanitized)  # Remove unwanted chars
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()  # Reduce spaces
    return sanitized

def parse_pdf(file_path: str):
    """
    Extracts text from each page using pdfplumber, sanitizes it,
    and groups lines into sections based on known keywords.
    """
    sections = defaultdict(list)
    current_section = "Uncategorized"

    try:
        with pdfplumber.open(file_path) as pdf:
            all_lines = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                all_lines.extend(text.splitlines())

            for line in all_lines:
                sanitized = sanitize_line(line)
                cleaned_line = sanitized.lower()

                is_header = (
                    len(cleaned_line.split()) <= 5 and
                    any(keyword in cleaned_line for section_vals in section_keywords.values() for keyword in section_vals)
                )

                if is_header:
                    for section, keywords in section_keywords.items():
                        if any(keyword in cleaned_line for keyword in keywords):
                            current_section = section
                            break
                else:
                    if sanitized:
                        sections[current_section].append(sanitized)

    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return {}

    return sections

def generate_grouped_content_string(parsed_sections):
    """
    Convert grouped content dictionary into a formatted string.
    """
    result = []
    for section, content in parsed_sections.items():
        result.append(f"=== {section.upper()} ===")
        result.extend(content)
        result.append("")
    return "\n".join(result)

# Degree patterns
degree_patterns = {
    "bachelor's degree": [
        r"\b(?:b\.?a\.?|b\.?s\.?)\b",
        r"\b(?:b\. ?s)\b",
        r"\b(?:b\.?sc\.?)\b",
        r"\bbachelor['’]s degree\b",
        r"\bbachelor['’]?s\b",
        r"\bbachelor of science\b",
        r"\bbachelor of arts\b"
    ],
    "master's degree": [
        r"\b(?:m\.?a\.?|m\.?s\.?)\b",
        r"\b(?:m\. ?s)\b",
        r"\b(?:m\.?ba)\b",
        r"\b(?:m\.?sc\.?)\b",
        r"\bmaster['’]s degree\b",
        r"\bmaster['’]?s\b",
        r"\bmaster of science\b",
        r"\bmaster of arts\b"
    ],
    "ph.d. degree": [
        r"\b(?:ph\.?d\.?|phd|dphil)\b",
        r"\bdoctor of philosophy\b",
        r"\bdoctoral degree\b",
        r"\bdoctorate\b"
    ]
}

def extract_degrees(text, patterns):
    matches = {}
    for degree, regex_list in patterns.items():
        pattern = '|'.join(regex_list)
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            matches[degree] = found
    return matches

def check_education_match(cv_text, job_description):
    cv_degrees = list(extract_degrees(cv_text, degree_patterns).keys())
    job_degrees = list(extract_degrees(job_description, degree_patterns).keys())
    degree_rank = {
        "ph.d. degree": 3,
        "master's degree": 2,
        "bachelor's degree": 1
    }

    cv_highest = max([degree_rank[deg] for deg in cv_degrees], default=0)
    job_required = max([degree_rank[deg] for deg in job_degrees], default=0)

    if cv_highest >= job_required:
        return "The CV meets the required education level."
    else:
        return "The CV does NOT meet the required education level."