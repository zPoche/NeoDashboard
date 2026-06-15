import os
import sys
from unittest.mock import MagicMock

import pytest

# ImageMagick is not available in CI; mock Wand before app imports.
sys.modules.setdefault('wand', MagicMock())
sys.modules.setdefault('wand.image', MagicMock())
sys.modules.setdefault('wand.exceptions', MagicMock())


@pytest.fixture
def app():
    os.environ['APP_SECRET_KEY'] = 'test-secret-key-for-pytest-only'
    os.environ['APP_DATABASE_URI'] = 'sqlite:///:memory:'
    os.environ['TESTING'] = 'True'

    from app import create_app, db
    from app.models import Account, AccountStrike

    application = create_app()
    application.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_ENGINE_OPTIONS': {},
        'WTF_CSRF_ENABLED': False,
        'STRIKE_AUTO_ACTIONS_ENABLED': True,
        'STRIKES_BEFORE_MUTE': 2,
        'STRIKES_BEFORE_BAN': 4,
        'STRIKE_MUTE_DAYS': 7,
        'STRIKE_ROLLOFF_DAYS': 30,
        'CHAT_API_ENABLED': False,
    })

    with application.app_context():
        Account.__table__.create(db.engine, checkfirst=True)
        AccountStrike.__table__.create(db.engine, checkfirst=True)
        yield application
        db.session.remove()
        AccountStrike.__table__.drop(db.engine, checkfirst=True)
        Account.__table__.drop(db.engine, checkfirst=True)


@pytest.fixture
def client(app):
    return app.test_client()
