# AI Assistant Development Step-by-Step Guide

## Overview

This guide outlines how to build an AI Assistant with a specialized knowledge base using **Python**, **LangChain**, and **FastAPI**. The assistant will leverage two knowledge approaches (JSON and RAG vector search) and a web search API for broad queries. Key features include:

- **Knowledge Base**: 
  - **JSON Lookup** for quick checking if an action or integration exists in ActivePieces (a workflow automation platform).
  - **RAG (Retrieval Augmented Generation)** via a vector database (FAISS) for semantic search (e.g. finding which action can filter data).
- **LLM**: GPT-5 as the main agent model (with flexibility to switch to alternatives like Claude 4 or Google Gemini).
- **Tools/Integrations**: Perplexity API for real-time web search.
- **Memory**: Persistent chat memory so the assistant remembers past conversations.
- **Frontend**: A React + Vite web UI (to be implemented last) for user interaction.

We will build the project in phases, focusing on backend logic first and saving the user interface for the end.

## Step 1: Project Setup

1. **Initialize the Environment**: Create a new Python project and set up a virtual environment. For example:  
   ```bash
   python3 -m venv venv 
   source venv/bin/activate   # On Windows: venv\\Scripts\\activate
   ```  
   Ensure you have Python 3.9+ for compatibility with LangChain and other libraries.

2. **Install Dependencies**: Use `pip` to install the required packages:  
   ```bash
   pip install fastapi uvicorn langchain openai faiss-cpu python-dotenv requests
   ```  
   - **FastAPI** for building the API server.  
   - **Uvicorn** as the ASGI server to run FastAPI.  
   - **LangChain** for building the LLM agent, tools, and chains.  
   - **OpenAI** for accessing GPT-5 (and possibly embeddings).  
   - **faiss-cpu** for the local vector database (FAISS).  
   - **python-dotenv** to load API keys from a `.env` file.  
   - **requests** for calling external APIs (e.g., Perplexity).  
   *(Depending on model usage, you might also install specific SDKs, e.g., `anthropic` for Claude or Google AI libraries. Those can be added when integrating alternative models.)*

3. **Environment Variables**: Create a `.env` file at the project root to store configuration like API keys and model settings. For example:  
   ```ini
   OPENAI_API_KEY=<your OpenAI API key>  
   PERPLEXITY_API_KEY=<your Perplexity API key>  
   MODEL_PROVIDER=openai        # or "anthropic" or "google"  
   MODEL_NAME=gpt-5             # e.g., GPT-5 model name for OpenAI
   ```  
   This keeps sensitive keys out of code. Load this `.env` in your app using `dotenv` at startup.

4. **Project Structure**: Organize the code into modules for clarity. For instance:  
   - `main.py` (or `app.py`): Initialize FastAPI and include route definitions.  
   - `agent.py`: Setup of the LLM agent, tools, and knowledge base loading.  
   - `memory.py`: Utility for chat memory persistence.  
   - `frontend/`: Later, a separate folder for the React Vite frontend app.  

With the environment ready and dependencies installed, you can proceed to build the knowledge base and tools.

## Step 2: Knowledge Base Preparation

### 2.1 JSON Knowledge Base (ActivePieces Data)

First, prepare a structured knowledge base for ActivePieces integrations and actions:

- **Data Collection**: Create a JSON file (e.g., `activepieces_data.json`) that contains the list of available integrations (apps) and their actions/triggers. You might obtain this from ActivePieces documentation or export it from their platform. Structure it in a developer-friendly way, for example:  

  ```json
  {
    "integrations": [
      {
        "name": "Slack",
        "actions": ["Send Message", "Create Channel"],
        "triggers": ["New Message"]
      },
      {
        "name": "Google Sheets",
        "actions": ["Add Row", "Update Row", "Filter Rows"],
        "triggers": ["New Spreadsheet"]
      },
      {
        "name": "Router", 
        "actions": ["Conditional Branch"], 
        "triggers": []
      }
      // ... more integrations
    ]
  }
  ```  

  Include all relevant pieces (including utility ones like **Router/Filter** if they exist as steps).

- **JSON Loading**: In your Python code, load this JSON at startup. For example:  

  ```python
  import json
  with open("activepieces_data.json", "r") as f:
      ap_data = json.load(f)
  integration_list = ap_data["integrations"]
  ```  

- **Lookup Functions**: Implement helper functions to query this data. For instance:
  - `find_integration(name: str) -> dict or None`: Return the integration object if the name matches (allow case-insensitive or partial matches for flexibility).
  - `integration_has_action(integration_name: str, action_name: str) -> bool`: Check if a given action exists under a specific integration.
  - `find_action(action_name: str) -> list of str`: Find which integration(s) have an action with this name (for cases where user asks "Is there an action to do X?").

  These functions will search the `integration_list`. This gives the assistant quick, exact lookup capability. For example, `find_integration("Slack")` should return the Slack object if present, and `find_action("Filter Rows")` might return "Google Sheets" (in our sample data).

- **Usage Example**: If the user asks "Does ActivePieces have a Gmail integration?", the assistant (via a tool we'll set up) can call `find_integration("Gmail")`. If it returns an object, the answer would be "Yes, ActivePieces has a Gmail integration with actions X, Y, Z." If not, "No, there's no native Gmail integration available."

This JSON approach covers direct presence/absence queries. Next, we handle more open-ended queries with semantic search.

### 2.2 Vector Database for Semantic Search (RAG)

For questions like "How can I filter data in ActivePieces?" or "What action should I use to send an email?", we use a **Retrieval Augmented Generation** approach with a vector store:

- **Collect Knowledge Documents**: Gather textual descriptions of actions, integrations, and features:
  - You can create a small **knowledge base docs** by writing descriptions for each integration and key actions. For example, a paragraph about the **Router step** explaining it allows conditional filtering/branching, or a note that **Filter Rows** action exists under Google Sheets for filtering spreadsheet data.
  - If ActivePieces has documentation pages, use those (ensure you have rights if using content). Otherwise, write your own brief explanations.

  Example entries for the knowledge docs:
  - *"Router step: A built-in ActivePieces control flow step that routes data based on conditions. It can be used to filter or branch workflows."*
  - *"Google Sheets - Filter Rows action: Filters spreadsheet rows based on a condition. Useful for data cleaning or conditional processing in a flow."*

- **Embed and Index**: Use **FAISS** (Facebook AI Similarity Search) via LangChain to create a vector store of these documents:
  1. **Embeddings**: Decide on an embedding model. If using OpenAI, you can use `text-embedding-ada-002` via LangChain's `OpenAIEmbeddings`. Alternatively, use a local model from `sentence_transformers` for offline embedding.
  2. **Create Index**: Convert your knowledge texts into `Document` objects (with `page_content` and maybe metadata like a title). Then do:  
     ```python
     from langchain.embeddings import OpenAIEmbeddings
     from langchain.vectorstores import FAISS
     from langchain.docstore.document import Document

     texts = [
       "Router step: A control flow element that filters or branches data based on conditions in ActivePieces.",
       "Slack integration: allows sending messages to Slack channels or DMs via ActivePieces.",
       "Google Sheets 'Filter Rows' action: filters spreadsheet data according to specified criteria.",
       // ... more docs
     ]
     docs = [Document(page_content=t) for t in texts]
     embedding_model = OpenAIEmbeddings()  # uses default OpenAI embedding model
     vector_store = FAISS.from_documents(docs, embedding_model)
     vector_store.save_local("ap_faiss_index")
     ```  
     This will generate embeddings for each text and store them in a FAISS index (saved to disk as `ap_faiss_index` files for persistence).

  3. **Query Function**: Implement a function to query this vector store for relevant info. For example:  
     ```python
     def search_knowledge(query: str, k: int = 2) -> str:
         # Load the index (if not already in memory)
         global vector_store
         if vector_store is None:
             vector_store = FAISS.load_local("ap_faiss_index", embedding_model)
         results = vector_store.similarity_search(query, k=k)
         # Combine or summarize results
         snippets = [res.page_content for res in results]
         return " ".join(snippets)
     ```  
     This returns the content of the top-matching documents. (Later, the LLM will incorporate these snippets to answer the user.)

- **Example**: For the query "How do I branch a workflow based on a condition?", `search_knowledge` might return a snippet about the "Router step", which the LLM can use to answer: "You can use the **Router** step to branch the workflow based on conditions."

By setting up this vector-based knowledge retrieval, the assistant can handle fuzzy or conceptual queries by pulling relevant context.

## Step 3: Language Model and Tool Setup

Now integrate the language model and set up tools for the agent to use the knowledge base:

- **LLM Initialization**: Use LangChain to initialize the GPT-5 model. For example:  
  ```python
  import os
  from langchain.llms import OpenAI
  model_name = os.getenv("MODEL_NAME", "gpt-5")  
  llm = OpenAI(model_name=model_name, temperature=0.2)
  ```  
  This assumes GPT-5 is accessible via OpenAI API. Adjust parameters (like `temperature`) as needed. The `MODEL_NAME` and `MODEL_PROVIDER` from the .env will determine if you use `OpenAI`, `Anthropic`, etc. For instance:  
  ```python
  provider = os.getenv("MODEL_PROVIDER", "openai")
  if provider == "openai":
      llm = OpenAI(model_name=model_name, temperature=0.2)
  elif provider == "anthropic":
      from langchain.llms import Anthropic
      llm = Anthropic(model=model_name)  # e.g., model_name could be "claude-v4"
  elif provider == "google":
      # Google Gemini hypothetical integration (use appropriate SDK if available)
      llm = SomeGoogleLLM(model=model_name)
  ```  
  Encapsulate this in a function or just run once at startup. This design allows switching the backend LLM by changing env variables.

- **Define Tools**: We will create three main tools for the agent:
  1. **Integration Checker (JSON lookup)** – to verify if an integration or action exists in ActivePieces.
  2. **Knowledge Search (Vector DB)** – to retrieve info for "how to" questions from the FAISS index.
  3. **Web Search (Perplexity)** – to fetch answers from the web for general queries.

  Using LangChain's tool interface, you can wrap Python functions as tools. We can use the `@tool` decorator or `Tool` class. Each tool needs a name and a description so the agent knows when to use it.

  - **Tool 1: Check Integration/Action**  
    Define a function that uses the JSON data from Step 2.1. For example:  
    ```python
    from langchain.agents import tool

    @tool("check_activepieces", return_direct=True)
    def check_activepieces(query: str) -> str:
        """Check if an integration or action exists in ActivePieces and return details."""
        name = query.strip().lower()
        # Try finding integration by name
        result = find_integration(name)  # uses the helper from Step 2.1
        if result:
            actions = ", ".join(result.get("actions", []))
            return f"Yes, ActivePieces has '{result['name']}' integration. Actions include: {actions}."
        # If no integration, try finding an action
        found_actions = find_action(name)
        if found_actions:
            # found_actions could be a list of integration names that have this action
            return f"ActivePieces has an action '{query}' under: " + ", ".join(found_actions) + "."
        return f"No, '{query}' is not available as a built-in integration or action in ActivePieces."
    ```  
    This tool will allow the agent to answer direct availability questions. We set `return_direct=True` so that if this tool is used, the agent can directly return the result to the user without additional formatting (since the function already provides a complete answer).

    *Description*: Provide a concise description for the tool (via docstring or explicit parameter) such as: *"Use this tool to check if a given app integration or action exists in ActivePieces."*

  - **Tool 2: Search Knowledge Base**  
    This tool uses the vector store:  
    ```python
    @tool("search_activepieces_docs")
    def search_activepieces_docs(query: str) -> str:
        """Search the ActivePieces knowledge base for relevant info."""
        answer = search_knowledge(query)  # uses the function from Step 2.2
        return answer or "No relevant info found in knowledge base."
    ```  
    This returns raw snippets from the stored docs. The LLM will read these and incorporate them into its answer. In this case, we usually **do not** use `return_direct=True` because we expect the LLM to elaborate on the info rather than just parroting the snippet. The description could be: *"Use this tool to find information in the ActivePieces documentation (actions, integrations, usage) related to the query."*

  - **Tool 3: Web Search (Perplexity API)**  
    Implement a tool that calls the Perplexity Search API. We use the `requests` library to query the API. For example:  
    ```python
    import requests

    @tool("web_search")
    def web_search(query: str) -> str:
        """Search the web for current information (via Perplexity API)."""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            return "Error: No Perplexity API key provided."
        url = "https://api.perplexity.ai/search"  # hypothetical endpoint
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {"q": query}
        try:
            res = requests.get(url, headers=headers, params=params, timeout=5)
            data = res.json()
        except Exception as e:
            return f"Web search error: {e}"
        # Parse the response to get a useful snippet
        # (Assume data contains a list of results with 'snippet' or an 'answer' field)
        if "answer" in data:
            return data["answer"]
        results = data.get("results") or []
        if results:
            snippet = results[0].get("snippet") or results[0].get("text") or ""
            return snippet[:500]  # return first 500 chars of the top result
        return "No results found."
    ```  
    *Description*: "Use this tool to search the web for answers when the information is not in the ActivePieces knowledge base."

    Make sure to handle API errors or timeouts so the assistant doesn't hang. The Perplexity API might return a structured response; adjust parsing accordingly (the above is a generic example).

- **Tool Registration**: After defining these functions, compile them into a list for the agent. For example:  
  ```python
  tools = [check_activepieces, search_activepieces_docs, web_search]
  ```  
  (If not using the `@tool` decorator, you can also create tools via `Tool.from_function(...)` with name and description.)

At this stage, we have our **LLM** and our **tools** ready. Next, we'll create the agent that uses them.

## Step 4: Agent and Memory Setup

With the LLM and tools available, configure a LangChain agent to drive the conversation:

- **Agent Initialization**: Use `initialize_agent` from LangChain to create an agent that can use the tools. We will use a conversational agent type since we want it to handle multi-turn dialogue. For example:  
  ```python
  from langchain.agents import initialize_agent, AgentType

  agent = initialize_agent(
      tools, 
      llm, 
      agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
      verbose=True
  )
  ```  
  Here, `CHAT_ZERO_SHOT_REACT_DESCRIPTION` is an agent type that works well with chat models and can decide which tool to use based on the tool descriptions (following a ReAct style reasoning). We set `verbose=True` to see the thought process and tool usage during development (you can turn this off in production).

- **Customizing Agent Behavior**: You can provide a custom system prompt or prefix to guide the agent. For instance, instruct it that it is an expert on ActivePieces and should use the tools for certain types of queries. LangChain allows specifying a `agent_kwargs={"prefix": ..., "format_instructions": ...}` if needed. Example prefix system message:  
  *"You are an AI assistant helping with ActivePieces (an automation platform). You have access to these tools: (1) check_activepieces for verifying integrations/actions, (2) search_activepieces_docs for internal knowledge, (3) web_search for external info. Use them whenever appropriate to give accurate, helpful answers. If a question is about whether something exists in ActivePieces, use the check tool. If it's about how to do something or what action to use, search the docs. For anything else or if unsure, try a web search. Respond in a clear and concise manner."*  
  This primes the agent on how to use the tools. LangChain's standard agent may already infer this from tool descriptions, but an explicit instruction can improve reliability.

- **Conversation Memory**: To maintain context across multiple turns, integrate memory into the agent. LangChain chat agents can incorporate `ConversationBufferMemory` or similar. For example:  
  ```python
  from langchain.memory import ConversationBufferMemory
  memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
  agent.memory = memory
  ```  
  Now the agent will store the conversation in `memory.chat_history`. The `return_messages=True` flag ensures that for chat models, memory is handled as a list of messages rather than a big string (LangChain best practice for chat models).

- **Memory in Agent Chain**: If `initialize_agent` does not directly accept a memory argument (depending on LangChain version), you might instead use `AgentExecutor` or manually manage the chain. One approach: use a **ConversationalRetrievalChain** for RAG, but since we have multiple tools, sticking with a full agent is fine. In any case, ensure that when you call the agent for each input, it has access to the `memory` so that previous Q&As are considered.

At this point, the agent can use tools and maintain context in memory. Next, we address how to persist this memory beyond runtime.

## Step 5: Persisting Chat Memory

By default, `ConversationBufferMemory` resides in memory (RAM) and will reset if the process restarts. To make the chat history persistent across sessions or server restarts, implement a simple persistence layer:

- **In-Memory to Disk**: Each time the conversation updates (user asks something, assistant answers), append these entries to a file or database:
  - The simplest approach is a text file or JSON file. For example, maintain a `chat_history.json` array where each element is `{"role": "user", "message": "..."}` or `{"role": "assistant", "message": "..."}`.
  - After each response, open the file in append mode (or keep it open) and write the latest interaction.

- **Loading at Startup**: When the app starts, check if a history file exists. If yes, load it and insert those messages into the `ConversationBufferMemory`. For instance:  
  ```python
  import os, json
  history_file = "chat_history.json"
  if os.path.exists(history_file):
      with open(history_file, "r") as f:
          past_messages = json.load(f)
      for msg in past_messages:
          if msg["role"] == "user":
              memory.save_context({"input": msg["message"]}, {"output": ""})
          elif msg["role"] == "assistant":
              # The save_context method in LangChain expects both input and output; 
              # to save assistant messages alone, you might need to adapt or use memory.chat_memory.add_message()
              pass
  ```  
  A simpler approach might be to log the conversation separately and not attempt to preload memory on startup, unless you explicitly want the assistant to recall past sessions. Another approach is to use a database (like SQLite or TinyDB) keyed by a session ID for multiple users, but if it's a single-user personal assistant, a single log is fine.

- **Alternate Approach**: Use LangChain's built-in mechanisms like `ConversationTokenBufferMemory` with a `chat_memory` backed by a persistent store. For example, `ConversationBufferMemory` can take a `chat_memory` argument that could be an instance of `FileChatMessageHistory` (LangChain has a file-based message history class). This would handle reading/writing automatically. Example:  
  ```python
  from langchain.chat_models import ChatMessageHistory
  history = ChatMessageHistory(file_path="chat_history.txt")
  memory = ConversationBufferMemory(chat_memory=history, return_messages=True)
  ```  
  This way LangChain appends new messages to `chat_history.txt` under the hood.

- **Memory Limits**: Be mindful of memory growth. If the chat history grows very long, interactions might slow down or context window limits could be reached. In a production scenario, implement a strategy to summarize or truncate old memory. For now, a simple persistent log is sufficient.

By persisting memory, the assistant will not lose past conversation context even if you restart the server or refresh the client (assuming you reload that history).

## Step 6: FastAPI Backend Implementation

Now, tie everything together in a FastAPI app that exposes an endpoint for the chat:

1. **FastAPI App Initialization**: In `main.py`, create a FastAPI instance:  
   ```python
   from fastapi import FastAPI
   app = FastAPI()
   ```  
   When the app starts (you can use the `@app.on_event("startup")` decorator or just run at global scope), perform initializations:
   - Load environment variables (`dotenv.load_dotenv()`).
   - Load the ActivePieces JSON data (Step 2.1).
   - Load or build the FAISS index (Step 2.2):
     - If you saved the index to disk, load it with `FAISS.load_local("ap_faiss_index", embedding_model)`.
     - If not, call the code to create it. Make sure `embedding_model` is initialized (this might call OpenAI embeddings API once for each document if not cached).
   - Initialize the LLM (GPT-5 or chosen model) and the tools, then create the agent (Steps 3 & 4).
   - Attach the memory (if not already attached when creating the agent).
   - If you have a persistent history from previous sessions, load it into memory as discussed.

2. **Define API Endpoint**: Create an endpoint to handle incoming messages. A typical design is a POST request to `/chat` with JSON body containing the user's message (and maybe a session id if needed). For example:  
   ```python
   from pydantic import BaseModel

   class UserMessage(BaseModel):
       message: str

   @app.post("/chat")
   async def chat_endpoint(user_msg: UserMessage):
       user_input = user_msg.message
       # Run the agent to get a response
       try:
           assistant_reply = agent.run(user_input)
       except Exception as e:
           # In case of errors (tool failure, etc.), handle gracefully
           return {"error": str(e)}
       # Persist the interaction (append to history file)
       log_interaction(user_input, assistant_reply)  # define this to save to file
       return {"reply": assistant_reply}
   ```  

   This function takes the user message, feeds it to the agent (which internally uses the LLM and tools to produce an answer), then returns the assistant's reply. The `log_interaction` should append the `user_input` and `assistant_reply` to the persistent history (and you might have already stored it in memory via LangChain automatically).

3. **Additional Endpoints**: You may add other routes as needed:
   - A GET to `/` or `/health` returning "OK" (useful for testing if the server is up).
   - A POST to `/reset` to clear the conversation (both in memory and in the persistent store). This can simply reinitialize the `ConversationBufferMemory` and truncate the history file.

4. **Run the Server**: Use Uvicorn to run your app. For example, if `main.py` contains the app, run:  
   ```bash
   uvicorn main:app --reload
   ```  
   (The `--reload` flag is useful during development to auto-restart on code changes.)

5. **Testing via API**: While the server is running, test it with curl or a REST client:  
   - `curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message": "Hello"}'`  
   Expect a JSON response like `{"reply": "Hello! How can I assist you today?"}` (the exact reply depends on the LLM and prompt).  
   - Try asking a known integration: `{"message": "Is there a Google Sheets integration?"}`. The assistant should respond confirming it (likely using the check_activepieces tool).  
   - Try a semantic question: `{"message": "How can I send an email using ActivePieces?"}`. Ideally, the assistant will use the knowledge base and reply with something about an email integration or SMTP piece.  
   - If something is not working (e.g., the agent not using tools correctly), adjust the tool descriptions or the system prompt.

At this point, the backend (brain of the assistant) is complete and running. Now it's time to create a user-friendly interface.

## Step 7: Frontend UI with React (Vite)

For the user interface, we'll make a simple web chat client using **React** and **Vite**:

1. **Bootstrap the Project**: If you haven't already, create a new Vite React project:  
   ```bash
   npm create vite@latest my-assistant-ui -- --template react
   cd my-assistant-ui
   npm install    # install dependencies
   npm install axios  # or you can use fetch; axios is optional
   ```  
   This sets up a basic React project.

2. **Chat Interface Component**: Design a component (say, `Chat.jsx`) that manages the state of the conversation and renders the UI:
   - State variables: `messages` (an array of `{sender: "user"|"assistant", text: "..."}` objects), and `currentInput` (the text currently typed by the user).
   - JSX Structure: 
     - A scrollable div or list that displays each message (style user vs assistant messages differently for clarity).
     - An input box and send button at the bottom.
   - Example layout (JSX pseudo-code):  
     ```jsx
     <div className="chat-window">
       <div className="messages">
         {messages.map((msg, idx) => (
           <div key={idx} className={`message ${msg.sender}`}>
             <b>{msg.sender}:</b> {msg.text}
           </div>
         ))}
       </div>
       <div className="input-area">
         <input 
           type="text" 
           value={currentInput} 
           onChange={e => setCurrentInput(e.target.value)} 
           onKeyDown={handleKeyDown} // to send on Enter
         />
         <button onClick={sendMessage}>Send</button>
       </div>
     </div>
     ```  
     Add basic CSS to distinguish user vs assistant messages (different background color, alignment to left/right, etc.).

3. **Handling User Input**: Implement the `sendMessage` function (and pressing Enter handler):
   - When the user sends a message, first add the user message to `messages` state for immediate feedback.
   - Send a POST request to the FastAPI `/chat` endpoint with the user message. You can use `fetch` or `axios` for this. Example with `fetch`:  
     ```js
     async function sendMessage() {
       if (!currentInput) return;
       const userText = currentInput;
       setMessages([...messages, { sender: "user", text: userText }]);
       setCurrentInput("");  // clear input field
       try {
         const res = await fetch("http://localhost:8000/chat", {
           method: "POST",
           headers: { "Content-Type": "application/json" },
           body: JSON.stringify({ message: userText })
         });
         const data = await res.json();
         if (data.reply) {
           setMessages(prev => [...prev, { sender: "assistant", text: data.reply }]);
         } else if (data.error) {
           // handle error response
           setMessages(prev => [...prev, { sender: "assistant", text: "Error: " + data.error }]);
         }
       } catch (err) {
         setMessages(prev => [...prev, { sender: "assistant", text: "Network error, please try again." }]);
       }
     }
     ```  
     Ensure you handle errors gracefully (network issues or server errors) so that the UI doesn't freeze.

   - Also implement `handleKeyDown` to call `sendMessage` when the Enter key is pressed.

4. **CORS and Configuration**: By default, your React app (likely running on port 5173) will make requests to `localhost:8000`. In the FastAPI backend, enable CORS so that the browser can call the API:  
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```  
   Adjust the origin as needed (for development, you can allow all origins). This should be added before defining routes.

   Also, consider putting the API base URL in a config for the React app. In a production build, the frontend might be served from the same domain as the API, but during dev it's separate.

5. **Run and Test UI**: Start the React dev server (`npm run dev`) and open the app in your browser. Test sending messages:
   - The assistant should respond and each turn should appear in the chat window.
   - Try multi-turn interactions to see that the assistant remembers context (ask a follow-up question, etc.).
   - If the assistant seems to forget, check that the backend memory is working (the `messages` state in React is separate from backend memory; the backend memory ensures the *assistant* remembers, while the React state just displays conversation).

6. **UI Polish**: As needed, add features like:
   - Loading indicator (e.g., show "Assistant is typing..." while waiting for response).
   - Scroll to bottom when new messages appear.
   - Clear chat button (which could call the `/reset` endpoint to clear backend memory and UI state).
   - Responsive design considerations (if you plan to use it on mobile).

With the UI in place, you have a complete system: the user types into the web app, the request goes to FastAPI, the agent processes using LLM + tools, and the response is shown back in the UI.

## Conclusion and Next Steps

By following these steps, you've built a robust AI assistant with the following architecture:

- **Backend**: Python FastAPI app with a LangChain-powered agent (GPT-5 as the core) that uses:
  - JSON knowledge base for quick factual checks about ActivePieces integrations/actions.
  - FAISS vector store for semantic search (enabling RAG for "how-to" questions).
  - External web search via Perplexity API for open-domain queries.
  - A conversation memory that persists across sessions.

- **Frontend**: React/Vite application providing a chat interface for user interaction.

This system can be extended and improved in many ways. Some next steps or enhancements you might consider:

- **Alternate Models**: Implement the logic to switch between GPT-5, Claude 4, or Google Gemini based on availability or query type. For instance, you could route more creative tasks to one model and factual tasks to another, or simply allow a config switch as we set up.
- **ActivePieces Integration**: If ActivePieces has its own API or SDK, you could integrate that for live queries (for example, actually execute a sample workflow or fetch real-time info about pieces).
- **More Tools**: Add tools for other functionalities (e.g., a calculator, date/time info, etc.) if needed for your use cases.
- **Logging and Monitoring**: Implement logging for the agent's actions and decisions. This helps in debugging when the agent chooses an incorrect tool or gives a wrong answer.
- **Error Handling**: Enhance the agent’s ability to handle when a tool fails or returns nothing (perhaps have it try an alternative approach).
- **UI Enhancements**: Improve the chat UI with better styling, chat avatars, markdown support for assistant responses, etc. Perhaps add the ability to upload files or images if your assistant will handle those.
- **Performance**: If using large models like GPT-5, consider streaming responses for a better user experience (FastAPI can stream the response chunk by chunk, and the frontend can render as it comes in, simulating real-time typing).

By iterating on these steps, you can refine the assistant into a powerful tool. Good luck with building your AI assistant! Let the assistant (via Cursor) now proceed to implement the code following this guide, building the project block by block.
