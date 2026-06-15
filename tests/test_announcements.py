from unittest.mock import MagicMock, patch

from app.announcements import send_chat_announcement


def test_send_chat_announcement_success(app):
    with app.app_context():
        app.config['CHAT_API_ENABLED'] = True
        app.config['CHAT_API_URL'] = 'http://chat.test/api/v1'

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch('app.announcements.request.urlopen', return_value=mock_response):
            send_chat_announcement('Hello', 'World')
