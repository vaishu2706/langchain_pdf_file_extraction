
from langchain_community.document_loaders import PyPDFLoader

def extract_section_with_langchain(pdf_path, section_keyword="Common stream processing use cases"):
    try:
        # Load the PDF using LangChain
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()  # Extract all text from the PDF
        
        extracted_section = []
        capture = False  # Flag to track when we start capturing text
        
        for doc in docs:
            text = doc.page_content  # Extract page text
            
            if section_keyword.lower() in text.lower():
                capture = True  # Start capturing once keyword is found
            
            if capture:
                extracted_section.append(text)
                
                # Stop capturing after a reasonable amount of content
                if len(" ".join(extracted_section)) > 2000:  
                    break  
        
        extracted_text = "\n".join(extracted_section)
        print("Extracted Section Content:")
        print(extracted_text[:500])  # Show preview of extracted content
        return extracted_text

    except Exception as e:
        print(f"Error extracting section: {e}")
        return ""

# Example usage
pdf_path = "C:\\12n8\\BDA-Unit-6.pdf"  # Replace with your actual PDF file path
conclusion_text = extract_section_with_langchain(pdf_path)
