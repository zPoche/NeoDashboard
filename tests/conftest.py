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
    from app.models import Account, AccountStrike, DashboardSettings

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

    tables = [Account, AccountStrike, DashboardSettings]

    with application.app_context():
        for table in tables:
            table.__table__.create(db.engine, checkfirst=True)
        yield application
        db.session.remove()
        for table in reversed(tables):
            table.__table__.drop(db.engine, checkfirst=True)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def gm_account(app):
    from app.models import Account, db

    with app.app_context():
        account = Account(username='gm', password='hashed', gm_level=9)
        db.session.add(account)
        db.session.commit()
        account_id = account.id
        yield account_id


def create_account(username, gm_level=0):
    from app.models import Account, db

    account = Account(username=username, password='hashed', gm_level=gm_level)
    db.session.add(account)
    db.session.commit()
    return account


def create_character(account_id, name, pending_name='', needs_rename=False, char_id=1001):
    """Return a simple character-like object for unit tests."""
    class FakeCharacter:
        def __init__(self):
            self.id = char_id
            self.account_id = account_id
            self.name = name
            self.pending_name = pending_name
            self.needs_rename = needs_rename

        def save(self):
            pass

    return FakeCharacter()
