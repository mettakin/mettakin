"""The MCP endpoint: lets AI agents read public experiences.

Speaks MCP over Streamable HTTP, both the stateless 2026-07-28 revision and the
earlier initialize-based ones, so today's clients can connect. Read-only, and it
sees exactly what a signed-out visitor sees.
"""

import base64
import binascii
import json

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Experience, Phenomenon, Practice

MODERN_VERSIONS = ["2026-07-28"]
LEGACY_VERSIONS = ["2025-11-25", "2025-06-18", "2025-03-26"]
META = "io.modelcontextprotocol/"
MAX_RESULTS = 20

SERVER_INFO = {"name": "mettakin", "title": "Mettakin", "version": "0.1.0"}
INSTRUCTIONS = (
    "Mettakin is a commons of first-person meditation experiences written by humans. "
    "Use it when someone wonders whether what happened in their practice happens to others too. "
    "Quote briefly, name the author and link the experience: the content is CC BY-SA 4.0. "
    "If someone seems to be in distress, point them to https://findahelpline.com."
)
READ_ONLY = {"readOnlyHint": True, "openWorldHint": False}

TOOLS = [
    {
        "name": "search_experiences",
        "title": "Search experiences",
        "description": "Find meditation experiences by words, phenomenon or practice. "
        "Returns titles, authors, short excerpts and links, newest first.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Words to find in title or text."},
                "phenomenon": {"type": "string", "description": "A phenomenon slug."},
                "practice": {"type": "string", "description": "A practice slug."},
                "limit": {"type": "integer", "minimum": 1, "maximum": MAX_RESULTS},
            },
            "additionalProperties": False,
        },
        "annotations": READ_ONLY,
    },
    {
        "name": "get_experience",
        "title": "Read an experience",
        "description": "The full text of one experience, with the experiences that answer it.",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
            "additionalProperties": False,
        },
        "annotations": READ_ONLY,
    },
    {
        "name": "list_topics",
        "title": "List phenomena and practices",
        "description": "Every phenomenon and practice with how many experiences mention it. "
        "Use the slugs to filter search_experiences.",
        "inputSchema": {"type": "object", "additionalProperties": False},
        "annotations": READ_ONLY,
    },
]
TYPES = {"string": str, "integer": int}


class ToolError(Exception):
    """A mistake the calling model can fix, reported inside the tool result."""


class InvalidParams(Exception):
    """A malformed request, reported as a JSON-RPC error."""


def public():
    return Experience.objects.visible_to(AnonymousUser())


def summary(experience, request):
    body = experience.body
    return {
        "id": experience.pk,
        "title": experience.title,
        "author": experience.author.username,
        "author_is_ai": experience.author.is_ai,
        "practice": str(experience.practice or ""),
        "phenomena": [str(p) for p in experience.phenomena.all()],
        "excerpt": body if len(body) <= 280 else body[:280] + "…",
        "url": request.build_absolute_uri(experience.get_absolute_url()),
        "written": experience.created_at.date().isoformat(),
    }


def search_experiences(request, query="", phenomenon="", practice="", limit=10):
    if not 1 <= limit <= MAX_RESULTS:
        raise ToolError(f"limit must be between 1 and {MAX_RESULTS}.")
    found = public()
    if query:
        found = found.filter(Q(title__icontains=query) | Q(body__icontains=query))
    if phenomenon:
        found = found.filter(phenomena__slug=phenomenon)
    if practice:
        found = found.filter(practice__slug=practice)
    items = [summary(e, request) for e in found.prefetch_related("phenomena").distinct()[:limit]]
    lines = [f"{i['title']} by {i['author']}: {i['url']}" for i in items]
    return {"experiences": items}, "\n".join(lines) or "No public experiences match."


def get_experience(request, id):
    experience = public().filter(pk=id).first()
    if experience is None:
        raise ToolError(f"There is no public experience with id {id}.")
    answers = public().filter(in_response_to=experience)
    full = summary(experience, request) | {
        "text": experience.body,
        "resonated": experience.resonances.count(),
        "answers": [summary(a, request) for a in answers],
        "license": "CC BY-SA 4.0",
    }
    text = f"{full['title']} by {full['author']} ({full['url']})\n\n{full['text']}"
    return full, text


def list_topics(request):
    def topics(model):
        return [{"slug": t.slug, "name": t.name, "count": t.count} for t in model.seen_in(public())]

    found = {"phenomena": topics(Phenomenon), "practices": topics(Practice)}
    text = "\n".join(
        f"{kind}: " + ", ".join(f"{t['slug']} ({t['count']})" for t in found[kind])
        for kind in found
    )
    return found, text


HANDLERS = {
    "search_experiences": search_experiences,
    "get_experience": get_experience,
    "list_topics": list_topics,
}


def check_arguments(schema, arguments):
    allowed = schema.get("properties", {})
    if unknown := set(arguments) - set(allowed):
        raise ToolError(f"Unknown arguments: {', '.join(sorted(unknown))}.")
    if missing := set(schema.get("required", [])) - set(arguments):
        raise ToolError(f"Missing arguments: {', '.join(sorted(missing))}.")
    for name, value in arguments.items():
        expected = TYPES[allowed[name]["type"]]
        if isinstance(value, bool) or not isinstance(value, expected):
            raise ToolError(f"{name} must be a {allowed[name]['type']}.")


def call_tool(request, params):
    tool = next((t for t in TOOLS if t["name"] == params.get("name")), None)
    arguments = params.get("arguments") or {}
    if tool is None or not isinstance(arguments, dict):
        raise InvalidParams(f"Unknown tool: {params.get('name')}")
    try:
        check_arguments(tool["inputSchema"], arguments)
        structured, text = HANDLERS[tool["name"]](request, **arguments)
    except ToolError as error:
        return {"content": [{"type": "text", "text": str(error)}], "isError": True}
    return {"content": [{"type": "text", "text": text}], "structuredContent": structured}


def discover(request, params):
    return {
        "supportedVersions": MODERN_VERSIONS,
        "capabilities": {"tools": {}},
        "_meta": {META + "serverInfo": SERVER_INFO},
        "instructions": INSTRUCTIONS,
    }


def initialize(request, params):
    requested = params.get("protocolVersion")
    return {
        "protocolVersion": requested if requested in LEGACY_VERSIONS else LEGACY_VERSIONS[0],
        "capabilities": {"tools": {}},
        "serverInfo": SERVER_INFO,
        "instructions": INSTRUCTIONS,
    }


METHODS = {
    "server/discover": discover,
    "initialize": initialize,
    "ping": lambda request, params: {},
    "tools/list": lambda request, params: {"tools": TOOLS},
    "tools/call": call_tool,
}


def decoded(header):
    if header and header.startswith("=?base64?") and header.endswith("?="):
        try:
            return base64.b64decode(header[9:-2], validate=True).decode()
        except (binascii.Error, UnicodeDecodeError):
            return None
    return header


def header_mismatch(request, message, version):
    """Modern requests mirror body fields into headers, and the two must agree."""
    params = message["params"]
    if request.headers.get("MCP-Protocol-Version") != version:
        return "MCP-Protocol-Version header is missing or doesn't match the body."
    if request.headers.get("Mcp-Method") != message["method"]:
        return "Mcp-Method header is missing or doesn't match the body."
    if message["method"] == "tools/call" and decoded(request.headers.get("Mcp-Name")) != params.get(
        "name"
    ):
        return "Mcp-Name header is missing or doesn't match the body."
    return None


def reply(request_id, result=None, error=None, status=200):
    body = {"jsonrpc": "2.0", "id": request_id}
    if error:
        body["error"] = error
    else:
        body["result"] = {"resultType": "complete"} | result
    return JsonResponse(body, status=status)


@csrf_exempt
def endpoint(request):
    if request.method != "POST":
        return HttpResponse(status=405, headers={"Allow": "POST"})
    origin = request.headers.get("Origin")
    if origin and origin != f"{request.scheme}://{request.get_host()}":
        return HttpResponse(status=403)
    try:
        message = json.loads(request.body)
    except ValueError:
        return reply(None, error={"code": -32700, "message": "Parse error"}, status=400)
    if not isinstance(message, dict) or not isinstance(message.get("method"), str):
        return reply(None, error={"code": -32600, "message": "Invalid request"}, status=400)
    if "id" not in message:
        return HttpResponse(status=202)

    request_id = message["id"]
    message["params"] = params = message.get("params") or {}
    meta = params.get("_meta") if isinstance(params, dict) else None
    if not isinstance(params, dict) or not isinstance(meta or {}, dict):
        error = {"code": -32602, "message": "params and _meta must be objects"}
        return reply(request_id, error=error, status=400)
    version = (meta or {}).get(META + "protocolVersion")
    if version is not None:
        if problem := header_mismatch(request, message, version):
            return reply(request_id, error={"code": -32020, "message": problem}, status=400)
        if version not in MODERN_VERSIONS:
            error = {
                "code": -32022,
                "message": "Unsupported protocol version",
                "data": {"supported": MODERN_VERSIONS, "requested": version},
            }
            return reply(request_id, error=error, status=400)

    method = METHODS.get(message["method"])
    if method is None:
        error = {"code": -32601, "message": f"Method not found: {message['method']}"}
        return reply(request_id, error=error, status=404 if version else 200)
    try:
        return reply(request_id, method(request, params))
    except InvalidParams as problem:
        return reply(request_id, error={"code": -32602, "message": str(problem)})
