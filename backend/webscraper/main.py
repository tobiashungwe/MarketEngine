import streamlit as st
from scrape import scrape, clean_content, extract_content, split_dom_content
from parse import parse_with_ollama
from target_discovery import find_target_companies  # Import corrected here
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
if "selected_urls" not in st.session_state:
    st.session_state["selected_urls"] = []
if "confirmed_urls" not in st.session_state:
    st.session_state["confirmed_urls"] = []
if "company_selection" not in st.session_state:
    st.session_state["company_selection"] = {}

# Target Discovery input fields
industry = st.text_input("Enter industry (e.g., technology, healthcare):")
location = st.text_input("Enter location (e.g., USA, Europe):")
max_results = st.number_input("Max results", min_value=1, max_value=50, value=10)

# Button to find target companies based on specified criteria
if st.button("Find Target Companies"):
    st.write("Finding target companies...")
    company_urls = find_target_companies(industry, location, max_results)  # Call target discovery function
    st.session_state["company_urls"] = company_urls  # Store the found URLs in session state
    st.session_state["selected_urls"] = []  # Reset selected URLs on each new search
    st.write("Found companies:")

# Display each URL with a checkbox for selection, allowing the user to select multiple sites
if "company_urls" in st.session_state:
    for url in st.session_state["company_urls"]:
        # Check if this URL is selected and set the checkbox accordingly
        is_checked = url in st.session_state["selected_urls"]
        if st.checkbox(url, key=url, value=is_checked):
            if url not in st.session_state["selected_urls"]:
                st.session_state["selected_urls"].append(url)
        else:
            if url in st.session_state["selected_urls"]:
                st.session_state["selected_urls"].remove(url)

# Button to confirm the selection and trigger scraping
if st.button("Confirm Selection"):
    st.session_state["confirmed_urls"] = list(st.session_state["selected_urls"])  # Save the confirmed URLs for scraping
    st.write("Confirmed URLs for scraping:", st.session_state["confirmed_urls"])

# Display results only after confirmation
if "confirmed_urls" in st.session_state and st.session_state["confirmed_urls"]:
    company_data_list = []  # Initialize list to store company data results
    
    for url in st.session_state["confirmed_urls"]:
        st.write(f"Scraping {url}...")
        result = scrape(url)
        
        if result and result["type"] == "profile":
            # Extract DOM content and split it for `ollama`
            body_content = extract_content(result["content"])
            cleaned_content = clean_content(body_content)
            dom_chunks = split_dom_content(cleaned_content)
            
            # Parse DOM content with `ollama` to get company data
            company_data = parse_with_ollama(dom_chunks)

            # Use append instead of extend if company_data is a list of full entries
            if isinstance(company_data, list):
                company_data_list.append(company_data)
            else:
                # If company_data is a single string, split it into lines
                company_data_list.append(company_data.splitlines())

    # Flatten company_data_list if necessary
    company_data_list = [item for sublist in company_data_list for item in sublist] if any(isinstance(i, list) for i in company_data_list) else company_data_list

    # Informative text display
    st.subheader("Companies Identified")
    for company_entry in company_data_list:
        if ":" in company_entry:
            parts = company_entry.split(": ")
            company_name = parts[0].strip()
            company_link = parts[1].strip() if len(parts) > 1 else None

            # Display company name and link status
            if company_link and company_link.startswith("http"):
                st.write(f"**{company_name}**: [Website]({company_link})")
            else:
                st.write(f"**{company_name}**: No website link found")

    # Display companies with links in a checkbox list
    st.subheader("Select Companies for Outreach")
    if company_data_list:
        for index, company_entry in enumerate(company_data_list):
            if ":" in company_entry:
                parts = company_entry.split(": ")
                company_name = parts[0].strip()
                company_link = parts[1].strip() if len(parts) > 1 else None

                # Only add companies with valid links to the checkbox list
                if company_link and company_link.startswith("http"):
                    checkbox_key = f"{company_name}_{company_link}_{index}"
                    if st.checkbox(f"{company_name} - [Link]({company_link})", key=checkbox_key):
                        st.session_state["company_selection"][company_name] = company_link

    # Final selected companies with links
    st.subheader("Selected Companies for Outreach")
    if st.session_state["company_selection"]:
        for company_name, link in st.session_state["company_selection"].items():
            st.write(f"- {company_name}: [Link]({link})")
    else:
        st.write("No companies selected yet.")
