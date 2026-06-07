"""
Raw API helpers for Discord Components V2.
"""
import discord

# Component type constants
TYPE_ACTION_ROW   = 1
TYPE_BUTTON       = 2
TYPE_SELECT       = 3
TYPE_SECTION      = 9
TYPE_TEXT_DISPLAY = 10
TYPE_THUMBNAIL    = 11
TYPE_SEPARATOR    = 14
TYPE_CONTAINER    = 17

BUTTON_PRIMARY   = 1
BUTTON_SECONDARY = 2
BUTTON_SUCCESS   = 3
BUTTON_DANGER    = 4
BUTTON_LINK      = 5

IS_COMPONENTS_V2 = 1 << 15


# ── Builders ────────────────────────────────────────────────

def text(content: str) -> dict:
    return {"type": TYPE_TEXT_DISPLAY, "content": content}

def separator(large=False) -> dict:
    return {"type": TYPE_SEPARATOR, "spacing": 2 if large else 1, "divider": True}

def container(*components, accent_color: int = None) -> dict:
    """Wrap components in a container (needed for image_display at top level)."""
    c = {"type": TYPE_CONTAINER, "components": list(components)}
    if accent_color:
        c["accent_color"] = accent_color
    return c

def image_display(url: str) -> dict:
    """Must be used inside a container."""
    return {"type": TYPE_THUMBNAIL, "media": {"url": url}}

def button(label: str, custom_id: str = None, style: int = BUTTON_PRIMARY,
           emoji: str = None, url: str = None, disabled: bool = False) -> dict:
    b = {"type": TYPE_BUTTON, "label": label, "style": style}
    if custom_id:
        b["custom_id"] = custom_id
    if url:
        b["url"] = url
    if emoji:
        parts = emoji.strip("<>").split(":")
        if len(parts) == 3:
            animated = parts[0] == "a"
            b["emoji"] = {"name": parts[1], "id": parts[2], "animated": animated}
        else:
            b["emoji"] = {"name": emoji}
    if disabled:
        b["disabled"] = True
    return b

def action_row(*buttons) -> dict:
    return {"type": TYPE_ACTION_ROW, "components": list(buttons)}

def section(text_content: str, thumbnail_url: str = None) -> dict:
    """Section with optional thumbnail accessory."""
    s = {
        "type": TYPE_SECTION,
        "components": [{"type": TYPE_TEXT_DISPLAY, "content": text_content}]
    }
    if thumbnail_url:
        s["accessory"] = {
            "type": TYPE_THUMBNAIL,   # must be 11
            "media": {"url": thumbnail_url}
        }
    return s

def select_menu(custom_id: str, placeholder: str, options: list) -> dict:
    return {
        "type": TYPE_ACTION_ROW,
        "components": [{
            "type": TYPE_SELECT,
            "custom_id": custom_id,
            "placeholder": placeholder,
            "options": options
        }]
    }

def select_option(label: str, value: str, description: str = None, emoji: str = None) -> dict:
    opt = {"label": label, "value": value}
    if description:
        opt["description"] = description
    if emoji:
        parts = emoji.strip("<>").split(":")
        if len(parts) == 3:
            opt["emoji"] = {"name": parts[1], "id": parts[2], "animated": parts[0] == "a"}
    return opt

def banner_container(url: str) -> dict:
    """Container with a banner image — use at top of panels."""
    return container(image_display(url))


# ── Send helpers ─────────────────────────────────────────────

async def send_v2(channel, components: list, content: str = None):
    payload = {
        "flags": IS_COMPONENTS_V2,
        "components": components,
    }
    if content:
        payload["content"] = content
    route = discord.http.Route("POST", "/channels/{channel_id}/messages",
                               channel_id=channel.id)
    return await channel._state.http.request(route, json=payload)

async def send_v2_dm(user, components: list):
    try:
        dm = await user.create_dm()
        await send_v2(dm, components)
    except Exception:
        pass

async def edit_v2(message, components: list):
    payload = {
        "flags": IS_COMPONENTS_V2,
        "components": components,
    }
    route = discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}",
                               channel_id=message.channel.id,
                               message_id=message.id)
    return await message._state.http.request(route, json=payload)

async def send_v2_interaction(interaction, components: list, ephemeral: bool = False):
    flags = IS_COMPONENTS_V2
    if ephemeral:
        flags |= 64
    payload = {
        "type": 4,
        "data": {
            "flags": flags,
            "components": components,
        }
    }
    route = discord.http.Route("POST",
                               "/interactions/{interaction_id}/{interaction_token}/callback",
                               interaction_id=interaction.id,
                               interaction_token=interaction.token)
    return await interaction._state.http.request(route, json=payload)

async def send_v2_followup(interaction, components: list, ephemeral: bool = False):
    flags = IS_COMPONENTS_V2
    if ephemeral:
        flags |= 64
    payload = {
        "flags": flags,
        "components": components,
    }
    route = discord.http.Route("POST",
                               "/webhooks/{application_id}/{interaction_token}",
                               application_id=interaction.application_id,
                               interaction_token=interaction.token)
    return await interaction._state.http.request(route, json=payload)
