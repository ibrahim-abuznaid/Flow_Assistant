"""
Flow Builder - Specialized module for building comprehensive ActivePieces workflows.
This module provides intelligent flow building with clarification questions and detailed plans.
"""
import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from openai import OpenAI
from src.tools import find_piece_by_name, get_vector_store, web_search

load_dotenv()


class FlowBuilder:
    """
    Specialized flow builder that creates comprehensive, step-by-step workflow guides.
    Uses GPT-5 for advanced reasoning about workflow construction.
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
    
    def analyze_flow_request(self, user_request: str) -> Dict[str, Any]:
        """
        Analyze the user's flow request to understand what they want to build.
        
        Args:
            user_request: The user's flow building request
            
        Returns:
            Dictionary with flow analysis and clarification questions
        """
        analysis_prompt = f"""You are an expert workflow automation analyst for ActivePieces.

Analyze this flow building request and determine:
1. What the user wants to accomplish (trigger → actions)
2. What information is clear vs unclear
3. What clarifying questions would help (max 3, keep them optional)
4. The complexity level of the flow

User Request: "{user_request}"

Respond in this exact JSON format:
{{
  "flow_goal": "brief description of what user wants to accomplish",
  "trigger_type": "identified trigger or 'unclear'",
  "actions_needed": ["action 1", "action 2", ...],
  "is_clear": true/false,
  "missing_info": ["piece 1", "piece 2", ...],
  "clarifying_questions": [
    {{
      "question": "specific question",
      "purpose": "why this helps",
      "optional": true
    }}
  ],
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
  "clarifying_questions": [
    {{
      "question": "Do you want to filter for specific file types or folders?",
      "purpose": "To set up trigger filters if needed",
      "optional": true
    }},
    {{
      "question": "Should the email include the file link or content?",
      "purpose": "To configure email body properly",
      "optional": true
    }}
  ],
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
  "clarifying_questions": [
    {{
      "question": "How do new customers enter your system? (e.g., form submission, Stripe payment, CRM entry)",
      "purpose": "To identify the right trigger",
      "optional": false
    }},
    {{
      "question": "What are the main steps in your onboarding? (e.g., send welcome email, create account, add to CRM)",
      "purpose": "To identify required actions",
      "optional": false
    }},
    {{
      "question": "Which tools/platforms do you use? (e.g., Mailchimp, Slack, Google Sheets)",
      "purpose": "To verify available integrations",
      "optional": true
    }}
  ],
  "complexity": "complex",
  "confidence": "low"
}}

Now analyze the user's request above."""

        try:
            response = self.client.responses.create(
                model=self.model,
                input=analysis_prompt,
                reasoning={"effort": "medium"},
                text={"verbosity": "medium"}
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
                "clarifying_questions": [],
                "complexity": "moderate",
                "confidence": "medium"
            }
    
    def search_flow_components(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for the pieces, triggers, and actions needed for the flow.
        
        Args:
            analysis: The flow analysis from analyze_flow_request
            
        Returns:
            Dictionary with found components and their details
        """
        components = {
            "trigger": None,
            "actions": [],
            "pieces": [],
            "missing": []
        }
        
        # Search for trigger piece
        if analysis.get("trigger_type") and analysis["trigger_type"] != "unclear":
            trigger_keywords = analysis["trigger_type"].split(" - ")[0] if " - " in analysis["trigger_type"] else analysis["trigger_type"]
            trigger_piece = find_piece_by_name(trigger_keywords)
            
            if trigger_piece:
                components["trigger"] = {
                    "piece": trigger_piece,
                    "trigger_type": analysis["trigger_type"]
                }
                components["pieces"].append(trigger_piece)
            else:
                components["missing"].append(f"Trigger: {trigger_keywords}")
        
        # Search for action pieces
        for action in analysis.get("actions_needed", []):
            if action and action != "unclear - depends on onboarding steps":
                # Extract piece name from action description
                action_keywords = action.split(" ")[0:3]  # Take first few words
                action_piece = find_piece_by_name(" ".join(action_keywords))
                
                if action_piece:
                    components["actions"].append({
                        "piece": action_piece,
                        "action_description": action
                    })
                    if action_piece not in components["pieces"]:
                        components["pieces"].append(action_piece)
                else:
                    components["missing"].append(f"Action: {action}")
        
        # Search knowledge base for additional context
        try:
            vector_store = get_vector_store()
            search_query = f"{analysis.get('flow_goal', '')} {analysis.get('trigger_type', '')} {' '.join(analysis.get('actions_needed', []))}"
            results = vector_store.similarity_search(search_query, k=3)
            
            components["knowledge_context"] = [doc.page_content for doc in results] if results else []
        except Exception as e:
            print(f"⚠️  Knowledge base search error: {e}")
            components["knowledge_context"] = []
        
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
            user_answers: Optional answers to clarifying questions
            
        Returns:
            Comprehensive flow building guide
        """
        # Prepare context for the planner
        context = f"""
USER REQUEST: {user_request}

FLOW ANALYSIS:
- Goal: {analysis.get('flow_goal', 'Unknown')}
- Trigger: {analysis.get('trigger_type', 'Unknown')}
- Actions: {', '.join(analysis.get('actions_needed', []))}
- Complexity: {analysis.get('complexity', 'Unknown')}

FOUND COMPONENTS:
"""
        
        # Add trigger information
        if components.get("trigger") and components["trigger"].get("piece"):
            trigger_piece = components["trigger"]["piece"]
            context += f"\n✓ TRIGGER PIECE: {trigger_piece.get('displayName', 'Unknown')}\n"
            context += f"  Description: {trigger_piece.get('description', 'N/A')}\n"
            
            triggers = trigger_piece.get('triggers', [])
            if triggers:
                context += f"  Available Triggers ({len(triggers)}):\n"
                for t in triggers[:3]:
                    context += f"    - {t.get('displayName', 'Unknown')}: {t.get('description', 'N/A')}\n"
        
        # Add action information
        if components.get("actions"):
            context += f"\n✓ ACTION PIECES:\n"
            for action_info in components["actions"]:
                piece = action_info.get("piece")
                if piece:
                    context += f"\n  {piece.get('displayName', 'Unknown')}\n"
                    context += f"  Description: {piece.get('description', 'N/A')}\n"
                    
                    actions = piece.get('actions', [])
                    if actions:
                        context += f"  Available Actions ({len(actions)}):\n"
                        for a in actions[:3]:
                            context += f"    - {a.get('displayName', 'Unknown')}: {a.get('description', 'N/A')}\n"
        
        # Add knowledge base context
        if components.get("knowledge_context"):
            context += f"\n✓ ADDITIONAL CONTEXT FROM KNOWLEDGE BASE:\n"
            for kb_item in components["knowledge_context"][:2]:
                context += f"  - {kb_item[:200]}...\n"
        
        # Add user answers if provided
        if user_answers:
            context += f"\n✓ USER PROVIDED ADDITIONAL INFO:\n{user_answers}\n"
        
        # Add missing components
        if components.get("missing"):
            context += f"\n⚠️  MISSING/UNCLEAR COMPONENTS:\n"
            for missing in components["missing"]:
                context += f"  - {missing}\n"
        
        # Build the comprehensive plan
        planning_prompt = f"""You are an expert ActivePieces workflow architect. Create a COMPREHENSIVE, DETAILED, and ACTIONABLE flow building guide.

{context}

Create a powerful, step-by-step guide that includes:
1. **Flow Overview** - What this flow does and why
2. **Prerequisites** - What the user needs before starting
3. **Step-by-Step Instructions** - DETAILED steps with ALL required inputs
4. **Trigger Configuration** - Exact settings, all input fields, authentication
5. **Action Configuration** - For EACH action, list ALL inputs (required & optional)
6. **Testing & Validation** - How to test the flow
7. **Common Issues & Solutions** - Potential problems and fixes
8. **Pro Tips** - Advanced configurations or optimizations

CRITICAL REQUIREMENTS:
- List ALL input properties for each trigger/action (don't say "configure" - tell them EXACTLY what to configure)
- Include authentication requirements
- Provide example values where helpful
- Be specific about data mapping between steps
- If information is missing, search online or provide best practices
- Make it so detailed that a beginner can follow it perfectly

Format your response in clear markdown with headers, bullet points, and code blocks where appropriate.
Make this the MOST COMPREHENSIVE flow guide possible - the user should be able to build this flow by following your guide step-by-step.
"""

        try:
            # Use web search if we have missing components or need more details
            if components.get("missing") or analysis.get("confidence") == "low":
                search_results = self._search_for_missing_info(analysis, components)
                planning_prompt += f"\n\nADDITIONAL RESEARCH FROM WEB:\n{search_results}\n"
            
            # Generate comprehensive plan
            response = self.client.responses.create(
                model="gpt-5" if analysis.get("complexity") == "complex" else self.model,
                input=planning_prompt,
                reasoning={"effort": "high"},  # High effort for detailed planning
                text={"verbosity": "high"}  # High verbosity for comprehensive output
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
        plan = f"# Flow Building Guide: {analysis.get('flow_goal', user_request)}\n\n"
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
        plan += "1. Log into your ActivePieces instance\n"
        plan += "2. Create a new flow\n"
        plan += "3. Add and configure the trigger\n"
        plan += "4. Add and configure the actions\n"
        plan += "5. Test your flow\n"
        
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


def build_flow(user_request: str, user_answers: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function to build a comprehensive flow guide.
    
    Args:
        user_request: The user's flow building request
        user_answers: Optional answers to clarifying questions
        
    Returns:
        Dictionary with flow guide and metadata
    """
    builder = get_flow_builder()
    
    # Step 1: Analyze the request
    analysis = builder.analyze_flow_request(user_request)
    
    # Step 2: Search for components
    components = builder.search_flow_components(analysis)
    
    # Step 3: Build comprehensive plan
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
        "clarifying_questions": analysis.get("clarifying_questions", [])
    }

