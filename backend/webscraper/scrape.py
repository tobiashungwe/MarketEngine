from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
import requests
from transformers import pipeline
from urllib.parse import urlparse
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
import requests
import time
from contact_recognition import extract_contact_forms, extract_emails, extract_vision_statement

# Replace with your actual Bright Data authentication details
AUTH = 'brd-customer-hl_6b9503ac-zone-webscraper_machine_engine:86kha6kfda9q'
SBR_WEBDRIVER = f'https://{AUTH}@zproxy.lum-superproxy.io:9515'

# Initialize the LLM pipeline for text classification
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# List of labels that indicate a company profile
PROFILE_LABELS = ["Website", "Employees", "Locations", "Industries", "Jobs"]

# Threshold for useful links needed to classify a page as "useful"
LINK_THRESHOLD = 3

# List of common domains to exclude
EXCLUDED_DOMAINS = ["facebook.com", "instagram.com", "linkedin.com", "twitter.com", "youtube.com", "pinterest.com"]

def respect_robots_txt(website):
    """Checks robots.txt to determine if scraping is allowed for the URL."""
    robots_url = f"{website}/robots.txt"
    response = requests.get(robots_url)
    if response.status_code == 200:
        if "Disallow: /" in response.text:
            print("Blocked by robots.txt")
            return False
    return True

def is_useful_profile_page(soup):
    """Analyzes the page structure to determine if it has company profile-like sections."""
    # Count occurrences of profile labels to assess if the page has structured company information
    profile_score = 0
    for label in PROFILE_LABELS:
        if soup.find(text=re.compile(label, re.IGNORECASE)):
            profile_score += 1

    print(f"Profile score based on labels: {profile_score}")
    # Consider a page useful if it has multiple profile-related labels
    return profile_score >= 3  # Adjust threshold as needed

def classify_link_context(context_text):
    """Uses LLM to classify if the context around a link suggests it is a direct company link."""
    # Classify the surrounding text to see if it's relevant to a company link
    result = classifier(context_text[:512])  # Limit to 512 characters for efficiency
    label = result[0]['label']
    score = result[0]['score']
    return label == "LABEL_1" and score > 0.8  # Adjust threshold as needed for context relevance

def extract_company_links(soup, base_domain):
    """Extracts and classifies outbound links to determine if they are likely to be company links."""
    company_links = []
    
    for link in soup.find_all("a", href=True):
        href = link['href']
        parsed_url = urlparse(href)
        domain = parsed_url.netloc
        
        # Skip internal and excluded domains
        if not domain or base_domain in domain or domain in EXCLUDED_DOMAINS:
            continue

        # Get surrounding text as context
        context_text = link.get_text() or link.find_parent().get_text()
        
        # Classify context to check if the link is likely a company link
        if classify_link_context(context_text):
            company_links.append(href)
    
    return company_links

def scrape(website):
    """Main scrape function that detects and processes aggregation pages or directly scrapes content."""
    if not respect_robots_txt(website):
        return None

    print("Launching chrome browser for direct content scraping...")
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
    options = ChromeOptions()
    driver = None  # Initialize the driver to None for error handling

    try:
        # Start the driver session
        driver = Remote(sbr_connection, options=options)
        driver.get(website)
        
        print('Waiting for captcha to solve...')
        solve_res = driver.execute('executeCdpCommand', {
            'cmd': 'Captcha.waitForSolve',
            'params': {'detectTimeout': 1000},
        })
        print('Captcha solve status:', solve_res.get('value', {}).get('status', 'unknown'))
        
        # Take a screenshot for verification
        driver.get_screenshot_as_file('./page.png')
        print('Page loaded successfully, beginning to scrape content...')
        
        # Get page source
        html = driver.page_source

    except Exception as e:
        print(f"Error during scraping: {e}")
        html = None  # Set html to None if an error occurs
    finally:
        # Ensure driver quits only if it was started
        if driver:
            driver.quit()

    if html:
        # Parse the page content
        soup = BeautifulSoup(html, 'html.parser')
        base_domain = urlparse(website).netloc

        # First, check if the page has structured profile information
        if is_useful_profile_page(soup):
            print("Page classified as useful based on profile structure.")
            return {"type": "profile", "content": html}

        # If no structured profile is found, attempt link extraction
        company_links = extract_company_links(soup, base_domain)
        
        # Check if we have enough company links to consider this page useful
        if len(company_links) >= LINK_THRESHOLD:
            print("Page classified as useful based on company links.")
            return {"type": "aggregation", "links": company_links}
        else:
            print("Page classified as not useful.")
            return {"type": "not_useful"}
    else:
        print("Failed to retrieve page content.")
        return None

def extract_content(html_content):
    """Extracts the body content from HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    body_content = soup.body
    if body_content:
        return str(body_content)
    return "" 

def clean_content(body_content):
    """Cleans the body content by removing scripts and styles, and stripping excess whitespace."""
    if not isinstance(body_content, str):
        body_content = str(body_content) if body_content else ""
        
    soup = BeautifulSoup(body_content, 'html.parser')
    for script_or_style in soup(['script', 'style']):
        script_or_style.extract()
        
    cleaned_content = soup.get_text(separator='\n')
    cleaned_content = '\n'.join([line for line in cleaned_content.split('\n') if line.strip()])
    return cleaned_content

def split_dom_content(dom_content, max_len=6000):
    """Splits DOM content into chunks for parsing, if needed."""
    return [dom_content[i:i+max_len] for i in range(0, len(dom_content), max_len)]

def scrape_company_page(website):
    """Scrape an individual company page for contact info and vision/mission."""
    
    # Initialize result dictionary
    result = {"type": "company_info", "content": None, "emails": [], "contact_forms": [], "vision": ""}
    
    # Setup the remote connection
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
    options = ChromeOptions()
    driver = None  # Initialize the driver to None for error handling

    # Ensure the URL is well-formed
    if not website.startswith("http"):
        website = "http://" + website

    try:
        # Start the Selenium Remote WebDriver session
        driver = Remote(sbr_connection, options=options)
        driver.get(website)
        
        # Wait for the body of the page to be fully loaded
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        print("Page loaded successfully, beginning to scrape content...")

        # Additional navigation to the /contact page if not on it
        if "/contact" not in driver.current_url:
            contact_url = website.rstrip('/') + "/contact"
            print(f"Navigating to contact page at {contact_url}")
            driver.get(contact_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            print("Contact page loaded successfully.")

        # Take a screenshot for verification
        driver.get_screenshot_as_file("./company_page.png")
        
        # Capture the HTML content of the page
        result["content"] = driver.page_source

        # Extract emails and contact forms from the page content
        result["emails"] = extract_emails(result["content"])
        result["contact_forms"] = extract_contact_forms(result["content"], website)

        # Optionally, extract the vision/mission statement
        result["vision"] = extract_vision_statement(result["content"])

    except requests.exceptions.RequestException as req_err:
        print(f"Network error while accessing {website}: {req_err}")
        result["type"] = "error"
        result["reason"] = "network_error"
    except Exception as e:
        print(f"General error while scraping {website}: {e}")
        result["type"] = "error"
        result["reason"] = str(e)
    finally:
        # Ensure the driver quits if it was started
        if driver:
            driver.quit()

    # If no content was retrieved, mark the result as an error
    if not result["content"]:
        result["type"] = "error"
        result["reason"] = "No content retrieved"

    return result