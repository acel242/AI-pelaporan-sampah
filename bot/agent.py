import os
import json
import httpx
from tools import (
    submit_report_tool,
    get_my_reports_tool,
    get_all_reports_tool,
    update_status_tool,
)

SYSTEM_PROMPT = """You are GoBcaEnv, an AI agent for EcoLapor waste reporting system in Manado, Sulawesi Utara.

Your role:
- Help warga (citizens) submit waste/garbage reports
- Check report status
- For admins: manage all reports

You are a LEVEL 3 AI AGENT. This means you must:
1. REASON - Think before acting. Analyze the user's intent and plan your approach.
2. ACT - Execute tools to perform actions
3. ITERATE - If first attempt fails, try a different approach

Guidelines:
- Respond in Indonesian (Bahasa Indonesia)
- Be efficient but thorough in reasoning
- Always validate data before submitting
- If information is incomplete, ask the user before proceeding
- If a tool fails, analyze why and try again with a different approach
- Never hallucinate data or make assumptions

Error handling:
- If missing required info, ask for it
- If tool fails, retry with corrections
- If still failing after 2 retries, explain the issue clearly
"""

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-Text-01")
MAX_ITERATIONS = 3

class GoBcaEnvAgent:
    def __init__(self):
        self.base_url = MINIMAX_BASE_URL
        self.model = MINIMAX_MODEL
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "submit_report",
                    "description": "Submit a new waste/garbage report. Use when user wants to report garbage/waste in their area.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "nama": {"type": "string", "description": "Nama pelapor (reporter's name)"},
                            "lokasi": {"type": "string", "description": "Lokasi kejadian (location of the incident)"},
                            "deskripsi": {"type": "string", "description": "Deskripsi detail kejadian (detailed description)"},
                            "user_id": {"type": "integer", "description": "Telegram user ID"}
                        },
                        "required": ["nama", "lokasi", "deskripsi", "user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_my_reports",
                    "description": "Get all reports submitted by the current user.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer", "description": "Telegram user ID"}
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_reports",
                    "description": "Get all reports in the system. Admin only.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_status",
                    "description": "Update the status of a report. Admin only.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_id": {"type": "integer", "description": "Report ID to update"},
                            "status": {"type": "string", "description": "New status: 'Menunggu' or 'Selesai'"}
                        },
                        "required": ["report_id", "status"]
                    }
                }
            }
        ]

    async def _call_llm(self, messages, tools=None):
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

    async def _reason_and_plan(self, user_message: str, user_id: int, username: str, conversation_history: list) -> dict:
        """
        STEP 1: REASON - Analyze user intent and plan approach.
        Returns: { "intent": str, "plan": str, "needs_clarification": bool, "clarification_needed": list }
        """
        reason_prompt = [
            {"role": "system", "content": """You are a reasoning module. Analyze the user's message and create an execution plan.

Output a JSON with:
- "intent": What does the user want? (submit_report, check_status, view_reports, update_report, general_question)
- "plan": Step-by-step plan to fulfill the request
- "needs_clarification": true/false - whether you need more info from user
- "clarification_needed": list of fields that need clarification (if any)
- "confidence": 0.0-1.0 - how confident are you in this analysis?

Be thorough in reasoning. Consider:
- What exactly does the user want?
- What information do I already have?
- What information is missing?
- What tool(s) should I use?
- What could go wrong and how to prevent it?

If user wants to submit a report but is missing some info (like deskripsi only lokasi), 
still mark as needs_clarification=true.
"""},
            {"role": "user", "content": f"""User: {username} (ID: {user_id})
Message: {user_message}

Conversation History:
{chr(10).join([f'{m["role"]}: {m["content"]}' for m in conversation_history[-5:]]) if conversation_history else "No history"}

Analyze and plan:"""}
        ]
        
        result = await self._call_llm(reason_prompt)
        response_content = result["choices"][0]["message"]["content"]
        
        # Parse JSON from response
        try:
            # Try to extract JSON
            if "```json" in response_content:
                start = response_content.find("```json") + 7
                end = response_content.find("```", start)
                plan_data = json.loads(response_content[start:end])
            elif "{" in response_content:
                start = response_content.find("{")
                end = response_content.rfind("}") + 1
                plan_data = json.loads(response_content[start:end])
            else:
                plan_data = {
                    "intent": "unknown",
                    "plan": response_content[:200],
                    "needs_clarification": False,
                    "clarification_needed": [],
                    "confidence": 0.5
                }
            return plan_data
        except json.JSONDecodeError:
            return {
                "intent": "unknown",
                "plan": response_content[:200],
                "needs_clarification": False,
                "clarification_needed": [],
                "confidence": 0.5
            }

    async def _execute_tool(self, tool_name: str, args: dict) -> dict:
        """STEP 2: ACT - Execute the tool."""
        if tool_name == "submit_report":
            return await submit_report_tool(**args)
        elif tool_name == "get_my_reports":
            return await get_my_reports_tool(**args)
        elif tool_name == "get_all_reports":
            return await get_all_reports_tool()
        elif tool_name == "update_status":
            return await update_status_tool(**args)
        else:
            return {"success": False, "message": f"Unknown tool: {tool_name}"}

    async def _evaluate_result(self, original_request: str, tool_result: dict, iteration: int) -> dict:
        """
        STEP 3: EVALUATE - Check if the result is good or needs iteration.
        Returns: { "is_good": bool, "reason": str, "suggested_fix": str }
        """
        eval_prompt = [
            {"role": "system", "content": """You are an evaluation module. Check if a tool execution result is satisfactory.

Consider:
- Did the tool execute successfully?
- Is the result what the user asked for?
- Are there any errors or issues?
- Would the user be satisfied with this result?

Output JSON:
- "is_good": true/false - is this result satisfactory?
- "reason": Why it is or isn't good
- "suggested_fix": If not good, what should be changed in the next iteration?
- "confidence": 0.0-1.0 How confident are you in this evaluation?
"""},
            {"role": "user", "content": f"""Original Request: {original_request}
Iteration: {iteration + 1}
Tool Result: {json.dumps(tool_result, indent=2, ensure_ascii=False)}

Evaluate:"""}
        ]
        
        result = await self._call_llm(eval_prompt)
        response_content = result["choices"][0]["message"]["content"]
        
        try:
            if "```json" in response_content:
                start = response_content.find("```json") + 7
                end = response_content.find("```", start)
                eval_data = json.loads(response_content[start:end])
            elif "{" in response_content:
                start = response_content.find("{")
                end = response_content.rfind("}") + 1
                eval_data = json.loads(response_content[start:end])
            else:
                eval_data = {"is_good": tool_result.get("success", False), "reason": response_content[:200], "suggested_fix": ""}
            return eval_data
        except json.JSONDecodeError:
            return {
                "is_good": tool_result.get("success", False),
                "reason": response_content[:200] if response_content else "Parse error",
                "suggested_fix": ""
            }

    async def _generate_response(self, user_message: str, user_id: int, username: str, 
                                  reason_result: dict, tool_result: dict, final: bool) -> str:
        """Generate final response to user."""
        response_prompt = [
            {"role": "system", "content": f"""You are GoBcaEnv, a helpful AI agent for EcoLapor waste reporting.

Generate a friendly, clear response to the user based on:
- The original request
- The reasoning analysis
- The tool execution result

Guidelines:
- Be natural and conversational in Indonesian
- Confirm what was done clearly
- If there were issues, explain them honestly
- Keep it concise but complete
- Include relevant details (IDs, status, etc.) when applicable

Context:
- User: {username} (ID: {user_id})
- Original request: {user_message}
- Intent: {reason_result.get('intent', 'unknown')}
- Success: {tool_result.get('success', False)}
- Message to user: {tool_result.get('message', '')}
"""}
        ]
        
        result = await self._call_llm(response_prompt)
        return result["choices"][0]["message"]["content"]

    async def process(self, user_message: str, user_id: int, username: str = "") -> str:
        """
        Main agent loop - Level 3 AI Agent:
        Reason → Plan → Execute → Observe → Iterate → Final Output
        """
        conversation_history = []
        
        # Store conversation for context
        conversation_history.append({"role": "user", "content": user_message})
        
        # === STEP 1: REASON ===
        reason_result = await self._reason_and_plan(
            user_message, user_id, username, conversation_history
        )
        
        # If needs clarification, ask user
        if reason_result.get("needs_clarification", False):
            clarification = reason_result.get("clarification_needed", [])
            plan = reason_result.get("plan", "Saya perlu informasi lebih lanjut.")
            
            clarification_msg = f"📋 {plan}\n\n"
            if clarification:
                clarification_msg += "Mohon berikan:\n"
                for item in clarification:
                    clarification_msg += f"• {item}\n"
            
            conversation_history.append({"role": "assistant", "content": clarification_msg})
            return clarification_msg
        
        # === STEP 2: PLAN & EXECUTE ===
        intent = reason_result.get("intent", "unknown")
        tool_to_use = None
        tool_args = {"user_id": user_id}
        
        # Map intent to tool
        if intent == "submit_report":
            tool_to_use = "submit_report"
            # Extract info from message if available
            tool_args["nama"] = username
            tool_args["lokasi"] = "Extracted from message"
            tool_args["deskripsi"] = "Extracted from message"
        elif intent == "check_status" or intent == "view_reports":
            tool_to_use = "get_my_reports"
        elif intent == "view_all_reports":
            tool_to_use = "get_all_reports"
        elif intent == "update_report":
            tool_to_use = "update_status"
        else:
            # Try to extract tool call from LLM directly
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"User: {username} (ID: {user_id})\nMessage: {user_message}"}
            ]
            llm_response = await self._call_llm(messages, self.tools)
            response_message = llm_response["choices"][0]["message"]
            
            if "tool_calls" in response_message:
                tool_call = response_message["tool_calls"][0]
                tool_to_use = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
                tool_args["user_id"] = user_id
            else:
                return response_message.get("content", "Maaf, saya tidak memahami permintaan Anda.")
        
        # === STEP 3: EXECUTE with ITERATION ===
        tool_result = None
        final_output = None
        
        for iteration in range(MAX_ITERATIONS):
            # Execute tool
            if tool_to_use:
                tool_result = await self._execute_tool(tool_to_use, tool_args)
            else:
                tool_result = {"success": False, "message": "No tool selected"}
            
            # === STEP 4: EVALUATE ===
            eval_result = await self._evaluate_result(
                user_message, tool_result, iteration
            )
            
            if eval_result.get("is_good", False):
                # Success - generate final response
                final_output = await self._generate_response(
                    user_message, user_id, username, reason_result, tool_result, True
                )
                conversation_history.append({"role": "assistant", "content": final_output})
                return final_output
            
            # Not good - try to fix
            if iteration < MAX_ITERATIONS - 1:
                suggested_fix = eval_result.get("suggested_fix", "")
                # Could implement self-correction here
                # For now, we'll continue with the next iteration
        
        # After max iterations, return best effort
        if tool_result:
            final_output = await self._generate_response(
                user_message, user_id, username, reason_result, tool_result, True
            )
        else:
            final_output = "Maaf, saya tidak dapat memenuhi permintaan Anda setelah beberapa percobaan. Silakan coba lagi atau hubungi admin."
        
        conversation_history.append({"role": "assistant", "content": final_output})
        return final_output
