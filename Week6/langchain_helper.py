import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

load_dotenv()

# ---- LLM Setup ----
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0.1
)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb_file_path = "faiss_index"


# ---- Vector DB ----
def create_vector_db():
    loaders = [
        CSVLoader(file_path="healthcare_faqs.csv", source_column="prompt"),
        CSVLoader(file_path="doctors.csv", source_column="DoctorName")
    ]
    all_data = []
    for loader in loaders:
        all_data.extend(loader.load())

    vectordb = FAISS.from_documents(all_data, embedding=embedding_model)
    vectordb.save_local(vectordb_file_path)


def get_qa_chain():
    vectordb = FAISS.load_local(
        vectordb_file_path,
        embedding_model,
        allow_dangerous_deserialization=True
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    prompt_template = """You are a helpful healthcare assistant.
    Use the context below to answer the question.
    If answer is not found, just say "I don't know."

    CONTEXT: {context}
    QUESTION: {question}"""

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        input_key="query",
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
