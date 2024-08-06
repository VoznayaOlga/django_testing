from notes.models import Note
from notes.tests.conftest import TestNoteBaseClassWithCreation


class TestNotes(TestNoteBaseClassWithCreation):

    def test_successful_creation(self):
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
