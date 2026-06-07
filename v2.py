import discord

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

# ── Colors ───────────────────────────────────────────────────
COLOR_BLUE   = 0x5865F2  # logs γενικά
COLOR_GREEN  = 0x57F287  # join, success, check
COLOR_RED    = 0xED4245  # leave, ban, error
COLOR_YELLOW = 0xFEE75C  # edit, warn
COLOR_PURPLE = 0x9B59B6  # role
COLOR_ORANGE = 0xE67E22  # voice
COLOR_WHITE  = 0xFFFFFF  # say2, invite
COLOR_PINK   = 0xEB459E  # boost, donate
COLOR_GOLD   = 0xF1C40F  # billing, review


def text(content: str) -> dict:
    return {"type": TYPE_TEXT_DISPLAY, "content": content}

def separator(large=False) -> dict:
    return {"type": TYPE_SEPARATOR, "spacing": 2 if large else 1, "divider": True}

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
            b["emoji"] = {"name": parts[1], "id": parts[2], "animated": parts[0] == "a"}
        else:
            b["emoji"] = {"name": emoji}
    if disabled:
        b["disabled"] = True
    return b

def action_row(*buttons) -> dict:
    return {"type": TYPE_ACTION_ROW, "components": list(buttons)}

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

def section(text_content: str, thumbnail_url: str = None) -> dict:
    s = {
        "type": TYPE_SECTION,
        "components": [{"type": TYPE_TEXT_DISPLAY, "content": text_content}]
    }
    if thumbnail_url:
        s["accessory"] = {
            "type": TYPE_THUMBNAIL,
            "media": {"url": thumbnail_url}
        }
    return s

def panel(text_content: str, thumbnail_url: str = None, color: int = COLOR_BLUE) -> dict:
    """Embed-style panel με χρωματιστή μπάρα αριστερά + thumbnail."""
    inner = {
        "type": TYPE_SECTION,
        "components": [{"type": TYPE_TEXT_DISPLAY, "content": text_content}]
    }
    if thumbnail_url:
        inner["accessory"] = {
            "type": TYPE_THUMBNAIL,
            "media": {"url": thumbnail_url}
        }
    return {
        "type": TYPE_CONTAINER,
        "accent_color": color,
        "components": [inner]
    }

def panel_with_buttons(text_content: str, buttons_row: dict,
                       thumbnail_url: str = None, color: int = COLOR_BLUE) -> dict:
    """Panel με χρώμα + thumbnail + buttons μέσα στο container."""
    inner = {
        "type": TYPE_SECTION,
        "components": [{"type": TYPE_TEXT_DISPLAY, "content": text_content}]
    }
    if thumbnail_url:
        inner["accessory"] = {
            "type": TYPE_THUMBNAIL,
            "media": {"url": thumbnail_url}
        }
    return {
        "type": TYPE_CONTAINER,
        "accent_color": color,
        "components": [
            inner,
            {"type": TYPE_SEPARATOR, "spacing": 1, "divider": True},
            buttons_row
        ]
    }


# ── Send helpers ─────────────────────────────────────────────

async def send_v2(channel, components: list, content: str = None):
    payload = {"flags": IS_COMPONENTS_V2, "components": components}
    if content:
        payload["content"] = content
    route = discord.http.Route("POST", "/channels/{channel_id}/messages",
                               channel_id=channel.id)
    return await channel._state.http.request(route, json=payload)

async def send_v2_dm(user, components: list):
    try:
        dm = await user.create_dm()
        await send_v2(dm, components)
    except:
        pass

async def edit_v2(message, components: list):
    payload = {"flags": IS_COMPONENTS_V2, "components": components}
    route = discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}",
                               channel_id=message.channel.id,
                               message_id=message.id)
    return await message._state.http.request(route, json=payload)

async def send_v2_interaction(interaction, components: list, ephemeral: bool = False):
    flags = IS_COMPONENTS_V2
    if ephemeral:
        flags |= 64
    payload = {"type": 4, "data": {"flags": flags, "components": components}}
    route = discord.http.Route("POST",
                               "/interactions/{interaction_id}/{interaction_token}/callback",
                               interaction_id=interaction.id,
                               interaction_token=interaction.token)
    return await interaction._state.http.request(route, json=payload)

async def send_v2_followup(interaction, components: list, ephemeral: bool = False):
    flags = IS_COMPONENTS_V2
    if ephemeral:
        flags |= 64
    payload = {"flags": flags, "components": components}
    route = discord.http.Route("POST",
                               "/webhooks/{application_id}/{interaction_token}",
                               application_id=interaction.application_id,
                               interaction_token=interaction.token)
    return await interaction._state.http.request(route, json=payload)
