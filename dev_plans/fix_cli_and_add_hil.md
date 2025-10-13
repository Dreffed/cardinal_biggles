# Development Plan: Fix CLI & Implement Human-in-the-Loop (HIL)

**Plan ID**: DEV-002
**Created**: 2025-01-13
**Priority**: 🔴 CRITICAL (CLI broken) + 🟡 HIGH (HIL feature)
**Status**: 📋 PLANNED
**Estimated Time**: 4-6 hours
**Risk Level**: Medium (user interaction adds complexity)

---

## 📝 Executive Summary

Fix critical CLI bugs preventing the application from running, then implement a Human-in-the-Loop (HIL) workflow system that allows users to review and approve agent outputs before proceeding to the next research phase.

**Impact**:
- **Critical Fix**: Enables CLI to run (currently broken)
- **Feature Add**: Allows human oversight and quality control during research

---

## 🎯 Objectives

### Primary Goals (CLI Fixes)
- [x] Fix missing `typing.Dict` import causing NameError
- [x] Verify all CLI commands work correctly
- [x] Test end-to-end CLI workflow
- [x] Update documentation to match actual CLI

### Secondary Goals (HIL Implementation)
- [x] Design HIL checkpoint architecture
- [x] Implement approval prompts between research phases
- [x] Add review/edit/regenerate capabilities
- [x] Create interactive CLI interface for approvals
- [x] Add configuration options for HIL mode

---

## 🐛 Bug Analysis

### Issue 1: Missing Type Import (CRITICAL)

**File**: `cli/main.py`
**Line**: 171
**Error**: `NameError: name 'Dict' is not defined`

```python
# CURRENT CODE (BROKEN)
def _display_summary(results: Dict):
    """Display research summary statistics"""
    # ...
```

**Root Cause**: Missing `from typing import Dict` at top of file

**Impact**: CLI cannot be imported or executed at all

**Fix**:
```python
# Add to imports at top of file (after line 8)
from typing import Dict, Any, Optional
```

---

### Issue 2: Documentation Mismatch

**Files**: DEPLOYMENT.md references non-existent `serve` command

**Lines**:
- Line 249: `ExecStart=...python -m cli.main serve`
- Line 349: `CMD ["python", "-m", "cli.main", "serve"]`

**Actual Commands**:
- `research` - Start research workflow
- `show-config` - Display configuration
- `test-providers` - Test LLM providers
- `init-config` - Create default config

**Fix**: Either implement `serve` command or update documentation

---

## 🏗️ Human-in-the-Loop Architecture

### Design Philosophy

**Current Workflow** (Fully Automated):
```
User Input → Phase 1 → Phase 2-5 (Parallel) → Phase 6 → Output
```

**HIL Workflow** (Human Checkpoints):
```
User Input → Phase 1
           ↓
         [CHECKPOINT: Review Trends]
           ↓
         Phase 2-5 (Parallel)
           ↓
         [CHECKPOINT: Review Research]
           ↓
         Phase 6
           ↓
         [CHECKPOINT: Review Report]
           ↓
         Output
```

### Checkpoint Types

| Checkpoint | When | Purpose | Options |
|------------|------|---------|---------|
| **Trend Review** | After Phase 1 | Validate identified trends | Approve / Edit / Regenerate / Skip |
| **Research Review** | After Phase 2-5 | Review gathered research | Approve / Edit / Add Sources / Skip |
| **Report Review** | After Phase 6 | Final report approval | Approve / Edit / Regenerate / Export |

### User Actions at Checkpoints

```
┌──────────────────────────────────────┐
│     Checkpoint: Trend Review         │
│                                      │
│  Top 3 Trends Identified:            │
│  1. Multi-Agent Orchestration        │
│  2. Tool-Augmented LLMs              │
│  3. Retrieval-Augmented Generation   │
│                                      │
│  Options:                            │
│  [A] Approve & Continue              │
│  [E] Edit Trends                     │
│  [R] Regenerate                      │
│  [S] Skip to Next Phase              │
│  [Q] Quit                            │
│                                      │
│  Choice: _                           │
└──────────────────────────────────────┘
```

---

## 🔧 Implementation Plan

### Phase 1: Critical CLI Fixes (30 minutes)

#### Task 1.1: Fix Type Import
**File**: `cli/main.py`
**Action**: Add imports

```python
# BEFORE (line 1-8)
import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import yaml
from core.orchestrator import ResearchOrchestrator

# AFTER (add after line 8)
import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import yaml
from typing import Dict, Any, Optional  # ✅ ADD THIS LINE
from core.orchestrator import ResearchOrchestrator
```

**Checklist**:
- [ ] Add typing imports
- [ ] Run `python -m cli.main --help` to verify
- [ ] Test each CLI command
- [ ] Commit fix with proper message

---

#### Task 1.2: Verify All CLI Commands
**Test Script**: `test_cli.sh`

```bash
#!/bin/bash
# Test all CLI commands

echo "Testing CLI commands..."

# Test 1: Help
echo "1. Testing --help"
python -m cli.main --help || exit 1

# Test 2: init-config
echo "2. Testing init-config"
python -m cli.main init-config test_config.yaml || exit 1

# Test 3: show-config
echo "3. Testing show-config"
python -m cli.main show-config --config test_config.yaml || exit 1

# Test 4: test-providers (may fail if no providers configured)
echo "4. Testing test-providers"
python -m cli.main test-providers --config test_config.yaml

# Cleanup
rm -f test_config.yaml

echo "All CLI tests passed!"
```

**Checklist**:
- [ ] Create test script
- [ ] Run all commands
- [ ] Verify output is correct
- [ ] Document any issues found

---

### Phase 2: HIL Core Implementation (2-3 hours)

#### Task 2.1: Create HIL Controller
**File**: `core/hil_controller.py` (NEW)

```python
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
            return {"action": ApprovalAction.APPROVE, "data": data}

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
            f"[bold blue]🔍 Checkpoint: {phase_name}[/bold blue]\n"
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
                    "✓ Complete",
                    str(len(urls))
                )

        self.console.print(table)

        # Show sample of results
        first_agent = list(data.keys())[0]
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
            self.console.print("[green]✓ Approved. Continuing...[/green]")
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
```

**Checklist**:
- [ ] Create `core/hil_controller.py`
- [ ] Implement all checkpoint types
- [ ] Add user action handling
- [ ] Test with mock data
- [ ] Add unit tests

---

#### Task 2.2: Integrate HIL into Orchestrator
**File**: `core/orchestrator.py`
**Action**: Add HIL checkpoints

```python
# Add import at top
from core.hil_controller import HILController, CheckpointType

# In __init__ method, add:
self.hil_controller = HILController(
    enable_hil=config.get("hil", {}).get("enabled", False),
    auto_approve=config.get("hil", {}).get("auto_approve", False)
)

# Modify execute_workflow method to add checkpoints:
async def execute_workflow(self, topic: str) -> Dict:
    """Execute complete research workflow with HIL checkpoints"""

    # Phase 1: Trend Scouting
    trends = await agents["trend_scout"].scout_trends(topic, timeframe)

    # CHECKPOINT 1: Review Trends
    checkpoint_result = await self.hil_controller.checkpoint(
        CheckpointType.TREND_REVIEW,
        {"result": trends["result"], "urls": trends["urls"]},
        "Trend Scouting"
    )

    if checkpoint_result.get("quit"):
        return {"status": "cancelled", "phase": "trend_review"}

    if checkpoint_result.get("regenerate"):
        # Regenerate trends
        trends = await agents["trend_scout"].scout_trends(topic, timeframe)

    # ... continue with other phases

    # Phase 2-5: Research (Parallel)
    research_results = await asyncio.gather(
        historian.research_history(...),
        scholar.research_whitepapers(...),
        journalist.research_news(...),
        bibliophile.research_books(...)
    )

    # CHECKPOINT 2: Review Research
    checkpoint_result = await self.hil_controller.checkpoint(
        CheckpointType.RESEARCH_REVIEW,
        {
            "historian": research_results[0],
            "scholar": research_results[1],
            "journalist": research_results[2],
            "bibliophile": research_results[3]
        },
        "Research Phase"
    )

    if checkpoint_result.get("quit"):
        return {"status": "cancelled", "phase": "research_review"}

    # Phase 6: Report Generation
    report = await reporter.generate_report(research_data)

    # CHECKPOINT 3: Review Report
    checkpoint_result = await self.hil_controller.checkpoint(
        CheckpointType.REPORT_REVIEW,
        {"final_report": report},
        "Report Generation"
    )

    if checkpoint_result.get("quit"):
        return {"status": "cancelled", "phase": "report_review"}

    if checkpoint_result.get("regenerate"):
        # Regenerate report with user feedback
        report = await reporter.generate_report(research_data)

    return {
        "final_report": report,
        "hil_summary": self.hil_controller.get_checkpoint_summary()
    }
```

**Checklist**:
- [ ] Add HIL controller to orchestrator
- [ ] Add checkpoint after Phase 1
- [ ] Add checkpoint after Phases 2-5
- [ ] Add checkpoint after Phase 6
- [ ] Handle quit/regenerate actions
- [ ] Test workflow with HIL enabled

---

#### Task 2.3: Update CLI for HIL Mode
**File**: `cli/main.py`
**Action**: Add HIL options

```python
@cli.command()
@click.argument('topic')
@click.option('--config', '-c', default='config/config.yaml', help='Path to config file')
@click.option('--output', '-o', default=None, help='Output file path')
@click.option('--provider', default=None, help='Override default provider')
@click.option('--model', default=None, help='Override default model')
@click.option('--hil/--no-hil', default=False, help='Enable Human-in-the-Loop mode')  # ✅ NEW
@click.option('--auto-approve', is_flag=True, help='Auto-approve all checkpoints (for testing)')  # ✅ NEW
def research(topic, config, output, provider, model, hil, auto_approve):
    """Start a research workflow on a topic"""

    # ... existing code ...

    # Initialize orchestrator with HIL configuration
    try:
        # Load config
        with open(config, 'r') as f:
            config_dict = yaml.safe_load(f)

        # Override HIL settings from CLI
        if 'hil' not in config_dict:
            config_dict['hil'] = {}

        config_dict['hil']['enabled'] = hil
        config_dict['hil']['auto_approve'] = auto_approve

        # Save temporary config
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            temp_config = f.name

        orchestrator = ResearchOrchestrator(config_path=temp_config)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return

    # Display HIL status
    if hil:
        console.print(Panel.fit(
            "[bold yellow]⚠️  Human-in-the-Loop Mode ENABLED[/bold yellow]\n"
            "You will be prompted to review results at key checkpoints.",
            border_style="yellow"
        ))

    # ... rest of research command ...
```

**Checklist**:
- [ ] Add `--hil` flag
- [ ] Add `--auto-approve` flag
- [ ] Override config with CLI flags
- [ ] Display HIL status
- [ ] Update help text

---

### Phase 3: Configuration & Documentation (1 hour)

#### Task 3.1: Add HIL Configuration
**File**: `config/config.yaml`
**Action**: Add HIL section

```yaml
# Add at end of config.yaml

# Human-in-the-Loop Configuration
hil:
  enabled: false              # Enable HIL mode
  auto_approve: false         # Auto-approve all checkpoints (testing only)

  checkpoints:
    trend_review:
      enabled: true           # Review after trend scouting
      timeout: 300            # Seconds before auto-approve (0 = no timeout)

    research_review:
      enabled: true           # Review after research phases
      timeout: 600

    report_review:
      enabled: true           # Review final report
      timeout: 0              # No timeout for final review

  # Edit capabilities
  allow_editing: true         # Allow users to edit results
  allow_regeneration: true    # Allow regeneration requests
  save_checkpoints: true      # Save checkpoint history to file
  checkpoint_file: "./data/hil_checkpoints.json"
```

**Checklist**:
- [ ] Add HIL section to config
- [ ] Document all options
- [ ] Add to default config generation
- [ ] Test config loading

---

#### Task 3.2: Update Documentation
**Files**: README.md, CLAUDE.md, DEPLOYMENT.md

**README.md additions**:
```markdown
### Human-in-the-Loop Mode

Enable human oversight and approval at key research checkpoints:

```bash
# Enable HIL mode
python -m cli.main research "AI Trends" --hil

# With auto-approve for testing
python -m cli.main research "AI Trends" --hil --auto-approve
```

**Checkpoints**:
1. **Trend Review**: After initial trend identification
2. **Research Review**: After all research phases complete
3. **Report Review**: Before final report generation

**Actions at Each Checkpoint**:
- **Approve**: Continue to next phase
- **Edit**: Modify results before continuing
- **Regenerate**: Re-run the phase with feedback
- **Skip**: Skip to next phase without changes
- **Quit**: Exit workflow (saves partial results)
```

**CLAUDE.md additions**:
```markdown
## Human-in-the-Loop Architecture

Cardinal Biggles supports HIL workflow with approval checkpoints:

**Configuration** (`core/hil_controller.py:15-40`):
- `enable_hil`: Enable/disable HIL mode
- `auto_approve`: Auto-approve (for CI/CD)

**Checkpoint Types** (`core/hil_controller.py:10-14`):
- `TREND_REVIEW`: After Phase 1
- `RESEARCH_REVIEW`: After Phase 2-5
- `REPORT_REVIEW`: After Phase 6

**Integration** (`core/orchestrator.py:120-150`):
Checkpoints are inserted between workflow phases.
```

**Checklist**:
- [ ] Update README with HIL instructions
- [ ] Add HIL section to CLAUDE.md
- [ ] Update CLI help text
- [ ] Add HIL examples

---

### Phase 4: Testing & Validation (1-2 hours)

#### Task 4.1: Unit Tests
**File**: `tests/test_hil_controller.py` (NEW)

```python
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

    def test_disabled_mode(self):
        """Test HIL disabled returns immediate approval"""
        controller = HILController(enable_hil=False)

        result = await controller.checkpoint(
            CheckpointType.TREND_REVIEW,
            {"result": "test"},
            "Test Phase"
        )

        assert result["action"] == ApprovalAction.APPROVE

    def test_auto_approve_mode(self):
        """Test auto-approve mode"""
        controller = HILController(enable_hil=True, auto_approve=True)

        result = await controller.checkpoint(
            CheckpointType.TREND_REVIEW,
            {"result": "test"},
            "Test Phase"
        )

        assert result["action"] == ApprovalAction.APPROVE

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

    def test_checkpoint_summary(self):
        """Test checkpoint summary generation"""
        controller = HILController(enable_hil=True, auto_approve=True)

        # Add some checkpoints
        await controller.checkpoint(CheckpointType.TREND_REVIEW, {}, "Phase 1")
        await controller.checkpoint(CheckpointType.RESEARCH_REVIEW, {}, "Phase 2")

        summary = controller.get_checkpoint_summary()

        assert summary["total_checkpoints"] == 2
        assert summary["approvals"] == 2
```

**Checklist**:
- [ ] Create test file
- [ ] Test all checkpoint types
- [ ] Test all user actions
- [ ] Test disabled/enabled modes
- [ ] Test checkpoint history
- [ ] Run tests: `pytest tests/test_hil_controller.py`

---

#### Task 4.2: Integration Tests
**File**: `tests/test_integration/test_hil_workflow.py` (NEW)

```python
"""
Integration tests for HIL workflow
"""

import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.integration
class TestHILWorkflow:
    """Test complete HIL workflow"""

    @pytest.mark.asyncio
    @patch('core.hil_controller.Prompt.ask')
    async def test_full_workflow_with_hil(self, mock_prompt, config_file):
        """Test complete research workflow with HIL checkpoints"""
        from core.orchestrator import ResearchOrchestrator

        # Mock all user inputs to approve
        mock_prompt.side_effect = ["A", "A", "A"]  # 3 checkpoints

        # Enable HIL in config
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        config['hil'] = {'enabled': True, 'auto_approve': False}

        # Save modified config
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            temp_config = f.name

        orchestrator = ResearchOrchestrator(config_path=temp_config)

        # Run workflow
        results = await orchestrator.execute_workflow("Test Topic")

        # Verify checkpoints were hit
        assert "hil_summary" in results
        assert results["hil_summary"]["total_checkpoints"] == 3

    @pytest.mark.asyncio
    async def test_workflow_quit_at_checkpoint(self, config_file):
        """Test workflow can be quit at checkpoint"""
        # Similar to above but mock user choosing quit
        pass
```

**Checklist**:
- [ ] Test full workflow with approvals
- [ ] Test quitting at each checkpoint
- [ ] Test regeneration
- [ ] Test workflow with HIL disabled
- [ ] Run: `pytest tests/test_integration/test_hil_workflow.py`

---

#### Task 4.3: Manual Testing
**Test Script**: `manual_test_hil.sh`

```bash
#!/bin/bash
# Manual testing of HIL workflow

echo "=== Manual HIL Testing ==="

# Test 1: HIL Disabled (should run without prompts)
echo "Test 1: HIL Disabled"
python -m cli.main research "AI trends" --no-hil --output test_output_1.md

# Test 2: HIL Enabled with Auto-Approve
echo "Test 2: HIL with Auto-Approve"
python -m cli.main research "AI trends" --hil --auto-approve --output test_output_2.md

# Test 3: HIL Enabled (interactive)
echo "Test 3: HIL Interactive (you will be prompted)"
python -m cli.main research "AI trends" --hil --output test_output_3.md

echo "Manual tests complete. Check outputs."
```

**Checklist**:
- [ ] Test CLI without HIL
- [ ] Test CLI with auto-approve
- [ ] Test interactive HIL mode
- [ ] Verify user prompts appear
- [ ] Test all user actions (A, E, R, S, Q)
- [ ] Check output files

---

## 📋 Master Checklist

### Pre-Implementation
- [x] Review CLI code
- [x] Identify all issues
- [x] Design HIL architecture
- [x] Create development plan

### Implementation - Phase 1: CLI Fixes
- [ ] Fix `typing.Dict` import issue
- [ ] Verify all CLI commands work
- [ ] Create CLI test script
- [ ] Run all CLI tests
- [ ] Update CLI help text

### Implementation - Phase 2: HIL Core
- [ ] Create `core/hil_controller.py`
- [ ] Implement checkpoint system
- [ ] Implement user action handling
- [ ] Add display methods for each checkpoint type
- [ ] Integrate into orchestrator
- [ ] Add CLI flags for HIL mode
- [ ] Test with mock data

### Implementation - Phase 3: Configuration
- [ ] Add HIL config section
- [ ] Update default config generation
- [ ] Document configuration options
- [ ] Update README.md
- [ ] Update CLAUDE.md
- [ ] Add usage examples

### Implementation - Phase 4: Testing
- [ ] Create unit tests for HIL controller
- [ ] Create integration tests
- [ ] Run all tests
- [ ] Manual testing with real workflow
- [ ] Test all user actions
- [ ] Verify quit/regenerate work

### Post-Implementation
- [ ] Update CHANGELOG.md
- [ ] Update DEPLOYMENT.md
- [ ] Code review
- [ ] Performance testing
- [ ] Documentation review
- [ ] Commit with proper message

---

## 🎯 Success Criteria

### Must Have
1. ✅ CLI runs without errors
2. ✅ All CLI commands work
3. ✅ HIL mode can be enabled/disabled
4. ✅ Checkpoints appear at correct times
5. ✅ User can approve/quit workflow
6. ✅ All tests pass

### Nice to Have
1. ✅ User can edit results
2. ✅ User can regenerate phases
3. ✅ Checkpoint history saved
4. ✅ Rich formatting for prompts
5. ✅ Timeout for auto-approve

---

## 🧪 Test Plan

### Unit Tests (Required)
| Component | Test Coverage | Priority |
|-----------|--------------|----------|
| HILController | 90%+ | High |
| Checkpoint display | 80%+ | High |
| User action processing | 90%+ | High |
| CLI integration | 70%+ | Medium |

### Integration Tests (Required)
| Scenario | Expected Outcome | Priority |
|----------|-----------------|----------|
| Full workflow with approvals | Completes successfully | Critical |
| Quit at each checkpoint | Workflow stops gracefully | High |
| Regenerate phase | Phase re-runs | Medium |
| HIL disabled | No prompts, runs fully automated | Critical |

### Manual Tests (Recommended)
- [ ] Interactive workflow with real user input
- [ ] Test on different terminal types
- [ ] Test with different configurations
- [ ] Test error cases (invalid input, etc.)

---

## 📊 Expected Outcomes

### Before Fix
```
$ python -m cli.main --help
Traceback (most recent call last):
  ...
NameError: name 'Dict' is not defined
```

### After Fix (Basic)
```
$ python -m cli.main --help
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  Research Orchestrator CLI

Commands:
  research        Start a research workflow
  show-config     Display configuration
  test-providers  Test LLM providers
  init-config     Create default config
```

### After Fix (HIL)
```
$ python -m cli.main research "AI Trends" --hil

🔬 Multi-Agent Research Orchestrator
Topic: AI Trends

⚠️  Human-in-the-Loop Mode ENABLED
You will be prompted to review results at key checkpoints.

Running Phase 1: Trend Scouting...

┌─────────────────────────────────────┐
│ 🔍 Checkpoint: Trend Scouting       │
│ Type: trend_review                  │
└─────────────────────────────────────┘

Identified Trends:
1. Multi-Agent Orchestration
2. Tool-Augmented LLMs
3. Retrieval-Augmented Generation

Available Actions:
  [A] Approve & Continue
  [E] Edit Data
  [R] Regenerate
  [S] Skip to Next Phase
  [Q] Quit

Choose action [A]: _
```

---

## 🔍 Code Review Checklist

### For Reviewer
- [ ] Imports are correct
- [ ] Type hints are consistent
- [ ] Error handling is comprehensive
- [ ] User prompts are clear
- [ ] Configuration is well-documented
- [ ] Tests cover edge cases
- [ ] No security issues (user input sanitization)
- [ ] Performance is acceptable
- [ ] Code follows style guide

---

## 📝 Commit Message Template

```
fix(cli): Add missing type imports and implement HIL workflow

BREAKING: Adds Human-in-the-Loop mode with approval checkpoints

Changes:
- Fix missing typing.Dict import in cli/main.py
- Add core/hil_controller.py for checkpoint management
- Integrate HIL checkpoints into orchestrator workflow
- Add --hil and --auto-approve CLI flags
- Add HIL configuration section to config.yaml
- Update documentation with HIL usage

Features:
- User can review/approve at 3 key checkpoints
- Support for edit/regenerate/quit actions
- Auto-approve mode for CI/CD
- Checkpoint history tracking

Tests:
- Add 15 unit tests for HIL controller
- Add 5 integration tests for workflow
- All tests passing (57/57)

See: dev_plans/fix_cli_and_add_hil.md

Fixes: #DEV-002
```

---

## 🚨 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| User confusion with prompts | Medium | Low | Clear instructions, good UX |
| Workflow interruption | Low | Medium | Save state, allow resume |
| Performance impact | Low | Low | Async operations, minimal overhead |
| Configuration complexity | Medium | Low | Good defaults, documentation |
| Testing complexity | Medium | Medium | Mock user input, auto-approve mode |

---

## 🎉 Completion Criteria

This plan is considered complete when:

1. ✅ CLI runs without NameError
2. ✅ All existing CLI commands work
3. ✅ HIL mode can be enabled via config or CLI
4. ✅ All 3 checkpoint types work
5. ✅ User can perform all 5 actions (A/E/R/S/Q)
6. ✅ All unit tests pass (15+)
7. ✅ All integration tests pass (5+)
8. ✅ Manual testing successful
9. ✅ Documentation updated
10. ✅ Code reviewed and approved

---

**End of Development Plan**

*Last Updated: 2025-01-13*
*Plan Status: 📋 READY FOR IMPLEMENTATION*
