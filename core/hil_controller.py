"""
Human-in-the-Loop Controller for Cardinal Biggles
Manages approval checkpoints and user interaction
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
import json


class CheckpointType(Enum):
    """Types of approval checkpoints"""
    TREND_REVIEW = "trend_review"
    RESEARCH_REVIEW = "research_review"
    REPORT_REVIEW = "report_review"


class ApprovalAction(Enum):
    """User actions at checkpoints"""
    APPROVE = "approve"
    EDIT = "edit"
    REGENERATE = "regenerate"
    SKIP = "skip"
    QUIT = "quit"


class HILController:
    """
    Controls human-in-the-loop workflow with approval checkpoints
    """

    def __init__(self, enable_hil: bool = True, auto_approve: bool = False):
        """
        Initialize HIL controller

        Args:
            enable_hil: Enable human-in-the-loop mode
            auto_approve: Auto-approve all checkpoints (for testing)
        """
        self.enable_hil = enable_hil
        self.auto_approve = auto_approve
        self.console = Console()
        self.checkpoint_history: List[Dict] = []

    async def checkpoint(
        self,
        checkpoint_type: CheckpointType,
        data: Dict[str, Any],
        phase_name: str
    ) -> Dict[str, Any]:
        """
        Present checkpoint to user for approval

        Args:
            checkpoint_type: Type of checkpoint
            data: Data to review
            phase_name: Name of the phase

        Returns:
            Dict with action and potentially modified data
        """
        if not self.enable_hil:
            return {"action": ApprovalAction.APPROVE, "data": data}

        if self.auto_approve:
            self.console.print(f"[yellow]Auto-approving {phase_name}[/yellow]")
            action = ApprovalAction.APPROVE
            # Record in history
            self.checkpoint_history.append({
                "type": checkpoint_type.value,
                "phase": phase_name,
                "action": action.value,
                "timestamp": self._get_timestamp()
            })
            return {"action": action, "data": data}

        # Display checkpoint
        self._display_checkpoint(checkpoint_type, data, phase_name)

        # Get user action
        action = self._get_user_action(checkpoint_type)

        # Process action
        result = await self._process_action(action, data, checkpoint_type)

        # Record in history
        self.checkpoint_history.append({
            "type": checkpoint_type.value,
            "phase": phase_name,
            "action": action.value,
            "timestamp": self._get_timestamp()
        })

        return result

    def _display_checkpoint(
        self,
        checkpoint_type: CheckpointType,
        data: Dict[str, Any],
        phase_name: str
    ):
        """Display checkpoint information to user"""

        self.console.print()
        self.console.print(Panel.fit(
            f"[bold blue]Checkpoint: {phase_name}[/bold blue]\n"
            f"Type: {checkpoint_type.value}",
            border_style="blue"
        ))

        if checkpoint_type == CheckpointType.TREND_REVIEW:
            self._display_trend_review(data)
        elif checkpoint_type == CheckpointType.RESEARCH_REVIEW:
            self._display_research_review(data)
        elif checkpoint_type == CheckpointType.REPORT_REVIEW:
            self._display_report_review(data)

    def _display_trend_review(self, data: Dict):
        """Display trends for review"""
        result = data.get("result", "")

        self.console.print("\n[bold]Identified Trends:[/bold]")
        self.console.print(result[:1000])  # First 1000 chars

        if len(result) > 1000:
            self.console.print(f"\n[dim]... ({len(result) - 1000} more characters)[/dim]")

    def _display_research_review(self, data: Dict):
        """Display research findings for review"""
        table = Table(title="Research Phase Results")
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("URLs Found", style="yellow")

        for agent_name, agent_data in data.items():
            if isinstance(agent_data, dict):
                urls = agent_data.get("urls", [])
                table.add_row(
                    agent_name.replace("_", " ").title(),
                    "Complete",
                    str(len(urls))
                )

        self.console.print(table)

        # Show sample of results
        first_agent = list(data.keys())[0] if data else None
        if first_agent:
            sample = data[first_agent].get("result", "")[:500]
            self.console.print(f"\n[bold]Sample Output ({first_agent}):[/bold]")
            self.console.print(sample)

    def _display_report_review(self, data: Dict):
        """Display report for review"""
        report = data.get("final_report", "")

        # Show report metadata
        lines = report.split('\n')
        preview_lines = min(50, len(lines))

        self.console.print(f"\n[bold]Report Preview (first {preview_lines} lines):[/bold]")
        self.console.print('\n'.join(lines[:preview_lines]))

        if len(lines) > preview_lines:
            self.console.print(f"\n[dim]... ({len(lines) - preview_lines} more lines)[/dim]")

        # Show stats
        self.console.print(f"\n[bold]Report Stats:[/bold]")
        self.console.print(f"  Total Lines: {len(lines)}")
        self.console.print(f"  Total Characters: {len(report)}")
        self.console.print(f"  Estimated Pages: {len(report) // 3000}")

    def _get_user_action(self, checkpoint_type: CheckpointType) -> ApprovalAction:
        """Prompt user for action at checkpoint"""

        self.console.print("\n[bold cyan]Available Actions:[/bold cyan]")
        self.console.print("  [A] Approve & Continue")
        self.console.print("  [E] Edit Data")
        self.console.print("  [R] Regenerate")
        self.console.print("  [S] Skip to Next Phase")
        self.console.print("  [Q] Quit")

        while True:
            choice = Prompt.ask(
                "\nChoose action",
                choices=["A", "E", "R", "S", "Q"],
                default="A"
            ).upper()

            action_map = {
                "A": ApprovalAction.APPROVE,
                "E": ApprovalAction.EDIT,
                "R": ApprovalAction.REGENERATE,
                "S": ApprovalAction.SKIP,
                "Q": ApprovalAction.QUIT
            }

            return action_map[choice]

    async def _process_action(
        self,
        action: ApprovalAction,
        data: Dict,
        checkpoint_type: CheckpointType
    ) -> Dict[str, Any]:
        """Process user action"""

        if action == ApprovalAction.APPROVE:
            self.console.print("[green]Approved. Continuing...[/green]")
            return {"action": action, "data": data}

        elif action == ApprovalAction.EDIT:
            edited_data = self._edit_data(data, checkpoint_type)
            return {"action": action, "data": edited_data}

        elif action == ApprovalAction.REGENERATE:
            self.console.print("[yellow]Requesting regeneration...[/yellow]")
            return {"action": action, "data": data, "regenerate": True}

        elif action == ApprovalAction.SKIP:
            self.console.print("[yellow]Skipping to next phase...[/yellow]")
            return {"action": action, "data": data}

        elif action == ApprovalAction.QUIT:
            self.console.print("[red]Quitting workflow...[/red]")
            return {"action": action, "data": data, "quit": True}

    def _edit_data(self, data: Dict, checkpoint_type: CheckpointType) -> Dict:
        """Allow user to edit data"""

        self.console.print("\n[bold]Edit Mode[/bold]")
        self.console.print("[yellow]Opening editor for data modification...[/yellow]")

        # For now, just return original data
        # In full implementation, open editor or provide line-by-line editing
        self.console.print("[yellow]Note: Full editing not yet implemented[/yellow]")

        if Confirm.ask("Keep original data?", default=True):
            return data
        else:
            # Minimal edit: let user add a note
            note = Prompt.ask("Add a note to the data")
            data["user_note"] = note
            return data

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_checkpoint_summary(self) -> Dict[str, Any]:
        """Get summary of all checkpoints"""
        return {
            "total_checkpoints": len(self.checkpoint_history),
            "approvals": sum(1 for c in self.checkpoint_history if c["action"] == "approve"),
            "edits": sum(1 for c in self.checkpoint_history if c["action"] == "edit"),
            "regenerations": sum(1 for c in self.checkpoint_history if c["action"] == "regenerate"),
            "history": self.checkpoint_history
        }


# Convenience function
def create_hil_controller(config: Dict[str, Any]) -> HILController:
    """Create HIL controller from configuration"""
    hil_config = config.get("hil", {})

    return HILController(
        enable_hil=hil_config.get("enabled", False),
        auto_approve=hil_config.get("auto_approve", False)
    )
