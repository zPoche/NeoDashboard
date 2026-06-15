from app.moderation import (
    AUTO_APPROVAL_ENABLED_KEY,
    DEFAULT_AUTO_APPROVAL_INTERVAL,
    get_auto_approval_enabled,
    get_auto_approval_interval,
)
from app.models import DashboardSettings


def test_dashboard_settings_get_set_default(app):
    with app.app_context():
        assert DashboardSettings.get('missing_key', 'fallback') == 'fallback'


def test_dashboard_settings_set_and_get(app):
    with app.app_context():
        DashboardSettings.set('test_key', 'test_value')
        assert DashboardSettings.get('test_key') == 'test_value'

        DashboardSettings.set('test_key', 'updated')
        assert DashboardSettings.get('test_key') == 'updated'


def test_auto_approval_disabled_by_default(app):
    with app.app_context():
        assert get_auto_approval_enabled() is False


def test_auto_approval_enabled_toggle(app):
    with app.app_context():
        DashboardSettings.set(AUTO_APPROVAL_ENABLED_KEY, 'true')
        assert get_auto_approval_enabled() is True

        DashboardSettings.set(AUTO_APPROVAL_ENABLED_KEY, 'false')
        assert get_auto_approval_enabled() is False


def test_auto_approval_interval_default(app):
    with app.app_context():
        assert get_auto_approval_interval() == DEFAULT_AUTO_APPROVAL_INTERVAL


def test_auto_approval_interval_custom(app):
    with app.app_context():
        DashboardSettings.set('auto_approval_interval', '30')
        assert get_auto_approval_interval() == 30


def test_auto_approval_interval_invalid_falls_back(app):
    with app.app_context():
        DashboardSettings.set('auto_approval_interval', 'not-a-number')
        assert get_auto_approval_interval() == DEFAULT_AUTO_APPROVAL_INTERVAL
