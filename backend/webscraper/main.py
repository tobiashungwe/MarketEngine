import time
import streamlit as st
from scrape import scrape, clean_content, extract_content, scrape_company_page, split_dom_content
from parse import parse_with_ollama
from target_discovery import find_target_companies
from contact_recognition import check_for_generic_email
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the title of the app
st.title('Market Engine')

st.markdown("""
Our system automates outreach by connecting with companies through generic email addresses and contact forms. 
With **company-specific, personalized messages**, it introduces our AI assistant, driving engagement and conversions.
""")

# Initialize session state variables if they don't exist
if "company_urls" not in st.session_state:
    st.session_state["company_urls"] = []
if "confirmed_urls" not in st.session_state:
    st.session_state["confirmed_urls"] = []
if "parsed_companies" not in st.session_state:
    st.session_state["parsed_companies"] = []
if "company_selection" not in st.session_state:
    st.session_state["company_selection"] = []

# Target Discovery input fields
industry = st.text_input("Enter industry (e.g., technology, healthcare):")
location = st.text_input("Enter location (e.g., USA, Europe):")
MAX_RESULTS = 10 

# Step 1: Find target companies and add them to confirmed URLs for scraping
if st.button("Find Target Companies"):
    st.write("Finding target companies...")
    company_urls = find_target_companies(industry, location, MAX_RESULTS)
    st.session_state["company_urls"] = company_urls
    st.session_state["confirmed_urls"] = []
    st.session_state["parsed_companies"] = []
    st.write("Found companies:")

if "company_urls" in st.session_state and st.session_state["company_urls"]:
    st.subheader("Available Companies for Scraping")
    for url in st.session_state["company_urls"]:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.write(url)
        with col2:
            if st.button(f"Add {url}", key=f"confirm_{url}"):
                if url not in st.session_state["confirmed_urls"]:
                    st.session_state["confirmed_urls"].append(url)
                    st.success(f"{url} added for scraping.")

# Display selected companies for scraping
if st.session_state["confirmed_urls"]:
    st.subheader("Confirmed URLs for Scraping")
    for url in st.session_state["confirmed_urls"]:
        st.write(f"- {url}")

# Step 2: Confirm selected URLs and parse them
if st.button("Scrape Confirmed URLs"):
    st.write("Scraping confirmed URLs...")
    company_data_list = []
    
    for url in st.session_state["confirmed_urls"]:
        st.write(f"Scraping {url}...")
        result = scrape(url)
        
        if result and result["type"] == "profile":
            body_content = extract_content(result["content"])
            cleaned_content = clean_content(body_content)
            dom_chunks = split_dom_content(cleaned_content)
            company_data = parse_with_ollama(dom_chunks)

            if isinstance(company_data, list):
                company_data_list.extend(company_data)
            else:
                company_data_list.extend(company_data.splitlines())

    st.session_state["parsed_companies"] = [
        {"name": entry.split(": ")[0].strip(), "link": entry.split(": ")[1].strip()}
        for entry in company_data_list if ": " in entry
    ]

# Display parsed companies for outreach selection
if st.session_state["parsed_companies"]:
    st.subheader("Parsed Companies Available for Outreach")
    for idx, company in enumerate(st.session_state["parsed_companies"]):
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.write(f"{company['name']}: [Link]({company['link']})")
        with col2:
            if st.button(f"Add {company['name']}", key=f"add_parsed_{company['name']}_{idx}"):
                if company not in st.session_state["company_selection"]:
                    st.session_state["company_selection"].append(company)
                    st.success(f"{company['name']} added for outreach.")

# Display selected companies for outreach
if st.session_state["company_selection"]:
    st.subheader("Selected Companies for Outreach")
    for company in st.session_state["company_selection"]:
        st.write(f"- {company['name']}: [Link]({company['link']})")
        
if st.button("Confirm Outreach"):
    st.subheader("Contact Methods for Selected Companies")
    
    for company in st.session_state["company_selection"]:
        st.write(f"Processing contact methods for {company['name']} - [Website]({company['link']})")

        start_time = time.time()
        st.write(f"Scraping {company['name']} at {company['link']} for contact details and vision...")
        
        scrape_start = time.time()
        result = scrape_company_page(company["link"])
        scrape_end = time.time()
        st.write(f"Scraping completed for {company['name']} in {scrape_end - scrape_start:.2f} seconds.")

        if result and result["type"] == "company_info":
            html_content = result.get("content", "")

            st.write(f"Extracting emails for {company['name']}...")
            email_start = time.time()
            emails = check_for_generic_email(company["link"])
            email_end = time.time()
            st.write(f"Email extraction completed in {email_end - email_start:.2f} seconds.")
            
            st.write(f"**Emails for {company['name']}:**")
            if emails:
                for email in emails:
                    st.write(f"- {email}")
            else:
                st.write("No generic email addresses found for this company.")
            
            contact_forms = result.get("contact_forms", [])
            vision_text = result.get("vision", "No vision statement found.")
            
            st.write(f"**Contact Forms for {company['name']}:**")
            if contact_forms:
                for form in contact_forms:
                    st.write(f"- [Contact Form]({form})")
            else:
                st.write("No contact forms found.")

            st.write(f"**Vision/Mission for {company['name']}:**")
            st.write(vision_text)
        elif result and result["type"] == "blocked":
            st.write(f"Scraping blocked by robots.txt for {company['link']}.")
        else:
            st.write(f"Failed to retrieve content for {company['link']}. Reason: {result.get('reason', 'unknown')}")

        end_time = time.time()
        st.write(f"Total time for processing {company['name']}: {end_time - start_time:.2f} seconds.\n")
