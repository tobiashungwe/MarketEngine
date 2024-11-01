import re
from bs4 import BeautifulSoup
import spacy
import time, os
import openai
from dotenv import load_dotenv


# Load spaCy model for NLP (you can use a smaller model like 'en_core_web_sm')
load_dotenv()
print("Loading spaCy model...")
nlp_load_start = time.time()
nlp = spacy.load("en_core_web_sm")
nlp_load_end = time.time()
print(f"SpaCy model loaded in {nlp_load_end - nlp_load_start:.2f} seconds.")
API_KEY = os.environ.get("OPENAI_API_KEY")
from openai import OpenAI
client = OpenAI(
    api_key= API_KEY
)
# Load environment variables from .env file


# Set your OpenAI API key
# client = OpenAI(
#     # This is the default and can be omitted
#     api_key=os.environ.get("OPENAI_API_KEY"),
# )

# openai.api_key = os.environ.get("OPENAI_API_KEY")



def extract_emails(html_content):
    """Enhanced email extraction using regex and NLP context to capture obfuscated patterns and contact-related sentences."""
    print("Starting email extraction...")
    
    # Primary email regex pattern with exclusions for common image extensions
    email_pattern = r"[a-zA-Z0-9._%+-]+@(?!example\.com|gmail\.com|yahoo\.com|hotmail\.com|[a-zA-Z0-9.-]+\.(jpg|jpeg|png|webp|svg|gif))[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    regex_emails = re.findall(email_pattern, html_content)

    # Additional patterns for obfuscated emails with common representations like "at" or spaces
    obfuscated_patterns = [
        r"[a-zA-Z0-9._%+-]+\s@\s[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # Obfuscated with spaces
        r"[a-zA-Z0-9._%+-]+<at>[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",   # Obfuscated with "<at>"
        r"[a-zA-Z0-9._%+-]+ \(at\) [a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # Obfuscated with "(at)"
    ]
    for pattern in obfuscated_patterns:
        obfuscated_emails = re.findall(pattern, html_content)
        for email in obfuscated_emails:
            cleaned_email = email.replace(" ", "").replace("<at>", "@").replace("(at)", "@")
            regex_emails.append(cleaned_email)

    # Use NLP to find sentences with contact keywords that might contain emails
    doc = nlp(html_content)
    nlp_emails = []
    contact_keywords = ["email", "contact", "reach us at", "get in touch", "inquiries", "support"]
    for sentence in doc.sents:
        if any(keyword in sentence.text.lower() for keyword in contact_keywords):
            sentence_emails = re.findall(email_pattern, sentence.text)
            nlp_emails.extend(sentence_emails)

    all_emails = list(set(regex_emails + nlp_emails))  # Remove duplicates

    if all_emails:
        print(f"Emails detected: {all_emails}")
    else:
        print("No emails found on this page.")
    
    return all_emails

def check_for_generic_email(url):
    try:
        # OpenAI API request to find generic emails
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that checks if a website has a generic email for contact."},
                {"role": "user", "content": f"Check if the website {url} has a generic email address like info@domain.com, support@domain.com, or contact@domain.com. If found, list the email(s)."}
            ]
        )
        emails = completion.choices[0].message.content.strip()
        return emails.split(", ") if emails else []
    except Exception as e:
        print("Error checking for generic emails:", e)
        return []

def extract_contact_forms(html_content, base_url):
    """Identify contact forms and links to contact pages based on form tags, buttons, and NLP analysis."""
    print("Starting contact form extraction...")
    form_start = time.time()

    soup = BeautifulSoup(html_content, "html.parser")
    contact_forms = []
    contact_keywords = ["contact", "inquiry", "message", "support", "feedback", "help"]

    for idx, form in enumerate(soup.find_all("form")):
        print(f"Analyzing form {idx + 1}...")
        form_analysis_start = time.time()

        # Extract form text and process with NLP
        form_text = form.get_text(separator=" ").strip().lower()
        doc = nlp(form_text)

        # Check for contact-related keywords in the form text
        is_contact_form = any(token.lemma_ in contact_keywords for token in doc)

        # Check labels and placeholders for contact keywords
        labels = [label.get_text().lower() for label in form.find_all("label")]
        placeholders = [input.get("placeholder", "").lower() for input in form.find_all("input")]

        label_placeholder_check = any(keyword in label or keyword in placeholder for keyword in contact_keywords for label, placeholder in zip(labels, placeholders))
        is_contact_form |= label_placeholder_check

        # Check submit buttons for contact-related text
        submit_buttons = [btn.get_text().lower() for btn in form.find_all("button", type="submit")]
        button_text_check = any("contact" in btn_text or "submit" in btn_text for btn_text in submit_buttons)
        is_contact_form |= button_text_check

        # If this is a contact form, attempt to get the form action URL
        if is_contact_form:
            form_action = form.get("action")
            if form_action:
                form_url = form_action if form_action.startswith("http") else f"{base_url.rstrip('/')}/{form_action.lstrip('/')}"
                contact_forms.append(form_url)
                print(f"Contact form detected. Form URL: {form_url}")
            else:
                print("Contact form detected but no action URL found.")

        form_analysis_end = time.time()
        print(f"Form {idx + 1} analysis completed in {form_analysis_end - form_analysis_start:.2f} seconds.")

    # Also check anchor tags that may link to a contact form or contact page
    for a_tag in soup.find_all("a", href=True):
        link_text = a_tag.get_text(separator=" ").strip().lower()
        if "contact" in link_text or any(kw in link_text for kw in contact_keywords):
            form_url = a_tag["href"]
            form_url = form_url if form_url.startswith("http") else f"{base_url.rstrip('/')}/{form_url.lstrip('/')}"
            contact_forms.append(form_url)

    form_end = time.time()
    print(f"Contact form extraction completed in {form_end - form_start:.2f} seconds. Total forms found: {len(contact_forms)}")
    return list(set(contact_forms))

def extract_vision_statement(html_content):
    """Extracts a potential vision or mission statement from the HTML content."""
    print("Starting vision statement extraction...")
    vision_start = time.time()

    soup = BeautifulSoup(html_content, 'html.parser')
    keywords = ["vision", "mission", "about us", "our values", "our goals", "what we believe", "purpose"]

    for keyword in keywords:
        matching_elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
        
        for element in matching_elements:
            parent = element.find_parent(['p', 'div', 'section'])
            if parent:
                vision_text = parent.get_text(separator=" ").strip()
                if len(vision_text) > 30:
                    vision_end = time.time()
                    print(f"Vision statement extraction completed in {vision_end - vision_start:.2f} seconds.")
                    return vision_text

    vision_end = time.time()
    print(f"No vision statement found. Completed in {vision_end - vision_start:.2f} seconds.")
    return "No vision or mission statement found on this page."


