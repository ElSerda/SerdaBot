"""Tool executor for proactive routing.

This module centralizes the execution of all tools via dynamic imports.
Each tool corresponds to a bot command but can be invoked programmatically.
"""

import importlib
import json
from pathlib import Path


TOOLS_REGISTRY_PATH = Path(__file__).parent.parent.parent.parent / "config" / "tools_registry.json"


class ToolExecutor:
    """Executes tools via dynamic import and returns formatted results."""
    
    def __init__(self, config: dict):
        """Initialize the tool executor.
        
        Args:
            config: Bot configuration dictionary
        """
        self.config = config
        with open(TOOLS_REGISTRY_PATH, "r", encoding="utf-8") as f:
            self.registry = json.load(f)
    
    async def execute_tool(self, tool_name: str, args: dict) -> str:
        """Execute a tool and return the formatted result.
        
        Args:
            tool_name: Name of the tool to execute (ex: "gameinfo")
            args: Arguments for the tool (ex: {"game_name": "Zelda"})
            
        Returns:
            Formatted string result from the tool execution
            
        Example:
            result = await tool_executor.execute_tool("gameinfo", {"game_name": "Zelda"})
        """
        debug = self.config.get("bot", {}).get("debug", False)
        
        if tool_name not in self.registry:
            return f"⚠️ Outil inconnu : {tool_name}"
        
        tool_config = self.registry[tool_name]
        
        if debug:
            print(f"[TOOL_EXECUTOR] 🔧 Executing {tool_name} with args: {args}")
        
        try:
            # Import dynamique du module
            module = importlib.import_module(tool_config["module"])
            func = getattr(module, tool_config["function"])
            
            # Extraction des arguments selon le type
            args_type = tool_config.get("args_type", "none")
            
            if args_type == "game_name":
                result = await func(args.get("game_name", ""))
            elif args_type == "question":
                result = await func(args.get("question", ""))
            elif args_type == "none":
                result = await func()
            else:
                # Fallback : passer tous les args
                result = await func(**args)
            
            if debug:
                print(f"[TOOL_EXECUTOR] ✅ {tool_name} executed successfully")
            
            return result
        
        except Exception as e:
            error_msg = f"❌ Erreur outil `{tool_name}` : {str(e)[:100]}"
            if debug:
                print(f"[TOOL_EXECUTOR] {error_msg}")
            return error_msg
