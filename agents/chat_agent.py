import getpass
import os
from agent_regestry import BaseAgent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv() 
if not os.getenv("MISTRAL_API_KEY"):
  os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter API key for Mistral AI: ")


class ChatAgent(BaseAgent):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.llm = init_chat_model("mistral-small-latest", model_provider="mistralai")

    def run(self, query: str):
        return self.llm.invoke("Respond the following query:{query}")
    

