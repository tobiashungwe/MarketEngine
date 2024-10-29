import re
from bs4 import BeautifulSoup
import spacy

# Load spaCy model for NLP (you can use a smaller model like 'en_core_web_sm')
nlp = spacy.load("en_core_web_sm")

def extract_emails(html_content):
    """Extract generic email addresses from HTML content."""
    email_pattern = r"[a-zA-Z0-9._%+-]+@(?!example\.com|gmail\.com|yahoo\.com|hotmail\.com)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, html_content)
    return list(set(emails))  # Remove duplicate email addresses

def extract_contact_forms(html_content, base_url):
    """Identify contact forms based on form tags and keywords, using NLP for better context recognition."""
    soup = BeautifulSoup(html_content, "html.parser")
    contact_forms = []

    for form in soup.find_all("form"):
        # Analyze the text within and around the form element
        form_text = form.get_text(separator=" ").strip().lower()
        doc = nlp(form_text)

        # Check for contact-related keywords using NLP
        contact_keywords = ["contact", "inquiry", "message", "support", "feedback", "help"]
        is_contact_form = any(token.lemma_ in contact_keywords for token in doc)

        # Additionally check labels and placeholders
        labels = [label.get_text().lower() for label in form.find_all("label")]
        placeholders = [input.get("placeholder", "").lower() for input in form.find_all("input")]
        is_contact_form |= any(keyword in label or keyword in placeholder for keyword in contact_keywords for label, placeholder in zip(labels, placeholders))

        # If determined to be a contact form, get the form's action URL
        if is_contact_form:
            form_action = form.get("action")
            if form_action:
                # Construct full URL if the action is relative
                form_url = form_action if form_action.startswith("http") else f"{base_url.rstrip('/')}/{form_action.lstrip('/')}"
                contact_forms.append(form_url)

    return contact_forms
