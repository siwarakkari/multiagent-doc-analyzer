import getpass
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from prompt import retrieval_qa_chat_prompt
from agent_regestry import BaseAgent
from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from worker.worker import VectorStoreIndexer
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate


load_dotenv() 
if not os.environ.get("MISTRAL_API_KEY"):
  os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter API key for Mistral AI: ")


class RAGAgent(BaseAgent):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        Indexer=VectorStoreIndexer()
        self.vectorstore = Indexer.vector_db
        self.llm = init_chat_model("mistral-small-latest", model_provider="mistralai")

        rag_prompt = PromptTemplate(
        input_variables=["context","input"],
        template=retrieval_qa_chat_prompt
    )
       
        combine_docs_chain = create_stuff_documents_chain(self.llm, rag_prompt)
        self.qa_chain = create_retrieval_chain(self.vectorstore.as_retriever(), combine_docs_chain)

    def run(self, query: str):
        result = self.qa_chain.invoke({"input": query})
        print(result)
        response = result.get("answer")
        source_documents = result.get("context", [])
        print(type(source_documents))
        references = []
        for doc in source_documents:
            metadata = doc.metadata
            source = metadata.get("source", "N/A")
            page_number = metadata.get("page_number", "N/A")
            references.append(f"Source: {source}, Page: {page_number}")
        return {"response": response, "references": references}
