"""Unit tests for WhiteboardController (returns (result, error) tuples)."""

import unittest
from unittest.mock import patch

from tests.support.fixtures import user_row

WB = 'app.controllers.whiteboard_controller'


class WhiteboardTestBase(unittest.TestCase):
    def setUp(self):
        from app.controllers.whiteboard_controller import WhiteboardController
        self.controller = WhiteboardController()


class TestCreateBoard(WhiteboardTestBase):
    @patch(f'{WB}.add_whiteboard_member')
    @patch(f'{WB}.create_whiteboard', return_value={'id': 1, 'code': '123456'})
    @patch(f'{WB}.get_whiteboard_by_code', return_value=None)
    def test_create(self, mock_bycode, mock_create, mock_add):
        board, err = self.controller.create_board(1, 'My Board')
        self.assertIsNone(err)
        self.assertEqual(board['id'], 1)
        mock_add.assert_called_once_with(1, 1)


class TestJoinBoard(WhiteboardTestBase):
    def test_blank_code_error(self):
        board, err = self.controller.join_board(1, '   ')
        self.assertIsNone(board)
        self.assertIn('code is required', err)

    @patch(f'{WB}.get_whiteboard_by_code', return_value=None)
    def test_unknown_code_error(self, mock_bycode):
        board, err = self.controller.join_board(1, 'ZZZZZZ')
        self.assertIsNone(board)
        self.assertIn('No whiteboard', err)

    @patch(f'{WB}.add_whiteboard_member')
    @patch(f'{WB}.get_whiteboard_by_code', return_value={'id': 5, 'code': 'ABC123'})
    def test_join_success(self, mock_bycode, mock_add):
        board, err = self.controller.join_board(1, 'ABC123')
        self.assertIsNone(err)
        self.assertEqual(board['id'], 5)
        mock_add.assert_called_once_with(1, 5)


class TestGetState(WhiteboardTestBase):
    @patch(f'{WB}.get_whiteboard_by_code', return_value=None)
    def test_board_not_found(self, mock_bycode):
        result, err = self.controller.get_state('X', 1)
        self.assertIsNone(result)
        self.assertEqual(err, 'Whiteboard not found')

    @patch(f'{WB}.is_user_in_whiteboard', return_value=False)
    @patch(f'{WB}.get_whiteboard_by_code', return_value={'id': 5})
    def test_access_denied(self, mock_bycode, mock_member):
        result, err = self.controller.get_state('ABC123', 1)
        self.assertEqual(err, 'Access denied')

    @patch(f'{WB}.get_whiteboard_state', return_value={'state': '{"shapes": [1]}'})
    @patch(f'{WB}.is_user_in_whiteboard', return_value=True)
    @patch(f'{WB}.get_whiteboard_by_code', return_value={'id': 5})
    def test_returns_parsed_state(self, mock_bycode, mock_member, mock_state):
        result, err = self.controller.get_state('ABC123', 1)
        self.assertIsNone(err)
        self.assertEqual(result['state'], {'shapes': [1]})


class TestSaveState(WhiteboardTestBase):
    @patch(f'{WB}.save_whiteboard_state')
    @patch(f'{WB}.get_user_by_id', return_value=user_row())
    @patch(f'{WB}.is_user_in_whiteboard', return_value=True)
    @patch(f'{WB}.get_whiteboard_by_code', return_value={'id': 5})
    def test_save_success(self, mock_bycode, mock_member, mock_user, mock_save):
        result, err = self.controller.save_state('ABC123', 1, {'shapes': []})
        self.assertIsNone(err)
        mock_save.assert_called_once()

    @patch(f'{WB}.get_user_by_id', return_value=None)
    @patch(f'{WB}.is_user_in_whiteboard', return_value=True)
    @patch(f'{WB}.get_whiteboard_by_code', return_value={'id': 5})
    def test_missing_user(self, mock_bycode, mock_member, mock_user):
        result, err = self.controller.save_state('ABC123', 1, {})
        self.assertEqual(err, 'User not found')


class TestClearState(WhiteboardTestBase):
    @patch(f'{WB}.clear_whiteboard_state')
    @patch(f'{WB}.is_user_in_whiteboard', return_value=True)
    @patch(f'{WB}.get_whiteboard_by_code', return_value={'id': 5})
    def test_clear(self, mock_bycode, mock_member, mock_clear):
        result, err = self.controller.clear_state('ABC123', 1)
        self.assertIsNone(err)
        self.assertIsNone(result['state'])
        mock_clear.assert_called_once_with(5)


if __name__ == '__main__':
    unittest.main()
