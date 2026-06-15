import json
from urllib import error, request

from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_user import login_required, current_user

from app import gm_level, log_audit
from app.forms import AnnouncementForm
from app.models import AnnouncementLog, db

announcements_blueprint = Blueprint('announcements', __name__)


def send_chat_announcement(title, message):
    """Send an announcement via the DLU Chat Web API."""
    if not current_app.config.get('CHAT_API_ENABLED', False):
        raise RuntimeError("Chat API is not enabled")

    api_url = current_app.config['CHAT_API_URL'].rstrip('/')
    payload = json.dumps({'title': title, 'message': message}).encode('utf-8')
    req = request.Request(
        f"{api_url}/announce",
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                raise RuntimeError(f"Chat API returned status {response.status}")
    except error.URLError as exc:
        raise RuntimeError(f"Failed to reach Chat API: {exc}") from exc


@announcements_blueprint.route('/', methods=['GET', 'POST'])
@login_required
@gm_level(8)
def index():
    form = AnnouncementForm()
    history = AnnouncementLog.query.order_by(AnnouncementLog.sent_at.desc()).limit(20).all()

    if form.validate_on_submit():
        title = form.title.data.strip()
        message = form.message.data.strip()
        try:
            send_chat_announcement(title, message)
            log_entry = AnnouncementLog(
                title=title,
                message=message,
                sent_by_id=current_user.id,
                success=True,
            )
            db.session.add(log_entry)
            db.session.commit()
            log_audit(f"Sent in-game announcement: {title}")
            flash("Announcement sent to the game server.", "success")
            return redirect(url_for('announcements.index'))
        except RuntimeError as exc:
            log_entry = AnnouncementLog(
                title=title,
                message=message,
                sent_by_id=current_user.id,
                success=False,
                error_message=str(exc),
            )
            db.session.add(log_entry)
            db.session.commit()
            flash(str(exc), "danger")

    return render_template(
        'announcements/index.html.j2',
        form=form,
        history=history,
        chat_api_enabled=current_app.config.get('CHAT_API_ENABLED', False),
        chat_api_url=current_app.config.get('CHAT_API_URL', ''),
    )
