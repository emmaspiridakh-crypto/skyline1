import os

TOKEN = os.environ.get("TOKEN")
PREFIX = "!"

ROLES = {
    "ceo":            1512030925989478451,
    "owner":          1512030928011137134,
    "co_owner":       1512030929097592862,
    "manager":        1512030932742180966,
    "staff":          1512030962668802118,
    "administrator":  1512030922705473567,
    "donate_manager": 1512030955550933012,
    "auto_role":      1512030977747320902,
}

SELLERS = [
    {"name": "Seller 1", "role_id": 1509180869942968531},
    {"name": "Seller 2", "role_id": 1263445083622215741},
    {"name": "Seller 3", "role_id": 999583544730996746},
    {"name": "Seller 4", "role_id": 1335693650755063818},
]

CHANNELS = {
    "ticket_category":  1512030994377605240,
    "voice_category":   1512031042842923158,
    "join_to_create":   1512031263479824474,
    "staff_notify":     1512124616808599796,
    "reviews":          1512031131757707414,
    "other_logs":       1512031993456758899,
    "ticket_logs":      1512138411400761514,
    "bot_logs":         1512145050887520458,
    "welcome_logs":     1512145072345321473,
    "punishments_logs": 1512145101391007967,
    "voice_logs":       1512145357365186852,
    "message_logs":     1512145394111348867,
    "channel_logs":     1512145431369617498,
    "role_logs":        1512145560910561381,
    "reaction_logs":    1512145598000922765,
    "invite_logs":      1512145624315723896,
    "billing_logs":     1512976780762546247,
}

BANNER_URL    = "https://i.imgur.com/M3AAbvA.jpeg"
THUMBNAIL_URL = "https://i.imgur.com/eVADKUU.png"

EMOJIS = {
    "ticket":       "<:ticket:1512145725914611747>",
    "close":        "<:close:1512137645806063666>",
    "notify":       "<:notify:1512124417831075940>",
    "support":      "<a:support:1512147009136623696>",
    "buy":          "<:buy:1512147241295413429>",
    "donate":       "<a:donate:1512331680260554782>",
    "review":       "<a:review:1512331908992860220>",
    "star":         "<a:star:1512943426679603373>",
    "star_empty":   "<:star_empty:1512146798289092718>",
    "pay":          "<a:pay:1512943442773282998>",
    "billing":      "<:billing:1512147204796842075>",
    "ban":          "<a:ban:1512146946607812699>",
    "kick":         "<a:kick:1512943429947228251>",
    "timeout":      "<a:timeout:1512331966928785508>",
    "unban":        "<a:unban:1512146946607812699>",
    "clear":        "<a:clear:1512147229001912340>",
    "log":          "<:log:1512945433792610426>",
    "join":         "<a:join:1512943429947228251>",
    "leave":        "<a:leave:1512943429947228251>",
    "edit":         "<:edit:1512128186236797119>",
    "delete":       "<:delete:1512147266947907624>",
    "voice_join":   "<a:voice_join:1512980531577618532>",
    "voice_leave":  "<a:voice_leave:1512943456845299783>",
    "role_add":     "<:role_add:1512128378118078655>",
    "role_remove":  "<:role_remove:1512128378118078655>",
    "channel_add":  "<:channel_add:1512146572560040038>",
    "channel_del":  "<:channel_del:1512146716139458621>",
    "reaction":     "<:reaction:1512060593497047231>",
    "invite":       "<a:invite:1512147189491826718>",
    "check":        "<a:check:1512146815104057608>",
    "error":        "<:error:1512137645806063666>",
    "loading":      "<a:loading:1512147229001912340>",
    "crown":        "<:crown:1512146898952126594>",
    "boost":        "<a:boost:1512331640020668456>",
    "suggestion":   "<:suggestion:1512145722156253277>",
    "upvote":       "<:upvote:1512146572560040038>",
    "downvote":     "<:downvote:1512146716139458621>",
    "say":          "<a:say:1512147024152363239>",
    "emoji_add":    "<:emoji_add:1512146932414287934>",
    "dm":           "<a:dm:1512147189491826718>",
    "voice":        "<:voice:1512128208659812476>",
    "punishment":   "<a:punishment:1512331805003350016>",
    "welcome":      "<a:welcome:1512943429947228251>",
}

STAFF_ROLES = ["ceo", "owner", "co_owner", "manager", "staff", "administrator"]

def is_staff(member):
    ids = [ROLES[k] for k in STAFF_ROLES]
    return any(r.id in ids for r in member.roles)

def has_roles(member, keys):
    ids = [ROLES[k] for k in keys if k in ROLES]
    return any(r.id in ids for r in member.roles)
