from vcdvcd import VCDVCD
import json
import requests
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from openai import OpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_deepseek import ChatDeepSeek
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
MODEL_NAME = "deepseek-reasoner"
API_KEY="my-api-key"

def llama(greet, prompt):
    print('Waiting for answer from llama3...\n')
    llm = OllamaLLM(model='llama3:latest', base_url='http://localhost:11434', temperature=0.0)
    
    output = ""
    for chunk in llm.stream(greet + prompt):
        output += chunk

    print(f'\n\n-------------------------- ANSWER --------------------------------\n')
    print(output)

def deepseek(greet, prompt):
    print('Waiting for answer from Deepseek...\n')
    client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": greet},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )

    print(response.choices[0].message.content)

def load_and_chunk_vcd_data(vcd_file_path: str):
    vcd = VCDVCD(vcd_file_path)
    documents = []
    print(vcd.signals)
    for signal_name in vcd.signals:
        if signal_name == 'hw_top.dut.u_hdcom28_top.cpu_core.instr_addr_o' : 
            print(vcd[signal_name])
        signal_content = json.dumps([{"time": x[0], "value": x[1]} for x in vcd[signal_name].tv], indent=2)

        doc = Document(
            page_content=f"signal_name: {signal_name}, signal_content: {signal_content}",
            metadata={"source": vcd_file_path, "signal_name": signal_name}
        )
        documents.append(doc)
    return documents

def setup_vector_store(documents):
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")

    print("Creating and populating vector database...")

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        collection_name="vcd",
        persist_directory="chroma_data"
    )
    print("Vector database populated.")
    return vectorstore

def setup_rag_chain(vectorstore):
    llm = ChatDeepSeek(
        model=MODEL_NAME,
        # export DEEPSEEK_API_KEY=<api_key>
    )

    # Define the retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10}) # Retrieve top 10 most relevant chunks

    # Define the prompt template for the LLM
    # The `context` variable will be populated by the retrieved documents
    prompt = ChatPromptTemplate.from_template("""
    You are an expert VCD signal analysis assistant. Use the following VCD signal data context to answer the user's question.

    Context:
    {context}

    Question: {input}
    """)

    # Create the document combining chain
    document_chain = create_stuff_documents_chain(llm, prompt)

    # Create the full retrieval chain
    rag_chain = create_retrieval_chain(retriever, document_chain)
    return rag_chain

if __name__ == "__main__":
    
    # documents = load_and_chunk_vcd_data('dump.vcd')
    # setup_vector_store(documents)
    vectorstore = Chroma(
        embedding_function=EMBEDDING_MODEL_NAME, 
        collection_name="vcd", 
        persist_directory="chroma_data"
    )
    rag = setup_rag_chain(vectorstore)

    print("\n--- RAG System Ready ---")

    # prompt = "Please tell me the exact time when the reset rst_ni signal is deasserted"
    prompt = "How does the instr interface work?"

    print("Searching and generating response...\n")
    response = rag.invoke({"input": prompt})

    print("DeepSeek's Answer:")
    print(response["answer"])
    print("\n--- Retrieved Context (for debugging) ---")
    for doc in response["context"]:
        print(f"- Signal: {doc.metadata.get('signal_name', 'N/A')}, Source: {doc.metadata.get('source', 'N/A')}")
        # print(doc.page_content[:200] + "...") # Uncomment to see snippets of retrieved content
    print("-" * 30)
    


