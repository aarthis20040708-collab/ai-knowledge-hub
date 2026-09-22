from io import BytesIO
from pypdf import PdfReader

def extract_text_from_file(file_obj) -> dict:
    """
    Extracts text from a single uploaded file (PDF, TXT, MD, CSV, PY).
    Returns a dictionary containing filename, text, page_count, and word_count.
    """
    file_name = file_obj.name
    file_extension = file_name.split(".")[-1].lower()
    text = ""
    page_count = 1

    try:
        if file_extension == "pdf":
            # Process PDF file
            pdf_bytes = BytesIO(file_obj.read())
            reader = PdfReader(pdf_bytes)
            page_count = len(reader.pages)
            extracted_pages = []
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append(f"--- [Page {idx + 1}] ---\n{page_text.strip()}")
            text = "\n\n".join(extracted_pages)
        else:
            # Process text-based files (txt, md, py, csv, etc.)
            content = file_obj.read()
            if isinstance(content, bytes):
                text = content.decode("utf-8", errors="replace")
            else:
                text = str(content)

    except Exception as e:
        text = f"Error reading file {file_name}: {str(e)}"

    word_count = len(text.split())

    return {
        "filename": file_name,
        "extension": file_extension,
        "page_count": page_count,
        "word_count": word_count,
        "content": text.strip()
    }


def process_multiple_files(uploaded_files) -> list:
    """
    Processes an entire list of uploaded files and returns their extracted data.
    """
    documents = []
    for file in uploaded_files:
        doc_data = extract_text_from_file(file)
        documents.append(doc_data)
    return documents


def format_documents_context(documents: list) -> str:
    """
    Combines text from all processed documents into a single prompt-ready context.
    """
    if not documents:
        return ""

    context_blocks = []
    for doc in documents:
        header = f"=== DOCUMENT: {doc['filename']} ({doc['word_count']} words, {doc['page_count']} pages) ==="
        body = doc['content']
        context_blocks.append(f"{header}\n{body}\n{'=' * 40}")

    return "\n\n".join(context_blocks)
