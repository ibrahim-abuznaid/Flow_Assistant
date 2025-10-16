"""
Planning layer for analyzing user queries and generating execution plans.
Uses GPT-5 (o1) for advanced reasoning and query interpretation.
"""
import os
import json
import re
from collections import OrderedDict
from copy import deepcopy
from threading import Lock
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class QueryPlanner:
    """
    Query planner that uses GPT-5 (gpt-5-thinking) to analyze user queries and generate
    clear, actionable plans for the agent to execute.
    """
    SIMPLE_LOOKUP_KEYWORDS = (
        "available",
        "exist",
        "exists",
        "support",
        "supported",
        "have",
        "integration",
        "piece",
        "trigger",
        "action",
        "connector",
    )
    SIMPLE_LOOKUP_VERBS = ("is", "does", "do", "can", "are", "was")
    DETAIL_KEYWORDS = (
        "input",
        "field",
        "property",
        "parameter",
        "configuration",
        "configure",
        "setup",
        "set up",
        "mapping",
        "settings",
    )
    ACTION_TERMS = ("action", "trigger", "step", "task", "piece")
    MAX_SIMPLE_LOOKUP_LENGTH = 140
    MAX_DETAIL_LOOKUP_LENGTH = 260
    CACHE_DEFAULT_SIZE = 64
    
    def __init__(self, model: str = "gpt-5-mini"):
        """
        Initialize the planner with GPT-5 model.
        
        Args:
            model: Model to use ('gpt-5', 'gpt-5-mini', or 'gpt-5-nano')
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self._cache_maxsize = int(os.getenv("PLANNER_CACHE_MAXSIZE", self.CACHE_DEFAULT_SIZE))
        self._plan_cache: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
        self._cache_lock = Lock()
        print(f"✓ Planner initialized with GPT-5 model: {model}")
    
    def _clone_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        return deepcopy(plan)
    
    def _get_cached_plan(self, cache_key: str) -> Optional[Dict[str, Any]]:
        with self._cache_lock:
            cached = self._plan_cache.get(cache_key)
            if cached is None:
                return None
            self._plan_cache.move_to_end(cache_key)
            return self._clone_plan(cached)
    
    def _store_plan(self, cache_key: str, plan: Dict[str, Any]) -> None:
        with self._cache_lock:
            self._plan_cache[cache_key] = self._clone_plan(plan)
            self._plan_cache.move_to_end(cache_key)
            if len(self._plan_cache) > self._cache_maxsize:
                self._plan_cache.popitem(last=False)
    
    def _looks_like_simple_lookup(self, query_lower: str) -> bool:
        if len(query_lower) > self.MAX_SIMPLE_LOOKUP_LENGTH:
            return False
        if any(keyword in query_lower for keyword in self.SIMPLE_LOOKUP_KEYWORDS):
            return True
        if query_lower.endswith("?") and query_lower.split("?")[0].count(" ") <= 8:
            return True
        return any(query_lower.startswith(verb + " ") for verb in self.SIMPLE_LOOKUP_VERBS)
    
    def _create_simple_lookup_plan(self, user_query: str) -> Dict[str, Any]:
        normalized = user_query.strip()
        return {
            "intent": f"Verify if '{normalized}' is available in ActivePieces",
            "query_type": "simple_check",
            "action_plan": [
                "Step 1: Call check_activepieces once using the exact query. SUCCESS = piece/action/trigger details returned. MAX ATTEMPTS = 1",
                "Step 2: If a result is found, summarize the key info (name, description, count of actions/triggers) and STOP immediately after responding.",
                "Step 3: If nothing is found, inform the user it's unavailable and suggest using HTTP request/webhook as alternatives."
            ],
            "recommended_tools": ["check_activepieces"],
            "search_queries": [normalized],
            "max_tool_calls": 1,
            "stopping_condition": "After a single check_activepieces call, respond with the findings or state that it is unavailable.",
            "fallback_strategy": "If the database lookup fails, explain the issue and suggest manually checking the ActivePieces UI.",
            "context": "Auto-generated fast path plan (no LLM planning call)."
        }
    
    def _looks_like_detail_lookup(self, query_lower: str) -> bool:
        if len(query_lower) > self.MAX_DETAIL_LOOKUP_LENGTH:
            return False
        if not any(keyword in query_lower for keyword in self.DETAIL_KEYWORDS):
            return False
        return any(term in query_lower for term in self.ACTION_TERMS)
    
    def _create_detail_lookup_plan(self, user_query: str) -> Dict[str, Any]:
        normalized = user_query.strip()
        return {
            "intent": f"Gather configuration details for '{normalized}'",
            "query_type": "configuration",
            "action_plan": [
                "Step 1: Use search_activepieces_docs once with the query. SUCCESS = list all input properties with types and requirements. MAX ATTEMPTS = 1",
                "Step 2: Summarize required/optional fields, types, and notable defaults. STOP immediately after summarizing.",
                "Step 3: If details remain unclear, note the gaps and recommend checking the ActivePieces UI."
            ],
            "recommended_tools": ["search_activepieces_docs"],
            "search_queries": [normalized],
            "max_tool_calls": 1,
            "stopping_condition": "After one documentation search call, respond with the gathered details (or note missing info).",
            "fallback_strategy": "If doc search fails, provide general guidance using known best practices and suggest checking the UI.",
            "context": "Auto-generated fast path plan for configuration-style queries."
        }
    
    def _build_fast_plan(self, user_query: str) -> Optional[Dict[str, Any]]:
        normalized = user_query.strip()
        if not normalized:
            return None
        lowered = normalized.lower()
        if self._looks_like_simple_lookup(lowered):
            return self._create_simple_lookup_plan(normalized)
        if self._looks_like_detail_lookup(lowered):
            return self._create_detail_lookup_plan(normalized)
        return None
    
    def analyze_query(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze user query and generate an execution plan.
        
        Args:
            user_query: The user's input query
            
        Returns:
            Dictionary containing:
                - intent: The user's primary intent
                - query_type: Type of query (simple_check, flow_building, explanation, etc.)
                - action_plan: Step-by-step plan for the agent
                - recommended_tools: Tools the agent should use
                - context: Additional context for the agent
        """
        
        normalized_query = (user_query or "").strip()

        if not normalized_query:
            fallback = self._create_fallback_plan(user_query)
            return fallback

        cache_key = f"{self.model}:{normalized_query.lower()}"

        cached_plan = self._get_cached_plan(cache_key)
        if cached_plan:
            print("⚡ Planner cache hit (reuse)")
            return cached_plan

        fast_plan = self._build_fast_plan(normalized_query)
        if fast_plan:
            print("⚡ Planner fast-path used (no LLM call)")
            self._store_plan(cache_key, fast_plan)
            return self._clone_plan(fast_plan)

        planning_prompt = f"""You are a query analyzer for an ActivePieces AI assistant. Your role is to analyze user queries and create CLEAR, SPECIFIC, and EFFICIENT plans that prevent the agent from getting stuck or making redundant searches.

ActivePieces is a workflow automation platform (like Zapier). The assistant has these capabilities:
- Knowledge base of 433 pieces (integrations)
- 2,681 actions and 694 triggers
- Tools: check_activepieces (database search), search_activepieces_docs (semantic search), web_search (general info)

CRITICAL PLANNING RULES:
1. Each step must have a CLEAR SUCCESS CRITERION - when to move to next step
2. Specify MAXIMUM tool calls per step (usually 1-2)
3. Define what "good enough" information looks like
4. Add fallback actions if a tool fails
5. Tell agent explicitly when to STOP and respond

Analyze this user query and provide a structured plan:
"{normalized_query}"

You must respond in this exact JSON format:
{{
  "intent": "brief description of what user wants",
  "query_type": "simple_check|flow_building|explanation|troubleshooting|configuration",
  "action_plan": [
    "step 1: SPECIFIC action with SUCCESS CRITERION and MAX ATTEMPTS",
    "step 2: SPECIFIC action with SUCCESS CRITERION and MAX ATTEMPTS",
    ...
  ],
  "recommended_tools": ["tool1", "tool2"],
  "search_queries": ["specific query 1", "specific query 2"],
  "max_tool_calls": 3,
  "stopping_condition": "clear condition that tells agent when it has enough info to respond",
  "fallback_strategy": "what to do if tools fail or return incomplete data",
  "context": "any additional context or considerations"
}}

Examples:

Query: "Is Gmail available in ActivePieces?"
{{
  "intent": "Check if Gmail integration exists",
  "query_type": "simple_check",
  "action_plan": [
    "Step 1: Use check_activepieces('Gmail') ONCE. SUCCESS = piece found with name and basic info. MAX ATTEMPTS = 1",
    "Step 2: If found, immediately respond with piece name, description, and count of actions/triggers. STOP after responding.",
    "Step 3: If NOT found in step 1, respond immediately that it doesn't exist. STOP."
  ],
  "recommended_tools": ["check_activepieces"],
  "search_queries": ["Gmail"],
  "max_tool_calls": 1,
  "stopping_condition": "After 1 check_activepieces call, you have enough info to answer. Do NOT search docs unless explicitly asked.",
  "fallback_strategy": "If database fails, respond that you cannot verify but suggest user check ActivePieces directly.",
  "context": "Simple existence check. ONE tool call maximum. Respond immediately after."
}}

Query: "I want to send an email when a new file is added to Google Drive"
{{
  "intent": "Build a workflow that triggers on new Google Drive file and sends an email",
  "query_type": "flow_building",
  "action_plan": [
    "Step 1: Search 'Google Drive new file trigger input properties' ONCE in docs. SUCCESS = found trigger name + required inputs. MAX ATTEMPTS = 1",
    "Step 2: Search 'send email action input properties' ONCE in docs. SUCCESS = found action name + required inputs (to, subject, body). MAX ATTEMPTS = 1",
    "Step 3: STOP after 2 searches. Compile the information into a clear flow: Trigger Setup → Action Setup with ALL inputs listed.",
    "Step 4: If any search returns incomplete data, use what you have and note what's missing. Do NOT repeat searches."
  ],
  "recommended_tools": ["search_activepieces_docs"],
  "search_queries": ["Google Drive new file trigger configuration", "send email action configuration"],
  "max_tool_calls": 2,
  "stopping_condition": "After 2 doc searches (1 for trigger, 1 for action), STOP and respond with available information. Do NOT make additional searches.",
  "fallback_strategy": "If searches return partial data, provide what you have and suggest user check ActivePieces UI for complete details.",
  "context": "Flow building requires trigger + action. Limit to 2 searches total. Provide what you find, don't chase perfection."
}}

Query: "How do I use webhooks in ActivePieces?"
{{
  "intent": "Understand how to use webhooks feature",
  "query_type": "explanation",
  "action_plan": [
    "Step 1: Search 'webhooks ActivePieces' ONCE in docs. SUCCESS = found webhook trigger/action info. MAX ATTEMPTS = 1",
    "Step 2: STOP after 1 search. Provide explanation based on what you found.",
    "Step 3: If search returns nothing, use general webhook knowledge and note that specific ActivePieces webhook docs weren't found."
  ],
  "recommended_tools": ["search_activepieces_docs"],
  "search_queries": ["webhooks ActivePieces trigger action"],
  "max_tool_calls": 1,
  "stopping_condition": "After 1 doc search, STOP and provide explanation. Do NOT search multiple times.",
  "fallback_strategy": "If no specific docs found, explain webhooks generally and suggest checking ActivePieces documentation.",
  "context": "Explanation question. ONE search maximum. Explain based on results, don't keep searching."
}}

Now analyze the user query above and provide the plan."""

        try:
            # Use GPT-5 with Responses API for advanced reasoning
            response = self.client.responses.create(
                model=self.model,
                input=planning_prompt,
                reasoning={
                    "effort": "medium"  # Medium reasoning for query analysis
                },
                text={
                    "verbosity": "medium"  # Medium verbosity for structured output
                }
            )
            
            plan_text = response.output_text.strip()
            
            # Parse the JSON response
            # Extract JSON from markdown code blocks if present
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_text:
                plan_text = plan_text.split("```", 1)[1].split("```", 1)[0].strip()
            
            plan = json.loads(plan_text)
            self._store_plan(cache_key, plan)
            plan_clone = self._clone_plan(plan)
            
            print(f"\n{'='*60}")
            print("📋 PLANNER OUTPUT:")
            print(f"Intent: {plan.get('intent', 'Unknown')}")
            print(f"Query Type: {plan.get('query_type', 'Unknown')}")
            print(f"Action Plan: {len(plan.get('action_plan', []))} steps")
            print(f"{'='*60}\n")
            
            return plan_clone
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Warning: Could not parse planner output as JSON: {e}")
            print(f"Raw output: {plan_text}")
            # Fallback to basic plan
            fallback = self._create_fallback_plan(normalized_query)
            self._store_plan(cache_key, fallback)
            return fallback
        
        except Exception as e:
            print(f"⚠️  Warning: Planner error: {e}")
            fallback = self._create_fallback_plan(normalized_query)
            self._store_plan(cache_key, fallback)
            return fallback
    
    def _create_fallback_plan(self, user_query: str) -> Dict[str, Any]:
        """
        Create a basic fallback plan if the planner fails.
        """
        return {
            "intent": "Process user query",
            "query_type": "general",
            "action_plan": [
                "Analyze the user query",
                "Use appropriate tools to find information",
                "Provide a comprehensive response"
            ],
            "recommended_tools": ["check_activepieces", "search_activepieces_docs"],
            "search_queries": [user_query],
            "context": "Fallback plan - process query normally"
        }
    
    def format_plan_for_agent(self, plan: Dict[str, Any]) -> str:
        """
        Format the plan into a clear instruction string for the agent.
        
        Args:
            plan: The plan dictionary from analyze_query
            
        Returns:
            Formatted string to include in the agent's prompt
        """
        formatted = f"""
🎯 QUERY ANALYSIS (Planning Layer):

USER INTENT: {plan.get('intent', 'Unknown')}
QUERY TYPE: {plan.get('query_type', 'general')}

📝 EXECUTION PLAN (FOLLOW EXACTLY):
"""
        
        for i, step in enumerate(plan.get('action_plan', []), 1):
            formatted += f"{i}. {step}\n"
        
        formatted += f"\n🔧 RECOMMENDED TOOLS: {', '.join(plan.get('recommended_tools', []))}\n"
        
        if plan.get('search_queries'):
            formatted += f"\n🔍 SUGGESTED SEARCHES (use these exact queries):\n"
            for query in plan.get('search_queries', []):
                formatted += f"  - \"{query}\"\n"
        
        formatted += f"\n⚠️ MAXIMUM TOOL CALLS ALLOWED: {plan.get('max_tool_calls', 3)}\n"
        
        formatted += f"\n🛑 STOPPING CONDITION:\n{plan.get('stopping_condition', 'Stop when you have enough info to answer')}\n"
        
        if plan.get('fallback_strategy'):
            formatted += f"\n🔄 FALLBACK STRATEGY:\n{plan.get('fallback_strategy')}\n"
        
        if plan.get('context'):
            formatted += f"\n💡 CONTEXT: {plan.get('context')}\n"
        
        formatted += "\n" + "="*60 + "\n"
        formatted += "⚡ CRITICAL: Follow this plan EXACTLY. Do NOT make extra searches.\n"
        formatted += "⚡ CRITICAL: STOP after reaching max tool calls or stopping condition.\n"
        formatted += "⚡ CRITICAL: If a tool fails, use fallback strategy immediately.\n"
        formatted += "="*60 + "\n"
        
        return formatted


# Global planner instance
_planner: Optional[QueryPlanner] = None


def get_planner() -> QueryPlanner:
    """Get or create the global planner instance."""
    global _planner
    if _planner is None:
        # Use gpt-5-mini by default (faster and cheaper), or gpt-5 for complex reasoning
        model = os.getenv("PLANNER_MODEL", "gpt-5-mini")
        _planner = QueryPlanner(model=model)
    return _planner


def create_guided_input(user_query: str) -> Dict[str, Any]:
    """
    Create a guided input for the agent by analyzing the user query.
    
    Args:
        user_query: The original user query
        
    Returns:
        Dictionary containing:
            - original_query: The user's original query
            - plan: The execution plan from the planner
            - enhanced_input: The query with planning context for the agent
    """
    planner = get_planner()
    plan = planner.analyze_query(user_query)
    plan_context = planner.format_plan_for_agent(plan)
    
    # Combine the plan with the original query
    enhanced_input = f"{plan_context}\n{'='*60}\n\nUSER QUERY: {user_query}"
    
    return {
        "original_query": user_query,
        "plan": plan,
        "enhanced_input": enhanced_input
    }

