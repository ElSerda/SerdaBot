"""Roast Manager - Manage dynamic roast targets and quotes."""

import json
import os
from typing import Dict, List, Optional

from twitchio.ext import commands

DEFAULT_PATH = "config/roast.json"
MAX_USERS = 200
MAX_QUOTES = 200
MAX_QUOTE_LEN = 180


def _norm(u: str) -> str:
    """Normalize username to lowercase."""
    return u.strip().lower()


def load_roast_config(path: str = DEFAULT_PATH) -> Dict[str, List[str]]:
    """Load roast configuration from JSON file."""
    if not os.path.exists(path):
        return {"users": [], "quotes": []}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("users", [])
    data.setdefault("quotes", [])
    return data


def save_roast_config(data: Dict[str, List[str]], path: str = DEFAULT_PATH):
    """Save roast configuration to JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class RoastManager(commands.Cog):
    """Cog for managing roast targets and quotes."""

    def __init__(self, bot: commands.Bot, path: str = DEFAULT_PATH):
        self.bot = bot
        self.path = path
        self.data = load_roast_config(self.path)

    def _is_mod(self, ctx: commands.Context) -> bool:
        """Check if user is mod or broadcaster."""
        return getattr(ctx.author, "is_mod", False) or getattr(
            ctx.author, "is_broadcaster", False
        )

    @commands.command(name="addroast")
    async def add_roast_user(self, ctx: commands.Context, username: Optional[str] = None):
        """Add a user to the roast list (mod only)."""
        if not self._is_mod(ctx):
            return
        if not username:
            return await ctx.send("Usage: !addroast <username>")

        u = _norm(username)
        users = set(map(_norm, self.data["users"]))

        if len(users) >= MAX_USERS:
            return await ctx.send(
                "Limite atteinte (users). Supprime quelqu'un avec !delroast."
            )
        if u in users:
            return await ctx.send(f"{username} est déjà roastable.")

        users.add(u)
        self.data["users"] = sorted(users)
        save_roast_config(self.data, self.path)
        await ctx.send(f"{username} ajouté à la liste roast ✅")

    @commands.command(name="delroast")
    async def del_roast_user(self, ctx: commands.Context, username: Optional[str] = None):
        """Remove a user from the roast list (mod only)."""
        if not self._is_mod(ctx):
            return
        if not username:
            return await ctx.send("Usage: !delroast <username>")

        u = _norm(username)
        users = set(map(_norm, self.data["users"]))

        if u not in users:
            return await ctx.send(f"{username} n'est pas dans la liste.")

        users.remove(u)
        self.data["users"] = sorted(users)
        save_roast_config(self.data, self.path)
        await ctx.send(f"{username} retiré de la liste roast ✅")

    @commands.command(name="listroast")
    async def list_roast_users(self, ctx: commands.Context):
        """List all roast targets (mod only)."""
        if not self._is_mod(ctx):
            return

        users = self.data.get("users", [])
        if not users:
            return await ctx.send("Aucun utilisateur roastable.")

        preview = ", ".join(users[:15]) + ("…" if len(users) > 15 else "")
        await ctx.send(f"Roastables ({len(users)}): {preview}")

    @commands.command(name="addquote")
    async def add_quote(self, ctx: commands.Context, *, text: Optional[str] = None):
        """Add a roast quote (mod only)."""
        if not self._is_mod(ctx):
            return
        if not text:
            return await ctx.send("Usage: !addquote <phrase>")

        text = text.strip()
        if len(text) > MAX_QUOTE_LEN:
            return await ctx.send(f"Max {MAX_QUOTE_LEN} caractères.")

        quotes = self.data.get("quotes", [])
        if len(quotes) >= MAX_QUOTES:
            return await ctx.send(
                "Limite atteinte (quotes). Supprime avec !delquote."
            )
        if text in quotes:
            return await ctx.send("Déjà enregistrée.")

        quotes.append(text)
        self.data["quotes"] = quotes
        save_roast_config(self.data, self.path)
        await ctx.send("Citation ajoutée ✅")

    @commands.command(name="delquote")
    async def del_quote(self, ctx: commands.Context, index: Optional[str] = None):
        """Delete a quote by index (mod only)."""
        if not self._is_mod(ctx):
            return
        if not index or not index.isdigit():
            return await ctx.send("Usage: !delquote <index> (voir !listquotes)")

        i = int(index)
        quotes = self.data.get("quotes", [])

        if not 0 <= i < len(quotes):
            return await ctx.send("Index invalide.")

        removed = quotes.pop(i)
        self.data["quotes"] = quotes
        save_roast_config(self.data, self.path)
        await ctx.send(
            f"Supprimée: {removed[:40]}{'…' if len(removed)>40 else ''}"
        )

    @commands.command(name="listquotes")
    async def list_quotes(self, ctx: commands.Context):
        """List all roast quotes (mod only)."""
        if not self._is_mod(ctx):
            return

        quotes = self.data.get("quotes", [])
        if not quotes:
            return await ctx.send("Aucune citation.")

        head = " | ".join(
            f"[{i}] {q[:30]}{'…' if len(q)>30 else ''}"
            for i, q in enumerate(quotes[:5])
        )
        tail = f" (+{len(quotes)-5} de plus)" if len(quotes) > 5 else ""
        await ctx.send(f"Quotes: {head}{tail}")


def prepare(bot: commands.Bot, path: str = DEFAULT_PATH):
    """Register the RoastManager cog."""
    bot.add_cog(RoastManager(bot, path))
