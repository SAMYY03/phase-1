# Phase 2 – Multi-Agent Architecture

This document describes the architecture of the Phase 2 Multi-Agent system built using
Semantic Kernel 



## Goal

The goal of this system is to demonstrate:
- Multi-agent orchestration
- Semantic Kernel tool calling
- Event-driven design
- MCP (external system integration)
- Reuse of RAG from Phase 1



## Main Components

### 1. FastAPI (Application Layer)
- Entry point for user interactions
- Exposes `/chat_sk` endpoint
- Forwards user messages to Semantic Kernel



### 2. Semantic Kernel (Orchestration Layer)
- Interprets user intent from natural language
- Automatically selects and calls tools
- Acts as the **orchestrator**



### 3. ManagerToolsPlugin (SK Tools)
Exposes agent capabilities as callable tools:
- `create_task`
- `update_task_status`
- `list_pending_tasks`
- `answer_policy_question`

Semantic Kernel decides when to invoke each tool.



### 4. Agents 

#### TaskDbAgent
- Manages tasks (create, update, list)
- Uses SQLite database
- Publishes events on task changes

#### KnowledgeRagAgent
- Reused from Phase 1
- Answers company policy questions
- Uses embeddings, vector search, and a local LLM

#### McpActionAgent
- Subscribes to task events
- Triggers external notifications



### 5. Event Bus (Core Infrastructure)
- Central event dispatcher
- Enables loose coupling between agents
- Events:
  - `TASK_CREATED`
  - `TASK_UPDATED`



### 6. MCP (External Integration)
- Implements external side effects
- Current integration: Slack notifications
- Triggered automatically via events



## Execution Flow

1. User sends a message to `/chat_sk`
2. Semantic Kernel analyzes intent
3. Appropriate tool is selected
4. Agent executes business logic
5. Event is published
6. MCP subscriber sends Slack notification



## Design Benefits

- Clean separation of concerns
- Easy extensibility (add new agents or tools)
- No hard dependency on external systems
- Production-ready and testable architecture
