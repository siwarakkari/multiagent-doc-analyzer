

from RAG_agent import RAGAgent
from agent_regestry import AgentRegistry
from chat_agent import ChatAgent
from summary_agent import SummarizationAgent
from supervisor import SupervisorAgent



if __name__ == "__main__":
   
    # 2. Instantiate agents
    rag_agent = RAGAgent("RAGAgent", "Answers questions based on retrieved documents.")
    chat_agent = ChatAgent("ChatAgent", "Engages in general conversation.")
    summarization_agent = SummarizationAgent("SummarizationAgent", "Summarizes provided text.")

    # 3. Register agents
    registry = AgentRegistry()
    registry.register_agent(rag_agent)
    registry.register_agent(chat_agent)
    registry.register_agent(summarization_agent)

    # 4. Instantiate the supervisor
    supervisor = SupervisorAgent("SupervisorAgent", "Routes queries to appropriate agents.", registry)

    # 5. Test the system
    print("\n--- Testing RAG Agent ---")
    rag_query = "What is Time management?"
    rag_response = supervisor.run(rag_query)
    print(f"Query: {rag_query}")
    print(f"Response: {rag_response['response']}")
    print(f"References: {rag_response['references']}")

    print("==="*40)

    print("\n--- Testing Chat Agent ---")
    chat_query = "Hello, how are you?"
    chat_response = supervisor.run(chat_query)
    print(f"Query: {chat_query}")
    print(f"Response: {chat_response.content}")

    print("==="*40)

    print("\n--- Testing Summarization Agent ---")
    summarize_text = "Artificial intelligence (AI) is intelligence—perceiving, synthesizing, and inferring information—demonstrated by machines, as opposed to intelligence displayed by animals and humans. AI research has been defined as the field of study that develops and studies intelligent agents. An intelligent agent is any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals. Colloquially, the term \"artificial intelligence\" is often used to describe machines (or computers) that mimic \"cognitive\" functions that humans associate with the human mind, such as \"learning\" and \"problem solving\"."
    summarization_response = supervisor.run(f"Summarize the following: {summarize_text}")
    print(f"Query: Summarize the provided text.")
    print(f"Response: {summarization_response.content}")

    print("==="*40)

    print("\n--- Testing a query that should fail routing ---")
    fail_query = "This query should not be routed."
    fail_response = supervisor.run(fail_query)
    print(f"Query: {fail_query}")
    print(f"Response: {fail_response}")

    print("==="*40)
