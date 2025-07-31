import getpass
import os
from langchain.prompts import PromptTemplate
from agent_regestry import AgentRegistry, BaseAgent
from langchain.chat_models import init_chat_model
from prompt import supervisor_prompt


from dotenv import load_dotenv
load_dotenv() 
if not os.getenv("MISTRAL_API_KEY"):
  os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter API key for Mistral AI: ")

class SupervisorAgent(BaseAgent):
    def __init__(self, name: str, description: str, agent_registry: AgentRegistry):
        super().__init__(name, description)
        self.agent_registry = agent_registry
        self.llm = init_chat_model("mistral-small-latest", model_provider="mistralai")
        self.routing_prompt = PromptTemplate(
            template=supervisor_prompt,
            input_variables=["agent_names", "query"]
        )
        self.routing_chain = self.routing_prompt | self.llm

    def run(self, query: str):
        agent_names = ", ".join(self.agent_registry.list_agents())
        selected_agent_name = self.routing_chain.invoke({"agent_names": agent_names, "query": query})
        print(selected_agent_name)
        
        try:
            selected_agent = self.agent_registry.get_agent(selected_agent_name.content)
            print(f"Routing query to {selected_agent.name}")
            return selected_agent.run(query)
        except ValueError as e:
            return f"Error: {e}. Could not route query to an agent. Please try again with a more specific query."

