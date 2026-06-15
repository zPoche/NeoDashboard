from unittest.mock import MagicMock, patch

from app.characters import apply_character_name_approval


def test_apply_character_name_approval_success(app):
    with app.app_context():
        character = MagicMock()
        character.pending_name = 'NewName'
        character.name = 'OldName'
        character.id = 1
        character.needs_rename = True

        with patch('app.characters.CharacterInfo') as mock_model, \
             patch('app.characters.log_audit'):
            mock_model.query.filter.return_value.first.return_value = None
            assert apply_character_name_approval(character) is True

        assert character.name == 'NewName'
        assert character.pending_name == ''
        assert character.needs_rename is False
        character.save.assert_called_once()


def test_apply_character_name_approval_no_pending_name(app):
    with app.app_context():
        character = MagicMock()
        character.pending_name = ''
        assert apply_character_name_approval(character) is False


def test_apply_character_name_approval_duplicate_name(app):
    with app.app_context():
        character = MagicMock()
        character.pending_name = 'TakenName'
        character.name = 'OldName'
        character.id = 2

        with patch('app.characters.CharacterInfo') as mock_model:
            mock_model.query.filter.return_value.first.return_value = MagicMock()
            assert apply_character_name_approval(character) is False

        character.save.assert_not_called()
