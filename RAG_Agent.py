import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import tool
from langchain.schema import Document
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from pydantic import BaseModel


def load_documents(folder_path: str) -> List[Document]:
    """Load documents from a folder with error handling."""
    documents = []
    
    # Check if folder exists, if not create a default docs folder
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} not found. Creating it...")
        os.makedirs(folder_path, exist_ok=True)
        print(f"Please add PDF or DOCX files to {folder_path} folder.")
        return documents
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if filename.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            elif filename.endswith('.docx'):
                loader = Docx2txtLoader(file_path)
            else:
                print(f"Unsupported file type: {filename}")
                continue
            documents.extend(loader.load())
            print(f"Loaded: {filename}")
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")
            continue
    
    return documents


# Use relative path that works in current directory
folder_path = "./docs"
documents = load_documents(folder_path)
print(f"Loaded {len(documents)} documents from the folder.")

# Only proceed if we have documents
if documents:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    splits = text_splitter.split_documents(documents)
    print(f"Split the documents into {len(splits)} chunks.")

    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    collection_name = "my_collection"
    vectorstore = Chroma.from_documents(
        collection_name=collection_name,
        documents=splits,
        embedding=embedding_function,
        persist_directory="./chroma_db"
    )
else:
    # Create empty vectorstore for when no documents are available
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        collection_name="my_collection",
        embedding_function=embedding_function,
        persist_directory="./chroma_db"
    )
    print("No documents found. Created empty vectorstore.")


class RagToolSchema(BaseModel):
    question: str


@tool(args_schema=RagToolSchema)
def retriever_tool(question):
    """Tool to Retrieve Semantically Similar documents to answer User Questions related to FutureSmart AI"""
    print("INSIDE RETRIEVER NODE")
    try:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        retriever_result = retriever.invoke(question)
        
        if not retriever_result:
            return "No relevant documents found in the knowledge base."
            
        return "\n\n".join(doc.page_content for doc in retriever_result)
    except Exception as e:
        return f"Error retrieving documents: {str(e)}"


# Test the retriever if documents are available
if documents:
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    try:
        retriever_results = retriever.invoke("Who is the founder of Futuresmart AI?")
        print("Test query results:", retriever_results)
    except Exception as e:
        print(f"Error in test query: {str(e)}")
