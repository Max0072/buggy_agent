# Code Debug Agent

An automated agent for debugging and fixing bugs in Python code using LLM (Qwen) and LangGraph.

## Description

This project implements an automated code debugging system based on "Qwen3-0.6B" LLM. The agent analyzes buggy code from the HumanEvalPack dataset and generates fixed code. After generation, the code is tested in isolated Docker environment.

## Project Structure

```
buggy_agent/
├── main.py              # Entry point
├── code_agent.py        # LangGraph agent for code fixing
├── code_model.py        # Qwen model wrapper
├── code_intepretor.py   # Docker runner for code execution
├── evaluation.py        # Evaluation system
├── prompts.py           # LLM prompts
└── requirements.txt     # Project dependencies
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the agent


```bash
python main.py
```

## Workflow

1. Load Data: Load HumanEvalPack dataset with buggy code
2. Prepare Prompt: Create prompt with task description, error type, and examples
3. Generate Fixed code: LLM analyzes code and generates fixed version
4. Testing: Fixed code runs with unit tests in Docker
5. Evaluation: Calculate Pass@1 metric and detailed statistics

