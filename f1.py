from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

# Step 1: Load the PDF
def load_pdf(file_path):
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"Loaded {len(documents)} pages from PDF")
        return documents
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return []

# Step 2: Split documents into smaller chunks
def split_documents(documents, chunk_size=2000, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    splits = text_splitter.split_documents(documents)
    print(f"Number of document splits: {len(splits)}")
    return splits

# Step 3: Create embeddings using Hugging Face
def create_embeddings(model_name="all-MiniLM-L6-v2"):
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("Embeddings created successfully.")
        return embeddings
    except Exception as e:
        print(f"Error creating embeddings: {e}")
        return None

# Step 4: Create Chroma vector store
def create_vector_store(document_splits, embeddings):
    try:
        vectorstore = Chroma.from_documents(
            documents=document_splits, 
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        print("Vector store created.")
        return vectorstore
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return None

# Step 5: Perform semantic search
# Step 5: Perform semantic search
def semantic_search(vectorstore, query):
    try:
        query_embedding = vectorstore._embedding_function.embed_query(query)  # ✅ Correct way to get embeddings
        results = vectorstore.similarity_search_by_vector(query_embedding)  # ✅ Use the correct function
        
        print("Top Search Results:")
        for i, res in enumerate(results):
            print(f"{i+1}. {res.page_content[:]}...")  # ✅ Show only relevant part
        
        return results
    except Exception as e:
        print(f"Error performing semantic search: {e}")
        return []


# Main execution function
def main():
    pdf_path = "C:\\12n8\\BDA-Unit-6.pdf"
    
    documents = load_pdf(pdf_path)
    if not documents:
        print("No documents loaded. Exiting.")
        return
    
    document_splits = split_documents(documents)
    
    embeddings = create_embeddings()
    if not embeddings:
        print("Error in creating embeddings. Exiting.")
        return
    
    vectorstore = create_vector_store(document_splits, embeddings)
    if not vectorstore:
        print("Error in creating vector store. Exiting.")
        return
    
    query = "describe stream processing fundamentals"
    results = semantic_search(vectorstore, query)

if __name__ == "__main__":
    main()
