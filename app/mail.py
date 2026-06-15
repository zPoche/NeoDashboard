from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_user import login_required, current_user
from app.models import Mail, CharacterInfo, db
from app.forms import SendMailForm
from app import gm_level, log_audit
from app.luclient import translate_from_locale, query_cdclient
from app.cdclient_queries import get_loot_objects
import time

mail_blueprint = Blueprint('mail', __name__)


def _mail_payload(form, *, receiver_id, receiver_name, sender_name, sent_at):
    return {
        'sender_id': 0,
        'sender_name': sender_name,
        'receiver_id': receiver_id,
        'receiver_name': receiver_name,
        'time_sent': sent_at,
        'subject': form.subject.data,
        'body': form.body.data,
        'attachment_id': 0,
        'attachment_lot': form.attachment.data,
        'attachment_subkey': 0,
        'attachment_count': form.attachment_count.data,
        'was_read': False,
    }


@mail_blueprint.route('/view/<id>', methods=['GET'])
@login_required
def view(id):
    mail = Mail.query.filter(Mail.id == id).first()

    return render_template('mail/view.html.j2', mail=mail)


@mail_blueprint.route('/send', methods=['GET', 'POST'])
@login_required
@gm_level(3)
def send():
    form = SendMailForm()

    if request.method == "POST":
        if form.attachment.data != "0" and form.attachment_count.data == 0:
            form.attachment_count.data = 1
        if form.recipient.data == "0":
            characters = CharacterInfo.query.all()
            sender_name = f"[GM] {current_user.username}"
            sent_at = time.time()
            db.session.bulk_insert_mappings(Mail, [
                _mail_payload(
                    form,
                    receiver_id=character.id,
                    receiver_name=character.name,
                    sender_name=sender_name,
                    sent_at=sent_at,
                )
                for character in characters
            ])
            db.session.commit()
            log_audit(
                f"Sent bulk mail '{form.subject.data}' to {len(characters)} characters "
                f"with {form.attachment_count.data} of item {form.attachment.data}"
            )
        else:
            recipient = CharacterInfo.query.filter(
                CharacterInfo.id == form.recipient.data
            ).first()
            sender_name = f"[GM] {current_user.username}"
            sent_at = time.time()
            db.session.bulk_insert_mappings(Mail, [
                _mail_payload(
                    form,
                    receiver_id=recipient.id,
                    receiver_name=recipient.name,
                    sender_name=sender_name,
                    sent_at=sent_at,
                )
            ])
            db.session.commit()
            log_audit(
                f"Sent {form.subject.data}: {form.body.data} to "
                f"({recipient.id}){recipient.name} with {form.attachment_count.data} "
                f"of item {form.attachment.data}"
            )

        flash("Sent Mail", "success")
        return redirect(url_for('mail.send'))

    recipients = CharacterInfo.query.all()
    for character in recipients:
        form.recipient.choices.append((character.id, character.name))

    items = get_loot_objects()

    for item in items:
        name = translate_from_locale(f'Objects_{item[0]}_name')
        if name == f'Objects_{item[0]}_name':
            name = (item[2] if (item[2] != "None" and item[2] != "" and item[2] is not None) else item[1])
        form.attachment.choices.append(
            (
                item[0],
                f'({item[0]}) {name}'
            )
        )

    return render_template('mail/send.html.j2', form=form)
