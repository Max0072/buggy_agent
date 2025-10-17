from typing import TypedDict, List, Any
from langgraph.graph import StateGraph, START, END
from code_intepretor import DockerCodeRunner
from prompts import code_fixer_prompt
from code_model import CodingModel


class State(TypedDict, total=False):
    messages: List[Any]
    last_code: str


class CodeDebugAgent:
    def __init__(self):
        self.coding_model = CodingModel()
        self.code_runner = DockerCodeRunner(image="python:3.11-slim")

        self.graph = StateGraph(State)
        self.graph.add_node("agent_fix_code", self._agent_fix_code)
        self.graph.add_edge(START, "agent_fix_code")
        self.graph.add_edge("agent_fix_code", END)
        self.app = self.graph.compile()


    def _agent_fix_code(self, state: State) -> State:
        print("Agent is fixing code...")
        model_inputs = self.coding_model.prepare_model_input(state["messages"])
        model_outputs = self.coding_model.forward(model_inputs)
        return {"messages": [{"role": "assistant", "content": model_outputs}], "last_code": model_outputs}


    def fix_code(self, query):
        prompt = code_fixer_prompt + '\nHere is the data to be analized:'
        for i, j in query.items():
            if i == "task_id":
                continue
            prompt += f"\n{i}: \n\"{j}\""

        result = self.app.invoke({"messages": [{"role": "user", "content": prompt}]},
                                 config={"configurable": {"thread_id": query["task_id"]}})

        return result
