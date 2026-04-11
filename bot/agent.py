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

Guidelines:
- Respond in Indonesian (Bahasa Indonesia)
- Be efficient and concise
- Ask clarifying questions only if essential
- Confirm data before submitting reports
- If user wants to submit a report, get: nama, lokasi, deskripsi
- If user asks about status/history, use get_my_reports_tool
- If admin asks for all reports, use get_all_reports_tool
- If admin wants to update status, use update_status_tool

Error handling:
- If missing required info, ask for it
- If tool fails, explain error clearly
- Never hallucinate data
"""

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-Text-01")

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

    async def process(self, user_message: str, user_id: int, username: str = "") -> str:
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"User: {username} (ID: {user_id})\nMessage: {user_message}"}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "auto"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
        
        response_message = data["choices"][0]["message"]
        
        if "tool_calls" in response_message:
            tool_results = []
            for tool_call in response_message["tool_calls"]:
                func_name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                args["user_id"] = user_id

                if func_name == "submit_report":
                    result = await submit_report_tool(**args)
                elif func_name == "get_my_reports":
                    result = await get_my_reports_tool(**args)
                elif func_name == "get_all_reports":
                    result = await get_all_reports_tool()
                elif func_name == "update_status":
                    result = await update_status_tool(**args)
                else:
                    result = {"success": False, "message": f"Unknown function: {func_name}"}

                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result)
                })

            messages.append(response_message)
            messages.extend(tool_results)

            payload["messages"] = messages
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                final_response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                final_response.raise_for_status()
                final_data = final_response.json()
            
            return final_data["choices"][0]["message"]["content"]
        
        return response_message.get("content", "Maaf, tidak ada respons.")
