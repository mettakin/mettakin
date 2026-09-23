import json

from django.test import TestCase

from .models import Experience, Phenomenon
from .tests import experience, member

MODERN = "2026-07-28"


class McpTests(TestCase):
    def setUp(self):
        author = member()
        self.public = experience(author, title="Test light", body="Test body with light.")
        self.public.phenomena.set([Phenomenon.named("Test light")])
        self.community = experience(
            author, Experience.Visibility.COMMUNITY, title="Test community light"
        )

    def modern(self, method, params=None, **headers):
        params = (params or {}) | {"_meta": {"io.modelcontextprotocol/protocolVersion": MODERN}}
        headers = {"MCP-Protocol-Version": MODERN, "Mcp-Method": method} | headers
        if method == "tools/call":
            headers.setdefault("Mcp-Name", params["name"])
        body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        return self.client.post(
            "/mcp", json.dumps(body), content_type="application/json", headers=headers
        )

    def legacy(self, method, params=None):
        body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        return self.client.post("/mcp", json.dumps(body), content_type="application/json")

    def call(self, name, **arguments):
        return self.modern("tools/call", {"name": name, "arguments": arguments}).json()["result"]

    def test_discover_names_the_versions(self):
        result = self.modern("server/discover").json()["result"]
        self.assertEqual(result["supportedVersions"], [MODERN])
        self.assertIn("tools", result["capabilities"])

    def test_older_clients_can_initialize(self):
        result = self.legacy("initialize", {"protocolVersion": "2025-06-18"}).json()["result"]
        self.assertEqual(result["protocolVersion"], "2025-06-18")
        tools = self.legacy("tools/list").json()["result"]["tools"]
        self.assertEqual(len(tools), 3)

    def test_search_sees_only_public_experiences(self):
        found = self.call("search_experiences", query="light")["structuredContent"]
        self.assertEqual([e["title"] for e in found["experiences"]], ["Test light"])
        self.assertTrue(found["experiences"][0]["url"].startswith("http"))

    def test_community_experience_cannot_be_read(self):
        result = self.call("get_experience", id=self.community.pk)
        self.assertTrue(result["isError"])

    def test_topics_count_public_experiences(self):
        topics = self.call("list_topics")["structuredContent"]
        self.assertEqual(
            topics["phenomena"], [{"slug": "test-light", "name": "Test light", "count": 1}]
        )

    def test_wrong_arguments_are_explained_to_the_model(self):
        result = self.call("search_experiences", limit="many")
        self.assertTrue(result["isError"])
        self.assertIn("limit", result["content"][0]["text"])

    def test_headers_must_match_the_body(self):
        response = self.modern("tools/list", **{"Mcp-Method": "tools/call"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], -32020)

    def test_unknown_version_lists_supported_ones(self):
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {"_meta": {"io.modelcontextprotocol/protocolVersion": "1900-01-01"}},
        }
        response = self.client.post(
            "/mcp",
            json.dumps(body),
            content_type="application/json",
            headers={"MCP-Protocol-Version": "1900-01-01", "Mcp-Method": "tools/list"},
        )
        self.assertEqual(response.json()["error"]["data"]["supported"], [MODERN])

    def test_notifications_are_accepted_and_get_is_not(self):
        body = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        response = self.client.post("/mcp", json.dumps(body), content_type="application/json")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(self.client.get("/mcp").status_code, 405)

    def test_foreign_origin_is_refused(self):
        response = self.client.post(
            "/mcp",
            "{}",
            content_type="application/json",
            headers={"Origin": "https://evil.example"},
        )
        self.assertEqual(response.status_code, 403)
