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

# Initialize vectorstore only if we have documents
vectorstore = None

if documents:
    # Enhanced text splitting with better chunk management
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=250,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]  # Better separation logic
    )

    splits = text_splitter.split_documents(documents)
    print(f"Split the documents into {len(splits)} chunks.")

    # Initialize the Q&A optimized embedding model
    print("📊 Initializing Q&A optimized embeddings...")
    try:
        embedding_function = SentenceTransformerEmbeddings(model_name="multi-qa-mpnet-base-dot-v1")
        print("✅ Q&A optimized embedding model loaded successfully")
    except Exception as e:
        print(f"⚠️ Error loading Q&A model, falling back to default model: {str(e)}")
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    collection_name = "enhanced_collection"  # Updated collection name
    
    try:
        vectorstore = Chroma.from_documents(
            collection_name=collection_name,
            documents=splits,
            embedding=embedding_function,
            persist_directory="./chroma_db"
        )
        print("✅ Vectorstore created successfully with Q&A optimized embeddings.")
    except Exception as e:
        print(f"❌ Error creating vectorstore: {str(e)}")
        vectorstore = None
else:
    print("No documents found. Vectorstore will be created when documents are added.")


class RagToolSchema(BaseModel):
    question: str


@tool(args_schema=RagToolSchema)
def retriever_tool(question):
    """Tool to Retrieve Semantically Similar documents to answer User Questions using Q&A optimized embeddings"""
    print("INSIDE RETRIEVER NODE")
    
    # Check if vectorstore exists (i.e., if documents were loaded)
    if vectorstore is None:
        return "No documents are available in the knowledge base. Please add PDF or DOCX files to the ./docs folder and restart the system."
    
    try:
        # Enhanced retrieval with better parameters
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 3,  # Increased from 2 to get more context
                "score_threshold": 0.5  # Only return results above similarity threshold
            }
        )
        
        retriever_result = retriever.invoke(question)
        
        if not retriever_result:
            return "No relevant documents found in the knowledge base."
        
        # Enhanced result formatting
        formatted_results = []
        for i, doc in enumerate(retriever_result, 1):
            content = doc.page_content
            # Add source information if available
            source = doc.metadata.get('source', 'Unknown source')
            page = doc.metadata.get('page', 'N/A')
            
            formatted_results.append(
                f"📄 **Source {i}** (from {os.path.basename(source)}, page {page}):\n{content}"
            )
        
        return "\n\n" + "\n\n---\n\n".join(formatted_results)
            
    except Exception as e:
        return f"Error retrieving documents: {str(e)}"


# Test the retriever if documents are available
if documents and vectorstore:
    # Use same parameters as the actual tool for consistent testing
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 3,
            "score_threshold": 0.5
        }
    )
    try:
        retriever_results = retriever.invoke("Who is the founder of Futuresmart AI?")
        print("✅ Test query successful with Q&A optimized embeddings")
    except Exception as e:
        print(f"❌ Error in test query: {str(e)}")
else:
    print("⏭️ Skipping test query - no documents available.")


