from unittest.mock import patch

from app.cdclient_queries import get_zone_display_name


def test_get_zone_display_name_fallback(app):
    with app.app_context():
        with patch('app.cdclient_queries.query_cdclient', return_value=None):
            assert get_zone_display_name(9999) == 'Unknown Zone'


def test_get_zone_display_name_value(app):
    with app.app_context():
        with patch('app.cdclient_queries.query_cdclient', return_value=('Test Zone',)):
            assert get_zone_display_name(1200) == 'Test Zone'
