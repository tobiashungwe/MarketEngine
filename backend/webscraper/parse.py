from langchain_ollama import OllamaLLM 
from langchain_core.prompts import ChatPromptTemplate

# Updated template to extract company names and relevant links
template = (
    "You are tasked with identifying companies and their most relevant links from the following text content: {dom_content}. "
    "Please follow these instructions carefully:\n\n"
    "1. **Extract Companies and Links:** Identify each company name and its most relevant website link from the content.\n"
    "2. **Format:** Use the format 'Company: <company_name>, Link: <company_link>' for each entry.\n"
    "3. **No Extra Content:** Do not include any additional text, comments, or explanations in your response.\n"
    "4. **Empty Response:** If no companies or links are found, return an empty string ('')."
)

model = OllamaLLM(model="llama3.1")

def parse_with_ollama(dom_chunks, parse_description="Extract companies and links"):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model 
     
    parsed_results = []
     
    for i, chunk in enumerate(dom_chunks, start=1):
        response = chain.invoke(
            {"dom_content": chunk, "parse_description": parse_description}
        )
        print(f"Parsed batch {i} of {len(dom_chunks)}")
        parsed_results.append(response)
        
    return '\n'.join(parsed_results)
