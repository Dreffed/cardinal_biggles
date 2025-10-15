"""
Tests for HIL editing functionality
"""

import pytest
from unittest.mock import patch, mock_open, MagicMock
from core.hil_controller import HILController, CheckpointType
import json
import platform


class TestHILEditing:
    """Test HIL editing feature"""

    @pytest.fixture
    def hil_controller(self):
        """Create HIL controller for testing"""
        config = {'editor': 'nano'}
        return HILController(enable_hil=True, auto_approve=False, config=config)

    @pytest.fixture
    def sample_data(self):
        """Sample data for editing tests"""
        return {
            'result': 'Test research result',
            'urls': ['https://example.com'],
            'agent_id': 'test_agent'
        }

    def test_get_editor_from_config(self, hil_controller):
        """Test getting editor from config"""
        editor = hil_controller._get_editor()
        assert editor == 'nano'

    def test_get_editor_from_environment(self):
        """Test getting editor from environment variable"""
        hil_controller = HILController(enable_hil=True, config={})

        with patch.dict('os.environ', {'EDITOR': 'vim'}):
            editor = hil_controller._get_editor()
            assert editor == 'vim'

    def test_get_editor_default_windows(self):
        """Test default editor on Windows"""
        hil_controller = HILController(enable_hil=True, config={})

        with patch('platform.system', return_value='Windows'):
            with patch.dict('os.environ', {}, clear=True):
                editor = hil_controller._get_editor()
                assert editor == 'notepad.exe'

    def test_get_editor_default_macos(self):
        """Test default editor on macOS"""
        hil_controller = HILController(enable_hil=True, config={})

        with patch('platform.system', return_value='Darwin'):
            with patch.dict('os.environ', {}, clear=True):
                editor = hil_controller._get_editor()
                assert editor == 'nano'

    def test_get_editor_default_linux(self):
        """Test default editor on Linux"""
        hil_controller = HILController(enable_hil=True, config={})

        with patch('platform.system', return_value='Linux'):
            with patch.dict('os.environ', {}, clear=True):
                editor = hil_controller._get_editor()
                assert editor == 'nano'

    def test_edit_data_note_only(self, hil_controller, sample_data):
        """Test note-only editing mode"""
        with patch('rich.prompt.Prompt.ask', side_effect=['note-only']):
            with patch('rich.prompt.Confirm.ask', return_value=True):
                with patch('rich.prompt.Prompt.ask', return_value='Test note'):
                    # Mock all the prompts
                    with patch.object(hil_controller.console, 'print'):
                        with patch('rich.prompt.Prompt.ask', side_effect=['note-only']):
                            with patch('rich.prompt.Confirm.ask', return_value=True):
                                with patch('rich.prompt.Prompt.ask', return_value='Test note'):
                                    edited = hil_controller._edit_data(sample_data, CheckpointType.TREND_REVIEW)

                                    assert 'user_note' in edited
                                    assert edited['user_note'] == 'Test note'

    def test_edit_data_note_only_skip(self, hil_controller, sample_data):
        """Test note-only mode when user skips adding note"""
        with patch.object(hil_controller.console, 'print'):
            with patch('rich.prompt.Prompt.ask', return_value='note-only'):
                with patch('rich.prompt.Confirm.ask', return_value=False):
                    edited = hil_controller._edit_data(sample_data, CheckpointType.TREND_REVIEW)

                    assert 'user_note' not in edited
                    assert edited == sample_data

    def test_edit_data_json_success(self, hil_controller, sample_data):
        """Test successful JSON editing"""
        edited_json = json.dumps({'edited': True, 'result': 'Modified'})

        with patch.object(hil_controller.console, 'print'):
            with patch('rich.prompt.Prompt.ask', return_value='json'):
                with patch('tempfile.NamedTemporaryFile', mock_open()) as mock_temp:
                    mock_temp.return_value.name = '/tmp/test.json'
                    with patch('subprocess.run') as mock_run:
                        with patch('builtins.open', mock_open(read_data=edited_json)):
                            with patch('os.path.exists', return_value=True):
                                with patch('os.unlink'):
                                    edited = hil_controller._edit_data(sample_data, CheckpointType.TREND_REVIEW)

                                    assert edited == {'edited': True, 'result': 'Modified'}

    def test_edit_data_yaml_success(self, hil_controller, sample_data):
        """Test successful YAML editing"""
        edited_yaml = "edited: true\nresult: Modified"

        with patch.object(hil_controller.console, 'print'):
            with patch('rich.prompt.Prompt.ask', return_value='yaml'):
                with patch('tempfile.NamedTemporaryFile', mock_open()) as mock_temp:
                    mock_temp.return_value.name = '/tmp/test.yaml'
                    with patch('subprocess.run') as mock_run:
                        with patch('builtins.open', mock_open(read_data=edited_yaml)):
                            with patch('os.path.exists', return_value=True):
                                with patch('os.unlink'):
                                    edited = hil_controller._edit_data(sample_data, CheckpointType.TREND_REVIEW)

                                    assert edited['edited'] is True
                                    assert edited['result'] == 'Modified'

    def test_edit_data_editor_not_found(self, hil_controller, sample_data):
        """Test graceful failure when editor not found"""
        with patch.object(hil_controller.console, 'print'):
            with patch('rich.prompt.Prompt.ask', return_value='json'):
                with patch('tempfile.NamedTemporaryFile', mock_open()) as mock_temp:
                    mock_temp.return_value.name = '/tmp/test.json'
                    with patch('subprocess.run', side_effect=FileNotFoundError):
                        with patch('os.path.exists', return_value=True):
                            with patch('os.unlink'):
                                edited = hil_controller._edit_data(sample_data, CheckpointType.TREND_REVIEW)

                                # Should return original data
                                assert edited == sample_data

    def test_edit_data_invalid_json(self, hil_controller, sample_data):
        """Test handling of invalid JSON"""
        invalid_json = "{'invalid': json}"  # Invalid JSON syntax

        with patch.object(hil_controller.console, 'print'):
            with patch('rich.prompt.Prompt.ask', return_value='json'):
                with patch('tempfile.NamedTemporaryFile', mock_open()) as mock_temp:
                    mock_temp.return_value.name = '/tmp/test.json'
                    with patch('subprocess.run'):
                        with patch('builtins.open', mock_open(read_data=invalid_json)):
                            with patch('os.path.exists', return_value=True):
                                with patch('os.unlink'):
                                    edited = hil_controller._edit_data(sample_data, CheckpointType.TREND_REVIEW)

                                    # Should return original data on parse error
                                    assert edited == sample_data

    def test_edit_data_non_dict_result(self, hil_controller, sample_data):
        """Test rejection of non-dictionary edited data"""
        invalid_data = '["list", "not", "dict"]'

        with patch.object(hil_controller.console, 'print'):
            with patch('rich.prompt.Prompt.ask', return_value='json'):
                with patch('tempfile.NamedTemporaryFile', mock_open()) as mock_temp:
                    mock_temp.return_value.name = '/tmp/test.json'
                    with patch('subprocess.run'):
                        with patch('builtins.open', mock_open(read_data=invalid_data)):
                            with patch('os.path.exists', return_value=True):
                                with patch('os.unlink'):
                                    edited = hil_controller._edit_data(sample_data, CheckpointType.TREND_REVIEW)

                                    # Should return original data
                                    assert edited == sample_data

    def test_edit_data_subprocess_error(self, hil_controller, sample_data):
        """Test handling of subprocess errors"""
        import subprocess

        with patch.object(hil_controller.console, 'print'):
            with patch('rich.prompt.Prompt.ask', return_value='json'):
                with patch('tempfile.NamedTemporaryFile', mock_open()) as mock_temp:
                    mock_temp.return_value.name = '/tmp/test.json'
                    with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd')):
                        with patch('os.path.exists', return_value=True):
                            with patch('os.unlink'):
                                edited = hil_controller._edit_data(sample_data, CheckpointType.TREND_REVIEW)

                                # Should return original data on subprocess error
                                assert edited == sample_data

    def test_temp_file_cleanup(self, hil_controller, sample_data):
        """Test that temporary file is cleaned up"""
        edited_json = json.dumps({'edited': True})

        with patch.object(hil_controller.console, 'print'):
            with patch('rich.prompt.Prompt.ask', return_value='json'):
                with patch('tempfile.NamedTemporaryFile', mock_open()) as mock_temp:
                    mock_temp.return_value.name = '/tmp/test.json'
                    with patch('subprocess.run'):
                        with patch('builtins.open', mock_open(read_data=edited_json)):
                            with patch('os.path.exists', return_value=True):
                                with patch('os.unlink') as mock_unlink:
                                    edited = hil_controller._edit_data(sample_data, CheckpointType.TREND_REVIEW)

                                    # Verify unlink was called to clean up temp file
                                    assert mock_unlink.called

    def test_editor_priority_config_over_env(self):
        """Test that config editor takes priority over environment"""
        config = {'editor': 'vim'}
        hil_controller = HILController(enable_hil=True, config=config)

        with patch.dict('os.environ', {'EDITOR': 'nano'}):
            editor = hil_controller._get_editor()
            assert editor == 'vim'  # Config should take priority

    def test_editor_priority_env_over_default(self):
        """Test that environment editor takes priority over default"""
        hil_controller = HILController(enable_hil=True, config={})

        with patch.dict('os.environ', {'EDITOR': 'emacs'}):
            editor = hil_controller._get_editor()
            assert editor == 'emacs'
