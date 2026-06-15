import datetime

from app.models import AccountStrike, db
from app.strikes import count_active_strikes, deactivate_expired_strikes, issue_strike


def test_issue_strike_mutes_at_threshold(app):
    with app.app_context():
        from tests.conftest import create_account

        moderator = create_account('mod', gm_level=9)
        player = create_account('player')

        issue_strike(
            account_id=player.id,
            issued_by_id=moderator.id,
            source_type='manual',
            reason='first',
        )
        strike = issue_strike(
            account_id=player.id,
            issued_by_id=moderator.id,
            source_type='manual',
            reason='second',
        )

        db.session.refresh(player)
        assert strike.action_taken == 'mute'
        assert player.mute_expire > 0
        assert count_active_strikes(player.id) == 2


def test_issue_strike_bans_at_threshold(app):
    with app.app_context():
        from tests.conftest import create_account

        moderator = create_account('mod2', gm_level=9)
        player = create_account('player2')

        for i in range(3):
            issue_strike(
                account_id=player.id,
                issued_by_id=moderator.id,
                source_type='manual',
                reason=f'strike-{i}',
            )
        strike = issue_strike(
            account_id=player.id,
            issued_by_id=moderator.id,
            source_type='manual',
            reason='strike-final',
        )

        db.session.refresh(player)
        assert strike.action_taken == 'ban'
        assert player.banned is True


def test_deactivate_expired_strikes(app):
    with app.app_context():
        from tests.conftest import create_account

        moderator = create_account('mod3', gm_level=9)
        player = create_account('player3')
        expired = AccountStrike(
            account_id=player.id,
            issued_by_id=moderator.id,
            source_type='manual',
            reason='old',
            active=True,
            expires_at=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
        db.session.add(expired)
        db.session.commit()

        assert deactivate_expired_strikes() == 1
        db.session.refresh(expired)
        assert expired.active is False
