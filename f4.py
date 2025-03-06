
from flask import Flask, request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import uuid
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

documents_db = {}
PDF_FILE_PATH = "C:\\12n8\\BDA-Unit-6.pdf"

def load_pdf(file_path):
    try:
        logger.info(f"Loading PDF from {file_path}")
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} pages from PDF")
        return documents
    except FileNotFoundError:
        logger.error(f"PDF file not found: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading PDF: {e}")
        return None

@app.route("/documents/create", methods=["POST"])
def create_document():
    document_id = str(uuid.uuid4())
    documents_db[document_id] = PDF_FILE_PATH
    return jsonify({"document_id": document_id, "file_path": PDF_FILE_PATH})

@app.route("/documents/<document_id>", methods=["GET"])
def get_document(document_id):
    if document_id not in documents_db:
        return jsonify({"error": "Document not found"}), 404
    return jsonify({"document_id": document_id, "file_path": documents_db[document_id]})

@app.route("/documents/<document_id>", methods=["PUT"])
def update_document(document_id):
    data = request.get_json()
    new_path = data.get("file_path")
    if document_id not in documents_db:
        return jsonify({"error": "Document not found"}), 404
    documents_db[document_id] = new_path
    return jsonify({"document_id": document_id, "file_path": new_path})

@app.route("/documents/<document_id>", methods=["DELETE"])
def delete_document(document_id):
    if document_id not in documents_db:
        return jsonify({"error": "Document not found"}), 404
    del documents_db[document_id]
    return jsonify({"message": "Document deleted successfully"})

@app.route("/documents/<document_id>/extract-text", methods=["GET"])
def extract_text(document_id):
    if document_id not in documents_db:
        return jsonify({"error": "Document not found"}), 404
    file_path = documents_db[document_id]
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        extracted_text = " ".join([doc.page_content.replace("\uf0d8", "-").replace("\n", " ").strip() for doc in documents])
        extracted_text = re.sub(r'\s+', ' ', extracted_text).strip()
        
        return jsonify({"document_id": document_id, "extracted_text": extracted_text})
    except Exception as e:
        return jsonify({"error": f"Failed to extract text: {str(e)}"})

@app.route("/documents/<document_id>/extract-text/search", methods=["GET"])
def search_text(document_id):
    keyword = request.args.get("keyword")
    
    if not keyword:
        return jsonify({"error": "Keyword parameter is required"}), 400
    
    if document_id not in documents_db:
        return jsonify({"error":"document not found"})
    try:
        file_path = documents_db[document_id]
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        extracted_text = " ".join([doc.page_content.replace("\uf0d8", "-").replace("\n", " ").strip() for doc in documents])
        extracted_text = re.sub(r'\s+', ' ', extracted_text).strip()
        keyword = keyword.strip().lower()
        
        matching_sentences = [sentence for sentence in extracted_text.split('.') if keyword.lower() in sentence.lower()]
        
        if matching_sentences:
            return jsonify({"document_id": document_id, "message": "Keyword found", "matching_text": matching_sentences})
        else:
            return jsonify({"document_id": document_id, "message": "No matching content found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to search text: {str(e)}"}), 500
    



@app.route("/documents/<document_id>/extract-text/update", methods=["PUT"])
def update_text(document_id):
    data = request.get_json()
    old_text = data.get("old_text")
    new_text = data.get("new_text")

    if not old_text or not new_text:
        return jsonify({"error": "Both old_text and new_text are required"}), 400

    if document_id not in documents_db:
        return jsonify({"error": "Document not found"}), 404

    file_path = documents_db[document_id]
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        extracted_text = "\n".join([doc.page_content for doc in documents])

        if old_text not in extracted_text:
            return jsonify({"error": "Text not found"}), 404

        updated_text = extracted_text.replace(old_text, new_text)

        return jsonify({"document_id": document_id, "updated_text": updated_text})
    except Exception as e:
        return jsonify({"error": f"Failed to update text: {str(e)}"}), 500


@app.route("/documents/<document_id>/extract-text/delete", methods=["DELETE"])
def delete_text(document_id):
    data = request.get_json()
    text_to_delete = data.get("text_to_delete")

    if not text_to_delete:
        return jsonify({"error": "text_to_delete is required"}), 400

    if document_id not in documents_db:
        return jsonify({"error":"document not found"}) 
    file_path = documents_db[document_id]
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        extracted_text = "\n".join([doc.page_content for doc in documents])

        if text_to_delete not in extracted_text:
            return jsonify({"error": "Text not found"}), 404

        updated_text = extracted_text.replace(text_to_delete, "")

        return jsonify({"document_id": document_id, "updated_text": updated_text})
    except Exception as e:
        return jsonify({"error": f"Failed to delete text: {str(e)}"}), 500

if os.path.exists(PDF_FILE_PATH):
    logger.info(f"Loading included PDF: {PDF_FILE_PATH}")
    load_pdf(PDF_FILE_PATH)
else:
    logger.error(f"Included PDF file not found: {PDF_FILE_PATH}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
