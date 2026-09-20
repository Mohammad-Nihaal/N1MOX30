import os
import shutil
import subprocess
from typing import Optional


class OpenClawProvider:
    """
    OpenClaw AI provider.

    Uses the OpenClaw CLI inference interface:

        openclaw infer model run --local --prompt "..."

    The provider supports:
    - Windows
    - PowerShell environments
    - .cmd OpenClaw installations
    - UTF-8 output
    - OmniRoute models
    - timeout protection
    - empty response detection
    """

    def __init__(self) -> None:
        self.command = self._find_command()

    def _find_command(self) -> Optional[str]:
        """
        Locate the OpenClaw executable.

        Priority:
        1. OPENCLAW_COMMAND environment variable
        2. openclaw on PATH
        3. openclaw.cmd on PATH
        4. Windows npm global directory
        """

        env_command = os.getenv("OPENCLAW_COMMAND")

        if env_command:
            env_command = env_command.strip()

            if env_command and os.path.exists(env_command):
                return env_command

        command = shutil.which("openclaw")

        if command:
            return command

        command = shutil.which("openclaw.cmd")

        if command:
            return command

        appdata = os.getenv("APPDATA")

        if appdata:
            windows_command = os.path.join(
                appdata,
                "npm",
                "openclaw.cmd",
            )

            if os.path.exists(windows_command):
                return windows_command

        return None

    def is_available(self) -> bool:
        """
        Check whether OpenClaw is available.
        """

        if not self.command:
            return False

        try:

            process = subprocess.run(
                [
                    self.command,
                    "--version",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                shell=False,
            )

            return process.returncode == 0

        except Exception:
            return False

    def _clean_output(
        self,
        output: str,
    ) -> str:
        """
        Extract the AI response from OpenClaw CLI output.

        OpenClaw prints metadata such as:

            model.run via local
            provider: omniroute
            model: auto
            outputs: 1

        The actual model response follows that metadata.
        """

        if not output:
            return ""

        text = output.replace("\r\n", "\n")

        lines = text.split("\n")

        cleaned_lines = []

        skip_prefixes = (
            "model.run via ",
            "provider:",
            "model:",
            "outputs:",
            "16:",
            "17:",
            "18:",
            "19:",
            "20:",
            "21:",
            "22:",
            "23:",
            "00:",
            "01:",
            "02:",
            "03:",
            "04:",
            "05:",
            "06:",
            "07:",
            "08:",
            "09:",
            "🦞",
            "◇",
            "│",
        )

        for line in lines:

            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith(skip_prefixes):
                continue

            if (
                stripped.startswith("[provider-")
                or stripped.startswith("Usage:")
                or stripped.startswith("Options:")
            ):
                continue

            cleaned_lines.append(
                stripped
            )

        return "\n".join(
            cleaned_lines
        ).strip()

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate AI text using OpenClaw.

        Temperature is currently accepted for provider
        compatibility. The current OpenClaw CLI command
        uses the configured model defaults.
        """

        if not prompt or not prompt.strip():

            raise ValueError(
                "OpenClaw prompt cannot be empty."
            )

        if not self.command:

            raise RuntimeError(
                "OpenClaw command was not found. "
                "Make sure OpenClaw is installed "
                "and available in PATH."
            )

        command = [
    self.command,
    "infer",
    "model",
    "run",
    "--local",
    "--model",
    "omniroute/groq/openai/gpt-oss-120b",
    "--prompt",
" ".join(prompt.strip().split()),
]

        try:

            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                shell=False,
                env={
                    **os.environ,
                    "PYTHONIOENCODING": "utf-8",
                    "LANG": "en_US.UTF-8",
                },
            )

        except subprocess.TimeoutExpired as error:

            raise RuntimeError(
                "OpenClaw inference timed out "
                "after 180 seconds."
            ) from error

        except FileNotFoundError as error:

            raise RuntimeError(
                "OpenClaw command was not found. "
                "Make sure OpenClaw is installed "
                "and available in PATH."
            ) from error

        except Exception as error:

            raise RuntimeError(
                f"Unable to execute OpenClaw: {error}"
            ) from error

        stdout = (
            process.stdout or ""
        )

        stderr = (
            process.stderr or ""
        )

        if process.returncode != 0:

            error_message = (
                stderr.strip()
                or stdout.strip()
                or "Unknown OpenClaw error."
            )

            raise RuntimeError(
                "OpenClaw inference failed: "
                f"{error_message}"
            )

        result = self._clean_output(
            stdout
        )

        if not result:

            raise RuntimeError(
                "OpenClaw returned an empty response."
            )

        return result


openclaw_provider = OpenClawProvider()