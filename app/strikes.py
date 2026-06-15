import datetime

from flask import current_app
from sqlalchemy import or_

from app.models import Account, AccountStrike, CharacterInfo, db


def get_strike_config():
    return {
        'auto_actions_enabled': current_app.config.get('STRIKE_AUTO_ACTIONS_ENABLED', True),
        'strikes_before_mute': int(current_app.config.get('STRIKES_BEFORE_MUTE', 3)),
        'strikes_before_ban': int(current_app.config.get('STRIKES_BEFORE_BAN', 5)),
        'mute_days': int(current_app.config.get('STRIKE_MUTE_DAYS', 7)),
        'rolloff_days': int(current_app.config.get('STRIKE_ROLLOFF_DAYS', 90)),
    }


def count_active_strikes(account_id):
    now = datetime.datetime.utcnow()
    return AccountStrike.query.filter(
        AccountStrike.account_id == account_id,
        AccountStrike.active == True,
        or_(
            AccountStrike.expires_at.is_(None),
            AccountStrike.expires_at > now,
        ),
    ).count()


def account_id_for_character(character_id):
    character = CharacterInfo.query.filter(CharacterInfo.id == character_id).first()
    return character.account_id if character else None


def issue_strike(*, account_id, issued_by_id, source_type, reason, source_id=None):
    """Record a strike and optionally apply mute/ban thresholds."""
    if not account_id:
        return None

    config = get_strike_config()
    expires_at = None
    if config['rolloff_days'] > 0:
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=config['rolloff_days'])

    previous_count = count_active_strikes(account_id)
    strike = AccountStrike(
        account_id=account_id,
        issued_by_id=issued_by_id,
        source_type=source_type,
        source_id=source_id,
        reason=reason,
        expires_at=expires_at,
        active=True,
    )
    db.session.add(strike)
    db.session.commit()

    new_count = previous_count + 1
    action_taken = None

    if config['auto_actions_enabled']:
        account = Account.query.filter(Account.id == account_id).first()
        if account and account.gm_level < 3:
            if (
                new_count >= config['strikes_before_ban']
                and previous_count < config['strikes_before_ban']
                and not account.banned
            ):
                account.banned = True
                account.active = False
                action_taken = 'ban'
            elif (
                new_count >= config['strikes_before_mute']
                and previous_count < config['strikes_before_mute']
            ):
                mute_until = datetime.datetime.now() + datetime.timedelta(days=config['mute_days'])
                account.mute_expire = int(mute_until.timestamp())
                action_taken = 'mute'

            if action_taken:
                db.session.add(account)
                strike.action_taken = action_taken
                db.session.add(strike)
                db.session.commit()

    return strike


def deactivate_expired_strikes():
    now = datetime.datetime.utcnow()
    expired = AccountStrike.query.filter(
        AccountStrike.active == True,
        AccountStrike.expires_at.isnot(None),
        AccountStrike.expires_at <= now,
    ).all()
    for strike in expired:
        strike.active = False
        db.session.add(strike)
    if expired:
        db.session.commit()
    return len(expired)
