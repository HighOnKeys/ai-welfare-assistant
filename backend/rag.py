import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
vectorstore = None


load_dotenv()


def build_vectorstore():

    global vectorstore

    if vectorstore is not None:
        return vectorstore

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    schemes_path = os.path.join(BASE_DIR, "..", "data", "schemes.txt")
    with open(
        schemes_path,
        "r",
        encoding="utf-8",
    ) as f:

        text = f.read()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_text(text)

    docs = [
        Document(page_content=chunk)
        for chunk in chunks
    ]

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(
        docs,
        embeddings,
    )

    return vectorstore


def get_scheme_info(query):

    vectorstore = build_vectorstore()

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 2}
    )

    docs = retriever.invoke(query)

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # llm = ChatGoogleGenerativeAI(
    #    model="gemini-2.5-flash",
    #    temperature=0.2,
    # )
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
    )

    prompt = f"""
You are a government welfare assistant.

Answer ONLY using the provided context.

If the answer is not available in the context, say:

"I do not have enough verified information."

Do not make assumptions.

CONTEXT:
{context}

QUESTION:
{query}

Provide:
- Benefits
- Eligibility
- Required Documents
- Application Process

Use simple language.
"""

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":

    print("\n--- PM-KISAN TEST ---\n")

    answer = get_scheme_info(
        "Tell me about PM-KISAN."
    )

    print(answer)

    print("\n--- HALLUCINATION TEST ---\n")

    answer = get_scheme_info(
        "Tell me about PM Mudra Loan."
    )

    print(answer)
