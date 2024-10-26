import streamlit as st
from scrape import scrape, split_dom_content, clean_content, extract_content
# Set the title of the app
st.title('Machine Engine')

st.markdown("""
Our system automates outreach by connecting with companies through generic email addresses and contact forms. 
With **company-specific, personalized messages**, it introduces our AI assistant, driving engagement and conversions.
""")

url = st.text_input('Enter the URL of the website you want to scrape')

if st.button("Scrape Site"):
    st.write("Scraping the website")
    result = scrape(url)
    body_content = extract_content(result)
    cleaned_content = clean_content(body_content)
    st.session_state.dom_content = cleaned_content
    
    with st.expander("View Dom Content"):
        st.text_area("Dom Content", cleaned_content, height=300)


if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to parse? ")
    
    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing content")
            dom_chunks = split_dom_content(st.session_state.dom_content)
            