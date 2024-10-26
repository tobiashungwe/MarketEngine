import streamlit as st
from scrape import scrape

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
    print(result)

