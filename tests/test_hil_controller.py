"""
Tests for HIL Controller
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from core.hil_controller import HILController, CheckpointType, ApprovalAction


@pytest.mark.unit
class TestHILController:
    """Test HIL Controller functionality"""

    def test_controller_initialization(self):
        """Test controller initializes correctly"""
        controller = HILController(enable_hil=True, auto_approve=False)

        assert controller.enable_hil is True
        assert controller.auto_approve is False
        assert len(controller.checkpoint_history) == 0

    @pytest.mark.asyncio
    async def test_disabled_mode(self):
        """Test HIL disabled returns immediate approval"""
        controller = HILController(enable_hil=False)

        result = await controller.checkpoint(
            CheckpointType.TREND_REVIEW,
            {"result": "test"},
            "Test Phase"
        )

        assert result["action"] == ApprovalAction.APPROVE
        assert result["data"]["result"] == "test"

    @pytest.mark.asyncio
    async def test_auto_approve_mode(self):
        """Test auto-approve mode"""
        controller = HILController(enable_hil=True, auto_approve=True)

        result = await controller.checkpoint(
            CheckpointType.TREND_REVIEW,
            {"result": "test"},
            "Test Phase"
        )

        assert result["action"] == ApprovalAction.APPROVE
        assert len(controller.checkpoint_history) == 1

    @pytest.mark.asyncio
    @patch('core.hil_controller.Prompt.ask')
    async def test_user_approval(self, mock_prompt):
        """Test user approves at checkpoint"""
        mock_prompt.return_value = "A"

        controller = HILController(enable_hil=True, auto_approve=False)

        result = await controller.checkpoint(
            CheckpointType.TREND_REVIEW,
            {"result": "test"},
            "Test Phase"
        )

        assert result["action"] == ApprovalAction.APPROVE
        assert len(controller.checkpoint_history) == 1
        assert controller.checkpoint_history[0]["action"] == "approve"

    @pytest.mark.asyncio
    @patch('core.hil_controller.Prompt.ask')
    async def test_user_quit(self, mock_prompt):
        """Test user quits at checkpoint"""
        mock_prompt.return_value = "Q"

        controller = HILController(enable_hil=True, auto_approve=False)

        result = await controller.checkpoint(
            CheckpointType.TREND_REVIEW,
            {"result": "test"},
            "Test Phase"
        )

        assert result["action"] == ApprovalAction.QUIT
        assert result["quit"] is True
        assert len(controller.checkpoint_history) == 1

    @pytest.mark.asyncio
    @patch('core.hil_controller.Prompt.ask')
    async def test_user_regenerate(self, mock_prompt):
        """Test user requests regeneration"""
        mock_prompt.return_value = "R"

        controller = HILController(enable_hil=True, auto_approve=False)

        result = await controller.checkpoint(
            CheckpointType.TREND_REVIEW,
            {"result": "test"},
            "Test Phase"
        )

        assert result["action"] == ApprovalAction.REGENERATE
        assert result["regenerate"] is True

    @pytest.mark.asyncio
    @patch('core.hil_controller.Prompt.ask')
    async def test_user_skip(self, mock_prompt):
        """Test user skips checkpoint"""
        mock_prompt.return_value = "S"

        controller = HILController(enable_hil=True, auto_approve=False)

        result = await controller.checkpoint(
            CheckpointType.TREND_REVIEW,
            {"result": "test"},
            "Test Phase"
        )

        assert result["action"] == ApprovalAction.SKIP

    @pytest.mark.asyncio
    @patch('core.hil_controller.Confirm.ask')
    @patch('core.hil_controller.Prompt.ask')
    async def test_user_edit_keep(self, mock_prompt, mock_confirm):
        """Test user edits but keeps original data"""
        mock_prompt.return_value = "E"
        mock_confirm.return_value = True

        controller = HILController(enable_hil=True, auto_approve=False)

        result = await controller.checkpoint(
            CheckpointType.TREND_REVIEW,
            {"result": "test"},
            "Test Phase"
        )

        assert result["action"] == ApprovalAction.EDIT
        assert result["data"]["result"] == "test"

    @pytest.mark.asyncio
    async def test_checkpoint_summary(self):
        """Test checkpoint summary generation"""
        controller = HILController(enable_hil=True, auto_approve=True)

        # Add some checkpoints
        await controller.checkpoint(CheckpointType.TREND_REVIEW, {}, "Phase 1")
        await controller.checkpoint(CheckpointType.RESEARCH_REVIEW, {}, "Phase 2")
        await controller.checkpoint(CheckpointType.REPORT_REVIEW, {}, "Phase 3")

        summary = controller.get_checkpoint_summary()

        assert summary["total_checkpoints"] == 3
        assert summary["approvals"] == 3
        assert summary["edits"] == 0
        assert summary["regenerations"] == 0

    @pytest.mark.asyncio
    @patch('core.hil_controller.Prompt.ask')
    async def test_multiple_checkpoints_history(self, mock_prompt):
        """Test checkpoint history tracks all checkpoints"""
        mock_prompt.side_effect = ["A", "R", "Q"]

        controller = HILController(enable_hil=True, auto_approve=False)

        await controller.checkpoint(CheckpointType.TREND_REVIEW, {}, "Phase 1")
        await controller.checkpoint(CheckpointType.RESEARCH_REVIEW, {}, "Phase 2")
        await controller.checkpoint(CheckpointType.REPORT_REVIEW, {}, "Phase 3")

        assert len(controller.checkpoint_history) == 3
        assert controller.checkpoint_history[0]["action"] == "approve"
        assert controller.checkpoint_history[1]["action"] == "regenerate"
        assert controller.checkpoint_history[2]["action"] == "quit"

    def test_create_hil_controller_from_config(self):
        """Test creating HIL controller from config"""
        from core.hil_controller import create_hil_controller

        config = {
            "hil": {
                "enabled": True,
                "auto_approve": False
            }
        }

        controller = create_hil_controller(config)

        assert controller.enable_hil is True
        assert controller.auto_approve is False

    def test_create_hil_controller_default(self):
        """Test creating HIL controller with defaults"""
        from core.hil_controller import create_hil_controller

        config = {}

        controller = create_hil_controller(config)

        assert controller.enable_hil is False
        assert controller.auto_approve is False

    @pytest.mark.asyncio
    async def test_trend_review_checkpoint(self):
        """Test trend review checkpoint displays correctly"""
        controller = HILController(enable_hil=True, auto_approve=True)

        data = {
            "result": "Test trend data with some content",
            "urls": ["http://example.com"]
        }

        result = await controller.checkpoint(
            CheckpointType.TREND_REVIEW,
            data,
            "Trend Scouting"
        )

        assert result["action"] == ApprovalAction.APPROVE
        assert result["data"] == data

    @pytest.mark.asyncio
    async def test_research_review_checkpoint(self):
        """Test research review checkpoint displays correctly"""
        controller = HILController(enable_hil=True, auto_approve=True)

        data = {
            "history": {"result": "Historical data", "urls": []},
            "white_papers": {"result": "Paper data", "urls": []},
            "news": {"result": "News data", "urls": []},
            "books": {"result": "Book data", "urls": []}
        }

        result = await controller.checkpoint(
            CheckpointType.RESEARCH_REVIEW,
            data,
            "Research Phase"
        )

        assert result["action"] == ApprovalAction.APPROVE
        assert result["data"] == data

    @pytest.mark.asyncio
    async def test_report_review_checkpoint(self):
        """Test report review checkpoint displays correctly"""
        controller = HILController(enable_hil=True, auto_approve=True)

        data = {
            "final_report": "# Test Report\n\nThis is a test report with multiple lines.\n" * 10
        }

        result = await controller.checkpoint(
            CheckpointType.REPORT_REVIEW,
            data,
            "Report Generation"
        )

        assert result["action"] == ApprovalAction.APPROVE
        assert result["data"] == data
