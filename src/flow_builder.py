"""
Flow Builder - Specialized module for building comprehensive ActivePieces workflows.

ActivePieces is a workflow automation platform that allows users to create automated workflows
by connecting different services and applications through a visual flow builder. This module
helps users build flows for the ActivePieces platform with intelligent guidance and detailed plans.

Database Integration:
- 450 ActivePieces pieces (integrations) from ActivePieces API
- 2,890 actions with full input/output specifications
- 834 triggers with configuration details
- SQLite database with FTS5 full-text search
- Complete property metadata for all actions and triggers

Features:
- Three-phase flow analysis (analyze → search → build)
- Parallel component search using ThreadPoolExecutor
- AI-first detection (Text AI, Utility AI, Image AI, Video AI)
- RAG-enhanced recommendations from vector store
- GPT-5 powered comprehensive planning
- Adaptive model selection based on complexity
- Context-aware guide generation for ActivePieces platform
"""
import os
import json
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from openai import OpenAI
from src.tools import (
    find_piece_by_name,
    find_action_by_name,
    find_trigger_by_name,
    list_piece_actions_and_triggers,
    list_action_inputs,
    get_vector_store,
    web_search,
    get_code_generation_guidelines,
)

load_dotenv()


class FlowBuilder:
    """
    Specialized flow builder that creates comprehensive, step-by-step workflow guides.
    Uses GPT-5 for advanced reasoning about workflow construction.
    
    This builder leverages a comprehensive SQLite database with:
    - 450 ActivePieces integrations (pieces)
    - 2,890 actions with complete specifications
    - 834 triggers with full configurations
    - Full-text search (FTS5) for fast lookups
    - Complete input/output property metadata
    
    The builder uses a three-phase approach:
    1. Analyze: Understand user request and identify requirements
    2. Search: Find relevant pieces, actions, and triggers in parallel
    3. Build: Generate comprehensive step-by-step flow guide
    """
    
    def __init__(self, model: str = "gpt-5-mini"):
        """
        Initialize the flow builder with GPT-5 model.
        
        Args:
            model: Model to use ('gpt-5', 'gpt-5-mini', or 'gpt-5-nano')
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        print(f"✓ Flow Builder initialized with model: {model}")
        self._fast_mode = os.getenv("FLOW_BUILDER_FAST_MODE", "true").lower() in {"1", "true", "yes"}

    @staticmethod
    def _extract_keywords(text: str, max_words: int = 4) -> str:
        """Return the first few meaningful words from text for searching."""
        if not text:
            return ""
        tokens = [token.strip(",-:;|\n\t") for token in text.split() if token.strip()]
        if not tokens:
            return ""
        return " ".join(tokens[:max_words])

    @staticmethod
    def _generate_search_terms(text: str) -> List[str]:
        """Generate candidate search terms for a flow component description."""
        if not text:
            return []

        base = text.strip()
        lower = base.lower()
        separators = [" via ", " using ", " with ", " for "]
        candidates = {base}

        for sep in separators:
            if sep in lower:
                parts = base.lower().split(sep)
                tail = parts[-1].strip()
                if tail:
                    candidates.add(tail)

        words = [w.strip(",.;:") for w in base.split() if w.strip()]
        if len(words) >= 2:
            candidates.add(" ".join(words[:3]))
            candidates.add(" ".join(words[-3:]))

        # Filter and return unique preserving order
        ordered: List[str] = []
        seen = set()
        for item in [base, *candidates]:
            normalized = item.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            ordered.append(normalized)

        return ordered

    @staticmethod
    def _detect_ai_category(text: Optional[str]) -> Optional[str]:
        if not text:
            return None

        lowered = text.lower()

        if any(keyword in lowered for keyword in ("image", "logo", "banner", "graphic", "picture", "thumbnail")):
            return "image"

        if any(keyword in lowered for keyword in ("video", "clip", "animation", "reel", "promo")):
            return "video"

        if any(keyword in lowered for keyword in ("extract", "structured", "json", "schema", "fields", "parse", "table", "invoice")):
            return "structured"

        if any(keyword in lowered for keyword in ("moderation", "flag", "safe", "inappropriate")):
            return "moderation"

        if any(keyword in lowered for keyword in ("classify", "categorize", "category", "label")):
            return "classification"

        if any(keyword in lowered for keyword in ("summarize", "summary", "tl;dr", "compress")):
            return "summary"

        if any(keyword in lowered for keyword in (
            "ask",
            "answer",
            "write",
            "generate",
            "draft",
            "translate",
            "sentiment",
            "analysis",
            "chat",
            "respond",
            "reply",
            "describe",
            "explain",
            "gpt",
            "gpt-4",
            "gpt4",
            "gpt-5",
            "gpt5",
            "chatgpt",
            "openai",
            "claude",
            "gemini",
            "sonnet",
            "anthropic",
        )):
            return "text"

        return None

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_ai_piece_catalog() -> Dict[str, Optional[Dict[str, Any]]]:
        piece_names = {
            "text_ai": "Text AI",
            "utility_ai": "Utility AI",
            "image_ai": "Image AI",
            "video_ai": "Video AI",
        }

        catalog: Dict[str, Optional[Dict[str, Any]]] = {}
        for key, piece_name in piece_names.items():
            try:
                catalog[key] = find_piece_by_name(piece_name)
            except Exception as exc:
                print(f"⚠️  Unable to load AI piece '{piece_name}': {exc}")
                catalog[key] = None

        return catalog

    @staticmethod
    def _resolve_action_display(piece: Optional[Dict[str, Any]], desired_action: str) -> str:
        if not piece or not desired_action:
            return desired_action

        actions = piece.get("actions") or []
        for action in actions:
            display = (
                action.get("displayName")
                or action.get("display_name")
                or action.get("name")
            )
            if display and display.lower() == desired_action.lower():
                return display

        return desired_action

    @staticmethod
    def _select_ai_recommendation(action_text: str) -> Optional[Dict[str, str]]:
        category = FlowBuilder._detect_ai_category(action_text)
        if not category:
            return None

        catalog = FlowBuilder._get_ai_piece_catalog()

        if category == "structured":
            piece = catalog.get("utility_ai")
            if piece:
                action_name = FlowBuilder._resolve_action_display(piece, "Extract Structured Data")
                return {
                    "piece_key": "utility_ai",
                    "piece": piece,
                    "action": action_name,
                    "reason": "Structured data extraction task",
                }
            return None

        if category == "moderation":
            piece = catalog.get("utility_ai")
            if piece:
                action_name = FlowBuilder._resolve_action_display(piece, "Check Moderation")
                return {
                    "piece_key": "utility_ai",
                    "piece": piece,
                    "action": action_name,
                    "reason": "Content moderation task",
                }
            return None

        if category == "classification":
            piece = catalog.get("utility_ai")
            if piece:
                action_name = FlowBuilder._resolve_action_display(piece, "Classify Text")
                return {
                    "piece_key": "utility_ai",
                    "piece": piece,
                    "action": action_name,
                    "reason": "Text classification task",
                }
            return None

        if category == "summary":
            piece = catalog.get("text_ai")
            if piece:
                action_name = FlowBuilder._resolve_action_display(piece, "Summarize Text")
                return {
                    "piece_key": "text_ai",
                    "piece": piece,
                    "action": action_name,
                    "reason": "Text summarization task",
                }
            return None

        if category == "image":
            piece = catalog.get("image_ai")
            if piece:
                action_name = FlowBuilder._resolve_action_display(piece, "Generate Image")
                return {
                    "piece_key": "image_ai",
                    "piece": piece,
                    "action": action_name,
                    "reason": "Image generation task",
                }
            return None

        if category == "video":
            piece = catalog.get("video_ai")
            if piece:
                action_name = FlowBuilder._resolve_action_display(piece, "Generate Video")
                return {
                    "piece_key": "video_ai",
                    "piece": piece,
                    "action": action_name,
                    "reason": "Video generation task",
                }
            return None

        if category in {"text"}:
            piece = catalog.get("text_ai")
            if piece:
                action_name = FlowBuilder._resolve_action_display(piece, "Ask AI")
                return {
                    "piece_key": "text_ai",
                    "piece": piece,
                    "action": action_name,
                    "reason": "Text AI supports OpenAI GPT-4/5, Claude, and Gemini models directly",
                }

        return None

    @staticmethod
    @lru_cache(maxsize=128)
    def _rag_piece_suggestions(query: str) -> List[str]:
        if not query:
            return []
        try:
            vector_store = get_vector_store()
            docs = vector_store.similarity_search(query, k=4)
            suggestions: List[str] = []
            for doc in docs or []:
                metadata = doc.metadata or {}
                meta_piece = metadata.get("piece") or metadata.get("title") or metadata.get("source")
                snippet = (doc.page_content or "").strip()
                if len(snippet) > 180:
                    snippet = snippet[:180].rstrip() + "..."
                if meta_piece:
                    suggestions.append(f"{meta_piece}: {snippet}")
                elif snippet:
                    suggestions.append(snippet)
            return suggestions
        except Exception as exc:
            print(f"⚠️  RAG suggestion error for '{query}': {exc}")
            return []

    @staticmethod
    @lru_cache(maxsize=1)
    def _latest_http_request_docs() -> str:
        try:
            return web_search("ActivePieces HTTP Request piece latest documentation")
        except Exception as exc:
            return f"⚠️  Unable to retrieve HTTP Request documentation: {exc}"

    @staticmethod
    def _determine_action_strategy(action_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Decide how to fulfill an action requirement based on available pieces."""

        piece = action_entry.get("piece")
        matches = action_entry.get("matches") or []
        desired = action_entry.get("action_description")

        strategy: Dict[str, Any] = {
            "status": "custom",
            "recommended_piece": None,
            "recommended_action": None,
            "notes": [],
            "fallbacks": [],
        }

        preferred_piece = action_entry.get("preferred_piece")
        preferred_action = action_entry.get("preferred_action")
        preferred_piece_key = action_entry.get("preferred_piece_key")
        rag_suggestions = action_entry.get("rag_suggestions") or []

        if preferred_piece:
            piece = preferred_piece
            display_name = preferred_piece.get("displayName") or preferred_piece.get("name")
            if preferred_action:
                matches = [
                    {
                        "piece": display_name or "ActivePieces AI Utility",
                        "action": preferred_action,
                        "description": "Native ActivePieces AI utility",
                    }
                ] + [
                    match for match in matches
                    if (match.get("piece") or "").lower() != (display_name or "").lower()
                ]
            strategy["notes"].append(
                f"Use native ActivePieces AI utility '{display_name}' ({preferred_action}) to handle: {desired}."
            )

        if piece:
            display_name = piece.get("displayName") or piece.get("name")
            strategy["status"] = "native"
            strategy["recommended_piece"] = display_name
            matching_record = None
            for match in matches:
                if match.get("piece") and display_name and match["piece"].lower() == display_name.lower():
                    matching_record = match
                    break
            strategy["recommended_action"] = (matching_record or {}).get("action") or preferred_action
            if not strategy["recommended_action"] and matches:
                strategy["recommended_action"] = matches[0].get("action")
            strategy["notes"].append(
                f"Use native piece '{display_name}' to accomplish: {desired}."
            )
            if preferred_piece_key in {"text_ai", "utility_ai", "image_ai", "video_ai"}:
                strategy["notes"].append(
                    "This Action supports selecting OpenAI GPT-4/5, Google Gemini, and Anthropic Claude models directly inside ActivePieces."
                )
            return strategy

        if matches:
            first_match = matches[0]
            strategy["status"] = "alternative"
            strategy["recommended_piece"] = first_match.get("piece")
            strategy["recommended_action"] = first_match.get("action")
            strategy["notes"].append(
                f"No direct piece detected; consider '{first_match.get('piece')}' → '{first_match.get('action')}' for: {desired}."
            )
            if len(matches) > 1:
                strategy["notes"].append(
                    "Additional alternatives available; review other search matches for best fit."
                )
            return strategy

        if rag_suggestions:
            strategy["status"] = "rag"
            strategy["notes"].append(
                "Gathered alternative piece ideas from documentation search; review suggestions before custom implementation."
            )
            strategy["fallbacks"].append(
                {
                    "type": "rag_suggestions",
                    "description": "\n".join(rag_suggestions[:3]),
                }
            )
            return strategy

        strategy["fallbacks"] = [
            {
                "type": "http_request",
                "description": "Use the HTTP Request piece to call the service directly if it exposes an API.",
            },
            {
                "type": "code",
                "description": "Build a custom code step with the ActivePieces code template.",
            },
        ]
        strategy["notes"].append(
            "No direct or alternative piece found; evaluate HTTP Request or custom code options."
        )
        return strategy

    @staticmethod
    @lru_cache(maxsize=128)
    def _piece_overview_cached(piece_name: str) -> str:
        return list_piece_actions_and_triggers(piece_name)

    @staticmethod
    def _safe_piece_overview(piece_name: str) -> str:
        try:
            return FlowBuilder._piece_overview_cached(piece_name)
        except Exception as exc:
            return f"⚠️  Unable to load actions/triggers for {piece_name}: {exc}"

    @staticmethod
    @lru_cache(maxsize=256)
    def _action_inputs_cached(piece_name: str, action_name: str) -> str:
        return list_action_inputs(piece_name, action_name)

    @staticmethod
    def _safe_action_inputs(piece_name: str, action_name: str) -> str:
        try:
            return FlowBuilder._action_inputs_cached(piece_name, action_name)
        except Exception as exc:
            return f"⚠️  Unable to fetch inputs for {piece_name} – {action_name}: {exc}"
    
    def analyze_flow_request(self, user_request: str) -> Dict[str, Any]:
        """
        Analyze the user's flow request to understand what they want to build.
        
        Args:
            user_request: The user's flow building request
            
        Returns:
            Dictionary with flow analysis including goal, trigger type, actions, complexity, and confidence
        """
        analysis_prompt = f"""You are an expert workflow automation analyst for ActivePieces, a powerful workflow automation platform.

IMPORTANT: This analysis is for building automation workflows in ActivePieces platform - a visual workflow builder where users connect different services and applications.

You have access to a comprehensive ActivePieces database with:
- 450 pieces (integrations like Gmail, Slack, Google Sheets, etc.)
- 2,890 actions (operations you can perform)
- 834 triggers (events that start a flow)
- Complete metadata including all input properties and configurations

Analyze this ActivePieces flow building request and determine:
1. What the user wants to accomplish (trigger → actions)
2. What information is clear vs unclear
3. The complexity level of the flow

User Request: "{user_request}"

Respond in this exact JSON format:
{{
  "flow_goal": "brief description of what user wants to accomplish",
  "trigger_type": "identified trigger or 'unclear'",
  "actions_needed": ["action 1", "action 2", ...],
  "is_clear": true/false,
  "missing_info": ["piece 1", "piece 2", ...],
  "complexity": "simple|moderate|complex",
  "confidence": "high|medium|low"
}}

Examples:

Request: "I want to send an email when a new file is added to Google Drive"
{{
  "flow_goal": "Send email notification when new file added to Google Drive",
  "trigger_type": "Google Drive - New File",
  "actions_needed": ["Send Email"],
  "is_clear": true,
  "missing_info": [],
  "complexity": "simple",
  "confidence": "high"
}}

Request: "Automate my customer onboarding"
{{
  "flow_goal": "Automate customer onboarding process",
  "trigger_type": "unclear",
  "actions_needed": ["unclear - depends on onboarding steps"],
  "is_clear": false,
  "missing_info": ["trigger source", "onboarding steps", "tools used"],
  "complexity": "complex",
  "confidence": "low"
}}

Now analyze the user's request above."""

        reasoning_effort = "medium"
        verbosity_level = "medium"

        if self._fast_mode:
            reasoning_effort = "low"
            verbosity_level = "low"

        try:
            response = self.client.responses.create(
                model=self.model,
                input=analysis_prompt,
                reasoning={"effort": reasoning_effort},
                text={"verbosity": verbosity_level}
            )
            
            analysis_text = response.output_text.strip()
            
            # Parse JSON response
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(analysis_text)
            
            print(f"\n{'='*60}")
            print("🔍 FLOW ANALYSIS:")
            print(f"Goal: {analysis.get('flow_goal', 'Unknown')}")
            print(f"Clarity: {'Clear' if analysis.get('is_clear') else 'Needs clarification'}")
            print(f"Complexity: {analysis.get('complexity', 'Unknown')}")
            print(f"{'='*60}\n")
            
            return analysis
            
        except Exception as e:
            print(f"⚠️  Flow analysis error: {e}")
            return {
                "flow_goal": user_request,
                "is_clear": True,
                "complexity": "moderate",
                "confidence": "medium"
            }
    
    def search_flow_components(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Search for the pieces, triggers, and actions needed for the flow."""

        components: Dict[str, Any] = {
            "trigger": None,
            "trigger_matches": [],
            "actions": [],
            "pieces": [],
            "missing": [],
            "alternatives": [],
        }

        confidence = (analysis.get("confidence") or "").lower()
        should_fetch_kb = (not self._fast_mode) or confidence in {"", "medium", "low"}

        # Prepare cached lookups to avoid duplicate DB hits within a single request
        @lru_cache(maxsize=32)
        def cached_find_piece(name: str):
            try:
                return find_piece_by_name(name)
            except Exception as exc:
                print(f"⚠️  Piece lookup failed for '{name}': {exc}")
                return None

        @lru_cache(maxsize=32)
        def cached_find_action(term: str):
            try:
                return find_action_by_name(term, limit=8)
            except Exception as exc:
                print(f"⚠️  Action search failed for '{term}': {exc}")
                return []

        @lru_cache(maxsize=32)
        def cached_find_trigger(term: str):
            try:
                return find_trigger_by_name(term, limit=8)
            except Exception as exc:
                print(f"⚠️  Trigger search failed for '{term}': {exc}")
                return []

        def perform_vector_search() -> List[str]:
            try:
                vector_store = get_vector_store()
                search_query = " ".join(
                    filter(
                        None,
                        [
                            analysis.get("flow_goal", ""),
                            analysis.get("trigger_type", ""),
                            " ".join(analysis.get("actions_needed", [])),
                        ],
                    )
                ).strip()

                if not search_query:
                    return []

                results = vector_store.similarity_search(search_query, k=3)
                return [doc.page_content for doc in results] if results else []
            except Exception as exc:
                print(f"⚠️  Knowledge base search error: {exc}")
                return []

        futures: Dict[Any, Any] = {}
        trigger_terms = []

        with ThreadPoolExecutor(max_workers=8) as executor:
            trigger_type = analysis.get("trigger_type")
            if trigger_type and trigger_type != "unclear":
                trigger_terms = self._generate_search_terms(trigger_type)
                for term in trigger_terms[:2]:  # limit parallel fan-out
                    futures[("trigger_piece", term)] = executor.submit(cached_find_piece, term)
                    futures[("trigger_matches", term)] = executor.submit(cached_find_trigger, term)

            action_terms: List[tuple[int, str, str]] = []
            for idx, action_desc in enumerate(analysis.get("actions_needed", [])):
                if not action_desc or action_desc.startswith("unclear"):
                    continue

                terms = self._generate_search_terms(action_desc)
                primary_term = terms[0] if terms else self._extract_keywords(action_desc)
                action_terms.append((idx, action_desc, primary_term))
                futures[("action_piece", idx, primary_term)] = executor.submit(cached_find_piece, primary_term)
                futures[("action_matches", idx, primary_term)] = executor.submit(cached_find_action, primary_term)
                futures[("action_rag", idx, action_desc)] = executor.submit(FlowBuilder._rag_piece_suggestions, action_desc)

            if should_fetch_kb:
                futures[("knowledge_context", 0)] = executor.submit(perform_vector_search)

        resolved: Dict[Any, Any] = {}
        for key, future in futures.items():
            try:
                resolved[key] = future.result()
            except Exception as exc:
                print(f"⚠️  Lookup task {key} failed: {exc}")
                resolved[key] = None

        # Process trigger results
        trigger_piece = None
        for term in trigger_terms:
            candidate_piece = resolved.get(("trigger_piece", term))
            if candidate_piece:
                trigger_piece = candidate_piece
                break

        trigger_matches = []
        for term in trigger_terms:
            matches = resolved.get(("trigger_matches", term)) or []
            trigger_matches.extend(matches)

        if trigger_piece:
            components["trigger"] = {
                "piece": trigger_piece,
                "trigger_type": trigger_type,
                "search_terms": trigger_terms,
            }
            if trigger_piece not in components["pieces"]:
                components["pieces"].append(trigger_piece)
        elif trigger_type and trigger_type != "unclear":
            components["missing"].append(f"Trigger: {trigger_type}")

        if trigger_matches:
            components["trigger_matches"] = trigger_matches

        # Process action results
        for idx, action_desc, primary_term in action_terms:
            action_piece = resolved.get(("action_piece", idx, primary_term))
            matches = resolved.get(("action_matches", idx, primary_term)) or []
            rag_suggestions = resolved.get(("action_rag", idx, action_desc)) or []

            ai_recommendation = self._select_ai_recommendation(action_desc)
            preferred_piece = None
            preferred_action = None
            preferred_piece_key = None
            recommendation_reason = None
            if ai_recommendation:
                preferred_piece = ai_recommendation.get("piece")
                preferred_action = ai_recommendation.get("action")
                preferred_piece_key = ai_recommendation.get("piece_key")
                recommendation_reason = ai_recommendation.get("reason")

                if preferred_piece:
                    action_piece = action_piece or preferred_piece
                    preferred_display = preferred_piece.get("displayName") or preferred_piece.get("name")
                    if preferred_display:
                        preferred_record = {
                            "piece": preferred_display,
                            "action": preferred_action or "Primary Action",
                            "description": recommendation_reason or "Native ActivePieces AI utility",
                        }
                        matches = [preferred_record] + [
                            match for match in matches
                            if (match.get("piece") or "").lower() != preferred_display.lower()
                        ]

            action_entry = {
                "action_description": action_desc,
                "search_term": primary_term,
                "piece": action_piece,
                "matches": matches,
                "preferred_piece": preferred_piece,
                "preferred_action": preferred_action,
                "preferred_piece_key": preferred_piece_key,
                "ai_reason": recommendation_reason,
                "rag_suggestions": rag_suggestions,
            }

            if action_piece:
                if action_piece not in components["pieces"]:
                    components["pieces"].append(action_piece)
            else:
                components["missing"].append(f"Action: {action_desc}")
                if matches:
                    components["alternatives"].extend(matches[:3])
                if rag_suggestions:
                    components["alternatives"].extend(
                        [
                            {
                                "piece": "Knowledge Base Suggestion",
                                "action": "",
                                "description": suggestion,
                            }
                            for suggestion in rag_suggestions[:3]
                        ]
                    )

            components["actions"].append(action_entry)

        components["knowledge_context"] = resolved.get(("knowledge_context", 0)) or []
        
        return components
    
    def build_comprehensive_plan(
        self, 
        user_request: str, 
        analysis: Dict[str, Any], 
        components: Dict[str, Any],
        user_answers: Optional[str] = None
    ) -> str:
        """
        Build a comprehensive, step-by-step flow building plan.
        
        Args:
            user_request: Original user request
            analysis: Flow analysis
            components: Found components
            user_answers: Optional additional user information (currently unused)
            
        Returns:
            Comprehensive flow building guide
        """
        # Prepare context for the guide generator
        context_parts: List[str] = [
            f"""
USER REQUEST: {user_request}

FLOW ANALYSIS:
- Goal: {analysis.get('flow_goal', 'Unknown')}
- Trigger: {analysis.get('trigger_type', 'Unknown')}
- Actions: {', '.join(analysis.get('actions_needed', []))}
- Complexity: {analysis.get('complexity', 'Unknown')}

FOUND COMPONENTS:
"""
        ]

        context_parts.append(
            "\n✓ FLOW BUILDING FOUNDATIONS:\n"
            "  - Start every flow with exactly one trigger; it controls when the flow runs.\n"
            "  - Add actions after the trigger in the order they should execute; each action runs sequentially and the flow finishes once the last action completes.\n"
            "  - Insert router steps to branch the flow; create as many branches as needed and add filters on each branch to decide when it should execute.\n"
            "  - Configure branch filters with AND/OR groups so the branch runs only when its conditions are met; after a branch finishes, the flow continues with any steps placed after the router.\n"
            "  - Use loops when you need to process every item in an array or list; the actions inside the loop repeat once per item in the input collection.\n"
            "  - Map outputs from previous steps—including trigger data and earlier actions—into later actions; for example, reuse Gmail trigger fields like email text or attachments anywhere downstream.\n"
            "  - Test each action (and the trigger) as you build to confirm authentication, inputs, and data mappings before adding the next step.\n"
        )

        trigger_info = components.get("trigger")
        trigger_matches = components.get("trigger_matches", [])
        if trigger_info and trigger_info.get("piece"):
            trigger_piece = trigger_info["piece"]
            trigger_name = trigger_piece.get('displayName', 'Unknown')
            context_parts.append(f"\n✓ TRIGGER PIECE: {trigger_name}")
            context_parts.append(f"  Description: {trigger_piece.get('description', 'N/A')}")
            
            triggers = trigger_piece.get('triggers', [])
            if triggers:
                context_parts.append(f"  Available Triggers ({len(triggers)}), top options:")
                for t in triggers[:3]:
                    context_parts.append(
                        f"    - {t.get('displayName', 'Unknown')}: {t.get('description', 'N/A')}"
                    )
        elif analysis.get("trigger_type") not in (None, "unclear"):
            trigger_label = analysis.get("trigger_type")
            context_parts.append(
                f"\n⚠️  Trigger piece not confirmed for '{trigger_label}'."
            )

        if trigger_matches:
            context_parts.append("  Trigger search suggestions:")
            for match in trigger_matches[:5]:
                context_parts.append(
                    f"    - {match.get('piece', 'Unknown piece')} → {match.get('trigger', 'Unknown trigger')}"
                )

        piece_overviews: List[str] = []
        seen_piece_names = set()
        for piece in components.get("pieces", []):
            display = piece.get('displayName') or piece.get('name')
            if not display:
                continue
            key = display.lower()
            if key in seen_piece_names:
                continue
            seen_piece_names.add(key)
            overview = self._safe_piece_overview(display)
            piece_overviews.append(f"\n=== {display} Actions & Triggers ===\n{overview}")

        if piece_overviews:
            context_parts.append("\n✓ PIECE CAPABILITY SUMMARIES:")
            context_parts.extend(piece_overviews)

        ai_highlights: List[str] = []
        for action_info in components.get("actions", []):
            preferred_key = action_info.get("preferred_piece_key")
            if not preferred_key:
                continue
            preferred_piece = action_info.get("preferred_piece") or action_info.get("piece")
            preferred_action = action_info.get("preferred_action") or (action_info.get("strategy") or {}).get("recommended_action")
            reason = action_info.get("ai_reason") or "ActivePieces AI utility"
            piece_display = None
            if isinstance(preferred_piece, dict):
                piece_display = preferred_piece.get("displayName") or preferred_piece.get("name")
            if not piece_display:
                piece_display = "ActivePieces AI utility"
            ai_highlights.append(
                f"  - {piece_display} → {preferred_action or 'Primary Action'} ({reason})"
            )

        if ai_highlights:
            context_parts.append("\n✓ ACTIVEPIECES AI UTILITIES SELECTED:")
            context_parts.extend(ai_highlights)

        action_strategies: List[Dict[str, Any]] = []
        needs_http_fallback = False
        needs_code_fallback = False

        for action_info in components.get("actions", []):
            strategy = self._determine_action_strategy(action_info)
            action_info["strategy"] = strategy
            action_detail_lines = [
                f"\n→ Desired Action: {action_info.get('action_description', 'Unknown')}",
                f"  Status: {strategy['status']}",
            ]

            for note in strategy.get("notes", []):
                action_detail_lines.append(f"  Note: {note}")

            selected_inputs = None
            selected_piece = strategy.get("recommended_piece")
            selected_action = strategy.get("recommended_action")

            if strategy['status'] in {"native", "alternative"} and selected_piece and selected_action:
                selected_inputs = self._safe_action_inputs(selected_piece, selected_action)

            action_info["inputs_reference"] = selected_inputs

            if strategy.get("fallbacks"):
                fallback_types = {fallback.get("type") for fallback in strategy["fallbacks"]}
                if "http_request" in fallback_types:
                    needs_http_fallback = True
                if "code" in fallback_types:
                    needs_code_fallback = True
                for fallback in strategy["fallbacks"]:
                    action_detail_lines.append(
                        f"  Fallback: {fallback.get('type')}: {fallback.get('description')}"
                    )

            rag_suggestions = action_info.get("rag_suggestions") or []
            if rag_suggestions:
                action_detail_lines.append("  Knowledge Base Alternatives:")
                for suggestion in rag_suggestions[:3]:
                    action_detail_lines.append(f"    - {suggestion}")

            if selected_inputs:
                action_detail_lines.append(
                    f"  Input Reference ({selected_piece} – {selected_action}):\n{selected_inputs}"
                )

            action_strategies.append("\n".join(action_detail_lines))

        if action_strategies:
            context_parts.append("\n✓ ACTION STRATEGIES:")
            context_parts.extend(action_strategies)

        http_reference = None
        http_docs_update = None
        if needs_http_fallback:
            for candidate_piece in ("HTTP", "HTTP Request"):
                http_reference = self._safe_action_inputs(candidate_piece, "Make Request")
                if not http_reference or http_reference.startswith("⚠️"):
                    continue
                if "✗" not in http_reference:
                    break
            http_docs_update = self._latest_http_request_docs()

        if http_reference:
            context_parts.append(
                f"\n✓ HTTP REQUEST FALLBACK INPUTS:\n{http_reference}"
            )

        if http_docs_update:
            snippet = (http_docs_update or "").strip()
            if len(snippet) > 800:
                snippet = snippet[:800].rstrip() + "..."
            context_parts.append(
                f"\n✓ HTTP REQUEST LATEST DOCS:\n{snippet}"
            )

        code_guidelines_reference = None
        if needs_code_fallback:
            try:
                guidelines_raw = (get_code_generation_guidelines("api_call") or "").strip()
                if len(guidelines_raw) > 1200:
                    code_guidelines_reference = guidelines_raw[:1200].rstrip() + "..."
                else:
                    code_guidelines_reference = guidelines_raw
            except Exception as exc:
                code_guidelines_reference = f"⚠️  Unable to load code generation guidelines: {exc}"

        if code_guidelines_reference:
            context_parts.append(
                f"\n✓ CUSTOM CODE GUIDANCE (excerpt):\n{code_guidelines_reference}"
            )

        knowledge_context = components.get("knowledge_context") or []
        if knowledge_context:
            context_parts.append("\n✓ ADDITIONAL CONTEXT FROM KNOWLEDGE BASE:")
            for kb_item in knowledge_context[:2]:
                snippet = kb_item.strip()
                if len(snippet) > 220:
                    snippet = snippet[:220] + "..."
                context_parts.append(f"  - {snippet}")

        if user_answers:
            context_parts.append(f"\n✓ USER PROVIDED ADDITIONAL INFO:\n{user_answers}")
        
        if components.get("missing"):
            context_parts.append("\n⚠️  MISSING/UNCLEAR COMPONENTS:")
            for missing in components["missing"]:
                context_parts.append(f"  - {missing}")

        context = "\n".join(context_parts)
        
        # Build the comprehensive plan
        planning_prompt = f"""You are an expert ActivePieces workflow architect. Create a COMPREHENSIVE, DETAILED, and ACTIONABLE flow building guide for the ActivePieces automation platform.

ABOUT ACTIVEPIECES:
ActivePieces is a powerful workflow automation platform (similar to Zapier or Make.com) that allows users to build automated workflows by connecting different services and applications. Users create flows in the ActivePieces visual flow builder by:
1. Adding a trigger (what starts the flow)
2. Adding actions (what happens when the flow runs)
3. Connecting pieces (integrations) together
4. Mapping data between steps

Your guide should help users build this flow directly in their ActivePieces instance.

DATABASE CAPABILITIES:
- 450 ActivePieces pieces (integrations) with full metadata
- 2,890 actions with complete input/output specifications
- 834 triggers with configuration details
- Full-text search enabled across all components
- Complete property definitions for all actions and triggers

{context}

IMPORTANT ACTIVEPIECES FLOW BUILDER RULES:
- ALWAYS specify that this is for building in ActivePieces platform
- ALWAYS use native ActivePieces AI utilities (Text AI, Utility AI, Image AI, Video AI) for AI tasks. They provide direct access to OpenAI GPT-4/5, Google Gemini, and Anthropic Claude models without custom API calls.
- When the user names a specific model (e.g., "GPT-5"), explain how to select that model inside the relevant ActivePieces action instead of building an HTTP request.
- The database provides comprehensive information about all ActivePieces pieces - leverage this for accurate guidance.
- All action/trigger input properties are documented in the database - include them in your guides.
- Only suggest HTTP Request or custom code after confirming no native or alternative ActivePieces piece exists and documenting the knowledge-base suggestions you've already checked.
- Always remind users that they're building this in their ActivePieces instance

Create a powerful, step-by-step guide that includes:

**START YOUR GUIDE WITH:**
A clear introduction stating: "This guide will help you build [flow description] in ActivePieces, a workflow automation platform."

**THEN INCLUDE:**
1. **Flow Overview** - What this ActivePieces flow does and why
2. **Prerequisites** - What the user needs before starting (ActivePieces account, required integrations, etc.)
3. **Step-by-Step Instructions** - DETAILED steps with ALL required inputs for building in ActivePieces
4. **Trigger Configuration** - Exact settings in ActivePieces, all input fields, authentication
5. **Action Configuration** - For EACH ActivePieces action, list ALL inputs (required & optional)
6. **Testing & Validation** - How to test the flow in ActivePieces
7. **Common Issues & Solutions** - Potential problems and fixes specific to ActivePieces
8. **Pro Tips** - Advanced configurations or optimizations in ActivePieces

CRITICAL REQUIREMENTS:
- Always mention that this is for ActivePieces platform
- List ALL input properties for each trigger/action (don't say "configure" - tell them EXACTLY what to configure in ActivePieces)
- Include authentication requirements specific to ActivePieces
- Provide example values where helpful
- Be specific about data mapping between steps in ActivePieces
- Reference the ActivePieces visual flow builder interface
- If information is missing, search online or provide best practices
- Make it so detailed that a beginner can build this flow in ActivePieces perfectly

Format your response in clear markdown with headers, bullet points, and code blocks where appropriate.
Make this the MOST COMPREHENSIVE ActivePieces flow guide possible - the user should be able to build this flow in their ActivePieces instance by following your guide step-by-step.
"""

        try:
            # Use web search if we have missing components or need more details
            if components.get("missing") or analysis.get("confidence") == "low":
                search_results = self._search_for_missing_info(analysis, components)
                planning_prompt += f"\n\nADDITIONAL RESEARCH FROM WEB:\n{search_results}\n"
            
            complexity_level = (analysis.get("complexity") or "moderate").lower()
            confidence_level = (analysis.get("confidence") or "").lower()

            model_choice = self.model
            reasoning_effort = "high"
            verbosity_level = "high"

            if complexity_level == "complex" and not self._fast_mode:
                model_choice = "gpt-5"

            if self._fast_mode:
                if complexity_level == "simple" and confidence_level == "high":
                    reasoning_effort = "low"
                    verbosity_level = "medium"
                else:
                    reasoning_effort = "medium"
                    verbosity_level = "high"
            elif complexity_level == "simple" and confidence_level == "high":
                reasoning_effort = "medium"
                verbosity_level = "medium"

            if components.get("missing") and not self._fast_mode:
                model_choice = "gpt-5"
                reasoning_effort = "high"
                verbosity_level = "high"

            # Generate comprehensive plan
            response = self.client.responses.create(
                model=model_choice,
                input=planning_prompt,
                reasoning={"effort": reasoning_effort},
                text={"verbosity": verbosity_level}
            )
            
            comprehensive_guide = response.output_text.strip()
            
            print(f"\n{'='*60}")
            print("📋 COMPREHENSIVE FLOW GUIDE GENERATED")
            print(f"Length: {len(comprehensive_guide)} characters")
            print(f"{'='*60}\n")
            
            return comprehensive_guide
            
        except Exception as e:
            print(f"⚠️  Plan building error: {e}")
            return self._create_basic_plan(user_request, analysis, components)
    
    def _search_for_missing_info(self, analysis: Dict[str, Any], components: Dict[str, Any]) -> str:
        """Search online for missing information about the flow."""
        search_queries = []
        
        # Build search queries for missing pieces
        for missing in components.get("missing", []):
            search_queries.append(f"ActivePieces {missing} how to configure")
        
        # Add general search for the flow type
        if analysis.get("flow_goal"):
            search_queries.append(f"How to build {analysis['flow_goal']} workflow in ActivePieces")
        
        search_results = []
        for query in search_queries[:2]:  # Limit to 2 searches
            try:
                # Import and use the web search function
                from src.tools import _search_with_openai, _search_with_perplexity
                import os
                
                search_provider = os.getenv("SEARCH_PROVIDER", "openai").lower()
                if search_provider == "openai":
                    result = _search_with_openai(query)
                else:
                    result = _search_with_perplexity(query)
                
                search_results.append(f"Query: {query}\nResult: {result}\n")
            except Exception as e:
                print(f"⚠️  Web search error: {e}")
        
        return "\n".join(search_results) if search_results else "No additional information found online."
    
    def _create_basic_plan(self, user_request: str, analysis: Dict[str, Any], components: Dict[str, Any]) -> str:
        """Create a basic plan if comprehensive planning fails."""
        plan = f"# ActivePieces Flow Building Guide: {analysis.get('flow_goal', user_request)}\n\n"
        plan += f"This guide will help you build this automation workflow in ActivePieces, a powerful workflow automation platform.\n\n"
        plan += f"## Overview\n{analysis.get('flow_goal', user_request)}\n\n"
        
        if components.get("trigger"):
            plan += "## Trigger Setup\n"
            trigger_piece = components["trigger"].get("piece")
            if trigger_piece:
                plan += f"1. Use the **{trigger_piece.get('displayName')}** piece\n"
                plan += f"2. Select the appropriate trigger\n"
                plan += f"3. Configure the trigger settings\n\n"
        
        if components.get("actions"):
            plan += "## Actions\n"
            for i, action_info in enumerate(components["actions"], 1):
                piece = action_info.get("piece")
                if piece:
                    plan += f"{i}. **{piece.get('displayName')}**: {action_info.get('action_description')}\n"
        
        plan += "\n## Next Steps\n"
        plan += "1. Log into your ActivePieces instance (ActivePieces platform)\n"
        plan += "2. Create a new flow in the ActivePieces visual flow builder\n"
        plan += "3. Add and configure the trigger in ActivePieces\n"
        plan += "4. Add and configure the actions in ActivePieces\n"
        plan += "5. Test your flow in ActivePieces\n"
        plan += "\n**Note:** This flow is designed for the ActivePieces automation platform.\n"
        
        return plan


# Global flow builder instance
_flow_builder: Optional[FlowBuilder] = None


def get_flow_builder() -> FlowBuilder:
    """Get or create the global flow builder instance."""
    global _flow_builder
    if _flow_builder is None:
        model = os.getenv("FLOW_BUILDER_MODEL", "gpt-5-mini")
        _flow_builder = FlowBuilder(model=model)
    return _flow_builder


def build_flow(
    user_request: str, 
    user_answers: Optional[str] = None,
    primary_model: str = "gpt-5-mini",
    secondary_model: Optional[str] = None,
    use_dual_models: bool = False
) -> Dict[str, Any]:
    """
    Main function to build a comprehensive ActivePieces flow guide using the ActivePieces database.
    
    ActivePieces is a workflow automation platform where users build automated workflows by
    connecting different services and applications. This function helps users create flows
    for the ActivePieces platform.
    
    This function orchestrates a three-phase process:
    1. Analyze: Parse user request and identify ActivePieces requirements
    2. Search: Query ActivePieces database (450 pieces, 2,890 actions, 834 triggers) in parallel
    3. Build: Generate detailed, step-by-step ActivePieces implementation guide
    
    Args:
        user_request: The user's ActivePieces flow building request
        user_answers: Optional additional user information (currently unused)
        primary_model: Primary model to use (default: gpt-5-mini)
        secondary_model: Optional secondary model for dual-model mode
        use_dual_models: Whether to use dual models (one for analysis, one for building)
        
    Returns:
        Dictionary with ActivePieces flow guide and metadata:
        - guide: Comprehensive markdown guide for building in ActivePieces
        - analysis: Flow analysis with complexity/confidence
        - components: Found ActivePieces pieces, actions, triggers
        - models_used: Information about which models were used
    """
    # Create builder with primary model
    builder = FlowBuilder(model=primary_model)
    
    # Step 1: Analyze the request
    analysis = builder.analyze_flow_request(user_request)
    
    # Step 2: Search for components
    components = builder.search_flow_components(analysis)
    
    # Step 3: Build comprehensive plan
    # If dual models enabled and secondary model provided, create a second builder for comprehensive planning
    if use_dual_models and secondary_model:
        print(f"🔄 Using dual models: {primary_model} for analysis, {secondary_model} for planning")
        planning_builder = FlowBuilder(model=secondary_model)
        comprehensive_guide = planning_builder.build_comprehensive_plan(
            user_request, 
            analysis, 
            components, 
            user_answers
        )
    else:
        print(f"🤖 Using single model: {primary_model}")
        comprehensive_guide = builder.build_comprehensive_plan(
            user_request, 
            analysis, 
            components, 
            user_answers
        )
    
    return {
        "guide": comprehensive_guide,
        "analysis": analysis,
        "components": components,
        "models_used": {
            "primary": primary_model,
            "secondary": secondary_model if use_dual_models else None,
            "dual_mode": use_dual_models
        }
    }

