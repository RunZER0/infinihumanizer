from django.test import TestCase
from django.urls import reverse

from .catalog import estimate_project, payment_structure


class PlatformSmokeTests(TestCase):
    def test_core_pages_render(self):
        for name in [
            "platform:home",
            "platform:services",
            "platform:pricing",
            "platform:enterprise",
            "platform:consultation",
            "platform:originality",
        ]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)

    def test_scope_flow(self):
        response = self.client.post(
            reverse("platform:start"),
            {
                "service": "research-production",
                "objective": "Assess a market and prepare a board brief.",
                "deliverable": "Decision brief",
                "audience": "Board",
                "source_state": "Existing internal notes",
                "research_depth": "standard",
                "complexity": "standard",
                "urgency": "standard",
                "email": "buyer@example.com",
            },
        )
        self.assertEqual(response.status_code, 302)
        project_id = next(iter(self.client.session["infini_projects"]))
        scope = self.client.get(reverse("platform:scope", kwargs={"project_id": project_id}))
        self.assertContains(scope, "PROVISIONAL RANGE")

    def test_price_scales_with_scope(self):
        small = estimate_project("research-production", "light", "focused", "flexible")
        large = estimate_project("research-production", "deep", "enterprise", "urgent")
        self.assertGreater(large[1], small[1])
        self.assertEqual(payment_structure(300)["percent"], 100)
        self.assertEqual(payment_structure(1500)["percent"], 50)
        self.assertEqual(payment_structure(10000)["percent"], 30)
