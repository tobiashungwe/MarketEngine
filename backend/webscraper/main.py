import streamlit as st
from scrape import scrape, split_dom_content, clean_content, extract_content
from parse import parse_with_ollama
from message_generator import generate_message
from email_sender import send_email
from target_discovery import find_target_companies
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the title of the app
st.title('Market Engine')

st.markdown("""
Our system automates outreach by connecting with companies through generic email addresses and contact forms. 
With **company-specific, personalized messages**, it introduces our AI assistant, driving engagement and conversions.
""")

# Target Discovery input fields
industry = st.text_input("Enter industry (e.g., technology, healthcare):")
location = st.text_input("Enter location (e.g., USA, Europe):")
max_results = st.number_input("Max results", min_value=1, max_value=50, value=10)

# Button to find target companies based on specified criteria
if st.button("Find Target Companies"):
    st.write("Finding target companies...")
    company_urls = find_target_companies(industry, location, max_results)
    st.session_state.company_urls = company_urls
    st.write("Found companies:", company_urls)

# Scrape each company URL from target discovery
for url in st.session_state.get("company_urls", []):
    st.write(f"Scraping {url}")
    result = scrape(url)
    if result:
        body_content = extract_content(result)
        cleaned_content = clean_content(body_content)
        
        with st.expander(f"View Content for {url}"):
            st.text_area(f"DOM Content for {url}", cleaned_content, height=300)

        # Parsing section
        parse_description = st.text_area("Describe what you want to parse for this company:")
        if st.button(f"Parse Content for {url}"):
            if parse_description:
                st.write("Parsing content...")
                dom_chunks = split_dom_content(cleaned_content)
                parsed_result = parse_with_ollama(dom_chunks, parse_description)
                st.write(parsed_result)

        # Personalize Message section
        company_name = st.text_input("Company Name", value=url.split("//")[1].split(".")[0])
        mission = st.text_input("Company Mission or Introduction")

        if st.button(f"Generate Message for {url}"):
            if company_name and mission:
                personalized_message = generate_message(company_name, mission)
                st.session_state[f"generated_message_{url}"] = personalized_message
                st.write("Generated Message:")
                st.text_area("Personalized Message", personalized_message, height=150)
            else:
                st.warning("Please enter the company name and mission.")

        # Email sending section
        recipient_email = st.text_input("Recipient Email Address")
        if st.button(f"Send Email to {url}") and f"generated_message_{url}" in st.session_state:
            if recipient_email:
                subject = "Introduction to Our Services"
                send_email(recipient_email, subject, st.session_state[f"generated_message_{url}"])
                st.success(f"Email sent to {recipient_email}")
            else:
                st.warning("Please enter the recipient email address.")
