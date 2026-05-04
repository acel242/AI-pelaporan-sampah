import os
import json
import re
import httpx
import logging
import database as db

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are EcoLapor AI, a friendly assistant for environmental reporting in Manado, Sulawesi Utara.

PERSONALITY: Warm, patient, never gives up. Like a helpful neighbor who genuinely wants to understand and help.

Language: ALWAYS respond in Indonesian (Bahasa Indonesia).

SELF-IMPROVING RULES (CRITICAL - follow in order):

1. APA YANG DIMAKSUD? (Ask first)
   - Kalau tidak mengerti atau tidak yakin → SELALU tanya balik dengan spesifik
   - JANGAN pernah langsung bilang "maaf terjadi kesalahan" atau "saya tidak tahu"

2. GUNAKAN TOOL until jelas
   - Kalau user minta sesuatu → coba gunakan tool
   - Kalau tool memberi hasil tidak sesuai → tanyakan apa yang user maksud

3. KALAU TIDAK ADA TOOL UNTUK ITU
   - Jangan error! Jawab dengan pengetahuan kamu
   - Kalau out of scope → ajak bicara terus

4. JANGAN MUNAFIK
   - Jangan bilang "saya tidak bisa" padahal bisa
   - Selalu coba dulu sebelum bilang tidak bisa

5. HELPFUL CLOSING
   - Akhiri dengan pertanyaan kembali atau ajakan

CATEGORIES: EcoLapor menerima laporan isu lingkungan:
- 🗑️ Sampah — tumpukan sampah, limbah, plastik, organik, B3
- 🔧 Fasilitas Rusak — taman rusak, lampu mati, trotoar
- 🐕 Hewan Liar — hewan terlantar/sakit/berbahaya
- 🔥 Kebakaran — kebakaran hutan/lahan
- 📌 Lainnya — isu lingkungan umum

TOOL USAGE:
- submit_report: Submit new environmental report (needs: nama, lokasi, deskripsi, user_id, kategori)
- get_my_reports: Get user's own reports
- get_all_reports: Admin only - get all reports
- update_status: Admin only - change report status
- set_priority: Admin only - set priority
- add_note: Admin only - add note
- bulk_update_status: Admin only - bulk update
- get_statistics: Admin only - get stats
- search_reports: Admin only - search
- auto_respond: Admin only - auto response
- learn_memory: Store new fact
- search_memory: Search learned facts

REASONING:
1. User said apa? → understand the intent
2. Is this an environmental issue? → categorize it
3. Do I have a tool for this? → call it
4. Did it work? → if no, ask clarifying question
5. Respond with helpful closing question
"""

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
ADMIN_USER_IDS = [int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()]

# ─── Smart Agent ───────────────────────────────────────────────────────────────

class SmartAgent:
    def __init__(self):
        self.openrouter_url = OPENROUTER_BASE_URL
        self.openrouter_model = OPENROUTER_MODEL
        self.openrouter_key = OPENROUTER_API_KEY
        self.groq_url = GROQ_BASE_URL
        self.groq_model = GROQ_MODEL
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "submit_report",
                    "description": "Submit a new environmental report (sampah, banjir, pencemaran, dll).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "nama": {"type": "string"},
                            "lokasi": {"type": "string"},
                            "deskripsi": {"type": "string"},
                            "user_id": {"type": "integer"},
                            "kategori": {"type": "string", "enum": ["Sampah", "Fasilitas Rusak", "Hewan Liar", "Kebakaran", "Lainnya"], "description": "Kategori laporan lingkungan"}
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
                        "properties": {"user_id": {"type": "integer"}},
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
                            "status": {"type": "string"},
                            "prioritas": {"type": "string"},
                            "limit": {"type": "integer"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_status",
                    "description": "Update report status. Admin only.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_id": {"type": "integer"},
                            "status": {"type": "string"}
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
                            "report_id": {"type": "integer"},
                            "prioritas": {"type": "string"}
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
                            "report_id": {"type": "integer"},
                            "catatan": {"type": "string"}
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
                            "report_ids": {"type": "array", "items": {"type": "integer"}},
                            "status": {"type": "string"}
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
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "auto_respond",
                    "description": "Set auto-response template. Admin only.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_id": {"type": "integer"},
                            "template": {"type": "string"}
                        },
                        "required": ["report_id", "template"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "learn_memory",
                    "description": "Store a new fact in memory for future reference.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keyword": {"type": "string"},
                            "fact": {"type": "string"},
                            "user_id": {"type": "integer"}
                        },
                        "required": ["keyword", "fact", "user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_memory",
                    "description": "Search previously learned facts.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "user_id": {"type": "integer"}
                        },
                        "required": ["query", "user_id"]
                    }
                }
            }
        ]

    def is_admin(self, user_id: int) -> bool:
        return user_id in ADMIN_USER_IDS

    async def _call_llm(self, messages, tools=None):
        """Call LLM with Deepseek primary, Groq fallback."""
        payload_base = {
            "messages": messages,
            "temperature": 0.7,
        }
        if tools:
            payload_base["tools"] = tools
            payload_base["tool_choice"] = "auto"

        # Try Sumodop first
        try:
            payload_sumodop = {"model": self.sumodop_model, **payload_base}
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.sumodop_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.sumodop_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload_sumodop
                )
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Sumodop API error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.warning(f"Sumodop call failed: {e}, trying Groq")

        # Fallback to Groq
        payload_groq = {"model": self.groq_model, **payload_base}
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.groq_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=payload_groq
                )
                if response.status_code != 200:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    raise Exception(f"Groq API error: {response.status_code}")
                return response.json()
        except httpx.TimeoutException:
            raise Exception("Timeout - coba lagi")
        except Exception as e:
            logger.error(f"LLM call failed (both providers): {e}")
            raise

    async def _generate_response(self, tool_result: dict) -> str:
        success = tool_result.get("success", False)
        message = tool_result.get("message", "")
        if success:
            return message
        else:
            return f"❌ {message}"

    async def process(self, user_message: str, user_id: int, username: str = "") -> str:
        is_admin = self.is_admin(user_id)

        # Step 1: Pre-search memory
        memory_context = ""
        try:
            memories = await db.search_conv_memory(user_id, user_message)
            if memories:
                memory_lines = [f"- {kw}: {fact}" for kw, fact in memories[:5]]
                memory_context = "\nLEARNED FACTS FROM THIS USER:\n" + "\n".join(memory_lines)
        except Exception as e:
            logger.warning(f"Memory search failed: {e}")

        # Step 2: Build messages — include role so LLM picks correct tool
        role_label = "ADMIN" if is_admin else "WARGA"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + memory_context},
            {"role": "user", "content": f"User: {username or 'anon'} (ID: {user_id}) | ROLE: {role_label}\nPesan: {user_message}"}
        ]

        try:
            # Step 3: Get LLM decision (may call tools)
            llm_response = await self._call_llm(messages, self.tools)
            response_message = llm_response["choices"][0]["message"]

            if "tool_calls" in response_message:
                for tool_call in response_message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])
                    # Only pass user_id to tools that accept it
                    tools_needing_user_id = {
                        "submit_report", "get_my_reports", "search_memory"
                    }
                    if tool_name not in tools_needing_user_id:
                        tool_args.pop("user_id", None)

                    # Admin-only check
                    admin_tools = ["get_all_reports", "update_status", "set_priority",
                                   "add_note", "bulk_update_status", "get_statistics",
                                   "search_reports", "auto_respond"]
                    if tool_name in admin_tools and not is_admin:
                        return "❌ Maaf, perintah ini hanya untuk admin."

                    # Route tool calls
                    if tool_name == "learn_memory":
                        await db.add_conv_memory(
                            tool_args["user_id"],
                            tool_args["keyword"],
                            tool_args["fact"]
                        )
                        return f"✅ Baik, saya akan mengingat: {tool_args['fact']}"

                    elif tool_name == "search_memory":
                        results = await db.search_conv_memory(
                            tool_args["user_id"],
                            tool_args["query"]
                        )
                        if results:
                            lines = [f"- {kw}: {fact}" for kw, fact in results]
                            return "Saya menemukan dalam memory:\n" + "\n".join(lines)
                        return "Tidak ada yang ditemukan dalam memory saya."

                    else:
                        # Route to tools.py
                        from tools import (
                            submit_report_tool, get_my_reports_tool,
                            get_all_reports_tool, update_status_tool,
                            set_priority_tool, add_note_tool,
                            bulk_update_status_tool, get_statistics_tool,
                            search_reports_tool, auto_respond_tool,
                        )
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
                            return f"❌ Tool tidak ditemukan: {tool_name}"
                        tool_result = await tool_func(**tool_args)
                        return await self._generate_response(tool_result)

            else:
                # No tool call - plain text response
                content = response_message.get("content", "").strip()
                if content:
                    return content
                return "Saya paham. Ada yang bisa saya bantu lagi?"

        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return (
                "Hmm, saya mau bantu tapi ada sesuatu yang tidak saya pahami. "
                "Bisa dijelaskan lagi dengan kata-kata berbeda? "
                "Atau mungkin anda bisa menyebut nomor laporan atau lokasi spesifik yang anda maksud?"
            )
