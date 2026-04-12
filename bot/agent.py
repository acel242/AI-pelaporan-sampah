import os
import json
import httpx
from tools import (
    submit_report_tool,
    get_my_reports_tool,
    get_all_reports_tool,
    update_status_tool,
    set_priority_tool,
    add_note_tool,
    bulk_update_status_tool,
    get_statistics_tool,
    search_reports_tool,
    auto_respond_tool,
)

SYSTEM_PROMPT = """You are GoBcaEnv, an AI agent for EcoLapor waste reporting system in Manado, Sulawesi Utara.

Your personality:
- Efficient and to-the-point
- Friendly but professional
- Proactive in helping admins manage reports

Your role:
- Help warga (citizens) submit waste/garbage reports
- Check report status
- For admins: FULL MANAGEMENT of all reports

You are a LEVEL 3 AI AGENT with the following workflow:
1. REASON - Analyze user intent and plan approach
2. ACT - Execute tools to perform actions
3. ITERATE - If first attempt fails, try a different approach

AVAILABLE TOOLS:
- submit_report: Submit new waste report (warga)
- get_my_reports: Get citizen's own reports
- get_all_reports: Get ALL reports with filters (admin)
- update_status: Update report status - 'Menunggu', 'Diproses', 'Selesai' (admin)
- set_priority: Set report priority - 'Tinggi', 'Sedang', 'Rendah' (admin)
- add_note: Add internal note to a report (admin)
- bulk_update_status: Update multiple reports at once (admin)
- get_statistics: Get report statistics (admin)
- search_reports: Search reports by keyword (admin)
- auto_respond: Set auto-response template (admin)

Guidelines:
- Respond in Indonesian (Bahasa Indonesia)
- Always validate data before submitting
- If information is incomplete, ask before proceeding
- If a tool fails, analyze why and retry
- Admin actions require admin role check

Admin commands:
- /stats - View statistics
- /all - View all reports
- /search <query> - Search reports
- /priority <id> <Tinggi|Sedang|Rendah> - Set priority
- /note <id> <catatan> - Add note
- /bulk <ids> <status> - Bulk update
- /auto <id> <template> - Auto respond
"""

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-Text-01")
ADMIN_USER_IDS = [int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()]
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
                            "nama": {"type": "string", "description": "Nama pelapor"},
                            "lokasi": {"type": "string", "description": "Lokasi kejadian"},
                            "deskripsi": {"type": "string", "description": "Deskripsi detail kejadian"},
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
                    "description": "Get all reports with optional filters. Admin only.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "description": "Filter by status"},
                            "prioritas": {"type": "string", "description": "Filter by priority"},
                            "limit": {"type": "integer", "description": "Max results (default 50)"}
                        }
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
                            "report_id": {"type": "integer", "description": "Report ID"},
                            "status": {"type": "string", "description": "New status: Menunggu, Diproses, Selesai"}
                        },
                        "required": ["report_id", "status"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_priority",
                    "description": "Set report priority. Admin only.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_id": {"type": "integer", "description": "Report ID"},
                            "prioritas": {"type": "string", "description": "Priority: Tinggi, Sedang, Rendah"}
                        },
                        "required": ["report_id", "prioritas"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_note",
                    "description": "Add internal note to a report. Admin only.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_id": {"type": "integer", "description": "Report ID"},
                            "catatan": {"type": "string", "description": "Note content"}
                        },
                        "required": ["report_id", "catatan"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "bulk_update_status",
                    "description": "Update multiple reports at once. Admin only.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_ids": {"type": "array", "items": {"type": "integer"}, "description": "List of report IDs"},
                            "status": {"type": "string", "description": "New status"}
                        },
                        "required": ["report_ids", "status"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_statistics",
                    "description": "Get report statistics. Admin only.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_reports",
                    "description": "Search reports by keyword. Admin only.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search keyword"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "auto_respond",
                    "description": "Set auto-response template for a report. Admin only.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_id": {"type": "integer", "description": "Report ID"},
                            "template": {"type": "string", "description": "Template: accepted, processing, completed, rejected"}
                        },
                        "required": ["report_id", "template"]
                    }
                }
            }
        ]

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in ADMIN_USER_IDS

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

    async def _reason_and_plan(self, user_message: str, user_id: int, username: str, is_admin: bool, conversation_history: list) -> dict:
        """STEP 1: Analyze user intent and plan approach."""
        admin_context = "User adalah ADMIN." if is_admin else "User adalah WARGA biasa."
        
        reason_prompt = [
            {"role": "system", "content": f"""You are a reasoning module. Analyze the user's message and create an execution plan.

Output a JSON with:
- "intent": What does the user want?
- "plan": Step-by-step plan
- "needs_clarification": true/false
- "clarification_needed": list of missing info
- "confidence": 0.0-1.0

{admin_context}

Intents:
- submit_report: User wants to file a waste report
- check_status: User wants to check their report status
- view_reports: User wants to see their own reports
- view_all_reports: Admin wants to see ALL reports (admin only)
- update_status: Admin wants to change report status
- set_priority: Admin wants to set report priority
- add_note: Admin wants to add note to report
- bulk_update: Admin wants to bulk update reports
- get_stats: Admin wants statistics
- search: Admin wants to search reports
- auto_respond: Admin wants to set auto-response
- unknown: Can't determine intent

If user is warga and tries admin-only action, deny politely."""},
            {"role": "user", "content": f"""User: {username} (ID: {user_id})
Is Admin: {is_admin}
Message: {user_message}

History:
{chr(10).join([f'{m["role"]}: {m["content"]}' for m in conversation_history[-3:]]) if conversation_history else "No history"}

Analyze:"""}
        ]
        
        result = await self._call_llm(reason_prompt)
        response_content = result["choices"][0]["message"]["content"]
        
        try:
            if "```json" in response_content:
                start = response_content.find("```json") + 7
                end = response_content.find("```", start)
                plan_data = json.loads(response_content[start:end])
            elif "{" in response_content:
                start = response_content.find("{")
                end = response_content.rfind("}") + 1
                plan_data = json.loads(response_content[start:end])
            else:
                plan_data = {"intent": "unknown", "plan": response_content[:200], "needs_clarification": False, "clarification_needed": [], "confidence": 0.5}
            return plan_data
        except json.JSONDecodeError:
            return {"intent": "unknown", "plan": response_content[:200], "needs_clarification": False, "clarification_needed": [], "confidence": 0.5}

    async def _execute_tool(self, tool_name: str, args: dict) -> dict:
        """STEP 2: Execute the tool."""
        tool_map = {
            "submit_report": submit_report_tool,
            "get_my_reports": get_my_reports_tool,
            "get_all_reports": get_all_reports_tool,
            "update_status": update_status_tool,
            "set_priority": set_priority_tool,
            "add_note": add_note_tool,
            "bulk_update_status": bulk_update_status_tool,
            "get_statistics": get_statistics_tool,
            "search_reports": search_reports_tool,
            "auto_respond": auto_respond_tool,
        }
        
        tool_func = tool_map.get(tool_name)
        if not tool_func:
            return {"success": False, "message": f"Unknown tool: {tool_name}"}
        
        try:
            return await tool_func(**args)
        except Exception as e:
            return {"success": False, "message": f"Tool error: {str(e)}"}

    async def _generate_response(self, user_message: str, user_id: int, username: str, 
                                  reason_result: dict, tool_result: dict) -> str:
        """Generate final response to user."""
        response_prompt = [
            {"role": "system", "content": f"""You are GoBcaEnv, a helpful AI agent for EcoLapor waste reporting.

Generate a friendly, clear response based on tool execution result.

Guidelines:
- Be natural and conversational in Indonesian
- Confirm what was done clearly
- Include relevant IDs and details
- If error, explain honestly
- Keep concise but complete

Success: {tool_result.get('success', False)}
Message: {tool_result.get('message', '')}
Original request: {user_message}
Intent: {reason_result.get('intent', 'unknown')}
"""}
        ]
        
        result = await self._call_llm(response_prompt)
        return result["choices"][0]["message"]["content"]

    async def process(self, user_message: str, user_id: int, username: str = "") -> str:
        """Main agent loop - Level 3: Reason → Plan → Execute → Evaluate → Iterate"""
        is_admin = self.is_admin(user_id)
        conversation_history = []
        conversation_history.append({"role": "user", "content": user_message})
        
        # STEP 1: REASON
        reason_result = await self._reason_and_plan(
            user_message, user_id, username, is_admin, conversation_history
        )
        
        # Handle clarification
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
        
        # STEP 2: MAP INTENT TO TOOL
        intent = reason_result.get("intent", "unknown")
        tool_name = None
        tool_args = {"user_id": user_id}
        
        # Admin-only intents
        admin_intents = ["view_all_reports", "update_status", "set_priority", "add_note", 
                         "bulk_update", "get_stats", "search", "auto_respond"]
        
        if intent in admin_intents and not is_admin:
            return "❌ Maaf, perintah ini hanya untuk admin. Hubungi admin jika Anda perlu bantuan."
        
        # Map intent to tool
        intent_to_tool = {
            "submit_report": "submit_report",
            "check_status": "get_my_reports",
            "view_reports": "get_my_reports",
            "view_all_reports": "get_all_reports",
            "update_status": "update_status",
            "set_priority": "set_priority",
            "add_note": "add_note",
            "bulk_update": "bulk_update_status",
            "get_stats": "get_statistics",
            "search": "search_reports",
            "auto_respond": "auto_respond",
        }
        
        tool_name = intent_to_tool.get(intent)
        
        # If unknown intent, try direct tool extraction from LLM
        if not tool_name:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"User: {username} (ID: {user_id})\nIs Admin: {is_admin}\nMessage: {user_message}"}
            ]
            llm_response = await self._call_llm(messages, self.tools)
            response_message = llm_response["choices"][0]["message"]
            
            if "tool_calls" in response_message:
                tool_call = response_message["tool_calls"][0]
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
                tool_args["user_id"] = user_id
            else:
                content = response_message.get("content", "")
                if content:
                    conversation_history.append({"role": "assistant", "content": content})
                    return content
                return "Maaf, saya tidak memahami permintaan Anda. Ketik /help untuk bantuan."
        
        # STEP 3: EXECUTE with iteration
        tool_result = None
        
        for iteration in range(MAX_ITERATIONS):
            tool_result = await self._execute_tool(tool_name, tool_args)
            
            if tool_result.get("success", False):
                break
            
            if iteration < MAX_ITERATIONS - 1:
                # Could implement self-correction here
                continue
        
        # STEP 4: GENERATE RESPONSE
        if tool_result:
            final_output = await self._generate_response(
                user_message, user_id, username, reason_result, tool_result
            )
        else:
            final_output = "Maaf, saya tidak dapat memenuhi permintaan Anda setelah beberapa percobaan. Silakan coba lagi."
        
        conversation_history.append({"role": "assistant", "content": final_output})
        return final_output
