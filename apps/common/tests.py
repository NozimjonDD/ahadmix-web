import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from django.urls import path, re_path
from django.views.static import serve

from apps.common import site_admin


def public_site_data(request, path):
    return serve(request, path, document_root=site_admin.DATA_DIR)


def response_bytes(response):
    try:
        return b"".join(response.streaming_content) if response.streaming else response.content
    finally:
        response.close()


urlpatterns = [
    path("", site_admin.SiteHomeTemplateView.as_view()),
    path("site-admin/api/", site_admin.SiteAdminAPIView.as_view()),
    re_path(r"^data/(?P<path>.*)$", public_site_data),
]


@override_settings(
    ROOT_URLCONF=__name__,
    SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies",
    ALLOWED_HOSTS=["testserver"],
)
class SiteAdminPublicDataFlowTests(SimpleTestCase):
    def test_saved_admin_changes_are_served_to_public_site(self):
        with TemporaryDirectory() as directory, patch.object(site_admin, "DATA_DIR", Path(directory)), patch.object(site_admin, "ADMIN_PASSWORD", "test-password"):
            homepage = self.client.get("/")
            self.assertEqual(homepage.status_code, 200)
            for filename in ("screens", "airport", "settings", "texts"):
                self.assertIn(f"data/{filename}.json".encode(), homepage.content)

            login = self.client.post(
                "/site-admin/api/?a=login",
                data=json.dumps({"password": "test-password"}),
                content_type="application/json",
            )
            self.assertEqual(login.status_code, 200)

            changes = (
                ("screens", lambda value: value[0].update(n="Updated screen"), lambda value: value[0]["n"] == "Updated screen"),
                ("airport", lambda value: value[0].update(zn="Updated airport format"), lambda value: value[0]["zn"] == "Updated airport format"),
                ("settings", lambda value: value.update(phone="+998 90 000 00 00"), lambda value: value["phone"] == "+998 90 000 00 00"),
            )
            for filename, edit, visible in changes:
                data = json.loads((Path(directory) / f"{filename}.json").read_text(encoding="utf-8"))
                edit(data)
                saved = self.client.post(
                    f"/site-admin/api/?a=save&file={filename}",
                    data=json.dumps({"data": data}),
                    content_type="application/json",
                )
                self.assertEqual(saved.status_code, 200, saved.content)
                public = self.client.get(f"/data/{filename}.json")
                self.assertEqual(public.status_code, 200)
                self.assertTrue(visible(json.loads(response_bytes(public))))

            saved = self.client.post(
                "/site-admin/api/?a=save&file=texts",
                data=json.dumps({"data": {"nav1": {"ru": "Новый текст", "uz": "Yangi matn", "en": "New text"}}}),
                content_type="application/json",
            )
            self.assertEqual(saved.status_code, 200, saved.content)
            public = self.client.get("/data/texts.json")
            self.assertEqual(public.status_code, 200)
            self.assertEqual(json.loads(response_bytes(public))["nav1"]["uz"], "Yangi matn")
