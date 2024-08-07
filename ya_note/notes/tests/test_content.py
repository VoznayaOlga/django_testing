from notes.forms import NoteForm
from notes.tests.conftest import (TestNoteBaseClassWithCreation,
                                  NOTES_LIST_URL,
                                  NOTES_ADD_URL,
                                  NOTES_EDIT_URL)


class TestNoteList(TestNoteBaseClassWithCreation):

    def test_note_in_list_for_authorized_user(self):
        users_statuses = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for user_client, expected_value in users_statuses:
            with self.subTest(user_client=user_client,
                              expected_value=expected_value):
                response = user_client.get(NOTES_LIST_URL)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, expected_value)

    def test_pages_contains_form(self):
        urls = [NOTES_EDIT_URL, NOTES_ADD_URL]
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(NOTES_EDIT_URL)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
