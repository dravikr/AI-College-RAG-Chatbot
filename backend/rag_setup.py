import os
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PDF_FILE = os.getenv("PDF_FILE", "NGP.pdf")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def setup_event_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

def setup_rag():
    loop = setup_event_loop()
    loader = PyPDFLoader(PDF_FILE)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=CHROMA_DIR)
    return vector_store

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant for **NGP College**. Answer the question in a natural, human-like way using **only the information provided in the context**.

Context:
{context}

Question: {input}

Guidelines:
- Provide clear, concise answers in **2 lines max**.
- Do NOT add extra closing phrases like "Hope this helps!" or "I hope this answers your question."
- If the question is **not related to SRM Trichy** or the information is not in the context, respond politely in one line.
- Keep the tone **friendly and professional**.

Answer:
""")
document_chain = create_stuff_documents_chain(llm, prompt)
vector_store = setup_rag()
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
retrieval_chain = create_retrieval_chain(retriever, document_chain)

def ask_question(question: str) -> str:
    response = retrieval_chain.invoke({"input": question})
    return response["answer"]
