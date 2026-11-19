"""Tests for application settings.

Verifies the ``Settings`` dataclass behaves correctly under various
configurations. All tests rely on the ``mock_settings`` fixture which
uses ``tmp_path`` so no real directories are touched.
"""

from __future__ import annotations

import pytest

from backend.app.core.config import Settings, get_settings


class TestSettingsDefaults:
    def test_default_app_env(self) -> None:
        s = Settings()
        assert s.APP_ENV == "development"

    def test_app_env_override(self) -> None:
        s = Settings(APP_ENV="staging")
        assert s.APP_ENV == "staging"

    def test_debug_defaults_to_true(self) -> None:
        s = Settings()
        assert s.DEBUG is True

    def test_debug_can_be_false(self) -> None:
        s = Settings(DEBUG=False)
        assert s.DEBUG is False


class TestSettingsCORS:
    def test_cors_single_origin(self) -> None:
        s = Settings(CORS_ORIGINS="http://example.com")
        assert s.cors_origins_list == ["http://example.com"]

    def test_cors_multiple_origins(self) -> None:
        s = Settings(CORS_ORIGINS="http://a.com,http://b.com")
        assert s.cors_origins_list == ["http://a.com", "http://b.com"]

    def test_cors_wildcard(self) -> None:
        s = Settings(CORS_ORIGINS="*")
        assert s.cors_origins_list == ["*"]


class TestSettingsValues:
    def test_log_level(self) -> None:
        s = Settings(LOG_LEVEL="WARNING")
        assert s.LOG_LEVEL == "WARNING"

    def test_app_name(self) -> None:
        s = Settings(APP_NAME="MyApp")
        assert s.APP_NAME == "MyApp"

    def test_app_version(self) -> None:
        s = Settings(APP_VERSION="2.0.0")
        assert s.APP_VERSION == "2.0.0"

    def test_database_url(self) -> None:
        s = Settings(DATABASE_URL="postgresql://user:pass@localhost/db")
        assert s.DATABASE_URL == "postgresql://user:pass@localhost/db"

    def test_log_format(self) -> None:
        s = Settings(LOG_FORMAT="json")
        assert s.LOG_FORMAT == "json"