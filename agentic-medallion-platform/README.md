# Prerequisites

1. Install Python
2. Install Ollama
    a. This is an open source tool that helps to download and run LLM models in local
    b. Eg: llama3 is a LLM model given by meta, similar to gpt
3. run: ollama pull llama3.1
4. check ollama list, you should see llama3.1
5. requirement.txt
    a.langgraph - orchestrator. controls the flow and good for decision making. It also represents workflows as graph.
    b.pandas - data processing
    c.numpy - numeric calculations like mean.
    d.langchain - Its a framework. Think of it like a jdbc, jdbc connects java to the database. similarly Langchain connects python to ollama. helps to connect LLM to application and tools/Data/API
    e.langchain community
    f.langchain ollama - connect langchain with ollama model. Pythom cannot understand ollama. with this now python can send prompts to ollama model.
6. create a python virtual environment. cmd: py -3 -m venv venv
    1. why do we need a virtual environment.
    2. if you are working on project A, project B, project A needs pandas 2.1, project B needs 1.0 and if everything installed globally, there will be conflicts on the versions.
    3. Anything you install using pip will be installed only for this project

7. Agents - Think of it like a team lead. It doesn;t know how to read csv, it asks tool to do that.

# Important concepts

What exactly happens when an LLM calls a tool?
 1. LLM is a reasoning engine. It can answer your question. eg: How to read a csv file?
 2. But it can't actually, open your csv, count null values, calculate duplicates rows, query your database.
 3. when you say, analyze sales.csv, it doesn't know where the csv file exists, null values, counts, duplcates etc..
 4. It requires tool
 5. A tool is simply a python function that the agent is alowed to use.
 6. eg def count_rows(file_path):
            df = pd.read_csv(file_path)
            return len(df)
7. This function is a tool. This gives LLM a capability that it can count row in a csv.

### Agent State

1. An agent needs memory during execution.
2. Then agent needs to remember file path, schema, quality, final report.
3. This is called Agent State.

### Nodes

1. A node is a step in workflow. Its simply a python function

### Tools

1. Python function

### LLM

1. LLM decides. Example " I need schema information" , calls python function -> get results -> explains findings

