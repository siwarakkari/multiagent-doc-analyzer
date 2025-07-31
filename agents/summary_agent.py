import getpass
import os
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from agent_regestry import BaseAgent
from prompt import summarization_prompt
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv() 
if not os.getenv("MISTRAL_API_KEY"):
  os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter API key for Mistral AI: ")


class SummarizationAgent(BaseAgent):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.llm = init_chat_model("mistral-small-latest", model_provider="mistralai")
        self.summarization_prompt = PromptTemplate(
            template=summarization_prompt,
            input_variables=["text"]
        )

    def run(self, text: str):
        # Simple summarization implementation for now
        chain = self.summarization_prompt | self.llm
        return chain.invoke({"text": text})
