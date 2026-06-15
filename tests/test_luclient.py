from unittest.mock import MagicMock, patch

from app.luclient import query_cdclient


def test_query_cdclient_returns_none_when_no_database(app):
    with app.app_context():
        with patch('app.luclient.get_cdclient', return_value=None):
            assert query_cdclient('SELECT 1', one=True) is None
            assert query_cdclient('SELECT 1', one=False) == []


def test_query_cdclient_one_result(app):
    with app.app_context():
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('value',)]
        mock_db = MagicMock()
        mock_db.execute.return_value = mock_cursor

        with patch('app.luclient.get_cdclient', return_value=mock_db):
            assert query_cdclient('SELECT ?', ['x'], one=True) == ('value',)
