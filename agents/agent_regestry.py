import abc

class BaseAgent(abc.ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abc.abstractmethod
    def run(self, *args, **kwargs):
        pass

class AgentRegistry:
    def __init__(self):
        self._agents = {}

    def register_agent(self, agent: BaseAgent):
        if not isinstance(agent, BaseAgent):
            raise TypeError("Only instances of BaseAgent can be registered.")
        self._agents[agent.name] = agent

    def get_agent(self, name: str) -> BaseAgent:
        agent = self._agents.get(name)
        if not agent:
            raise ValueError(f"Agent '{name}' not found in registry.")
        return agent

    def list_agents(self):
        return list(self._agents.keys())

