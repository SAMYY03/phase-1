class Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def describe(self) -> str:
        return f"Agent {self.name} handles {self.role}"


agent1 = Agent("SearchAgent", "Document Retrieval")
agent2 = Agent("DBAgent", "Database Operations")

print(agent1.describe())
print(agent2.describe())
