"""
CP-MVP2-03 — Claude provider adapter tests.

Per task governance ("Do NOT make real Claude calls as part of the
normal automated unit-test suite... Mock/stub the subprocess boundary"),
every test here mocks `llm.client.subprocess.run` and
`llm.client.shutil.which` — no real `claude` process is ever started, no
Claude Pro subscription usage is consumed, and no network call occurs.
"""
from __future__ import annotations

import json
import subprocess as real_subprocess
from unittest.mock import patch

import pytest

from llm.client import ClaudeLLMClient, ClaudeProviderError

VALID_CANDIDATE = {
    "scenario_type": "POSITIVE",
    "title": "Verify REQ-REG-01",
    "preconditions": [],
    "test_steps": ["step"],
    "expected_result": "result",
    "priority": "MEDIUM",
}

SAMPLE_CONTEXT = {
    "requirement_id": "REQ-REG-01",
    "requirement_text": "text",
    "approval_status": "APPROVED_BASELINED_V1_0",
    "evidence": [],
}


def _completed(returncode=0, stdout="", stderr=""):
    return real_subprocess.CompletedProcess(args=["claude"], returncode=returncode, stdout=stdout, stderr=stderr)


def _envelope(result_text, is_error=False):
    return json.dumps({"type": "result", "is_error": is_error, "result": result_text})


# ---------------------------------------------------------------------------
# Provider availability
# ---------------------------------------------------------------------------

def test_missing_executable_raises_provider_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("llm.client.shutil.which", return_value=None):
        with pytest.raises(ClaudeProviderError, match="not found on PATH"):
            ClaudeLLMClient()


def test_available_executable_constructs_successfully(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("llm.client.shutil.which", return_value="/usr/bin/claude"):
        client = ClaudeLLMClient()
        assert client.model_name == "claude-cli:default"


# ---------------------------------------------------------------------------
# Billing safety (ANTHROPIC_API_KEY guard)
# ---------------------------------------------------------------------------

def test_anthropic_api_key_present_raises_provider_error_before_touching_cli(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-totally-fake-secret-value")
    with patch("llm.client.shutil.which") as which_mock:
        with pytest.raises(ClaudeProviderError, match="ANTHROPIC_API_KEY"):
            ClaudeLLMClient()
        which_mock.assert_not_called()  # the billing guard must trip before even checking the CLI


def test_anthropic_api_key_value_never_appears_in_error_message(monkeypatch):
    secret = "sk-ant-totally-fake-secret-value-xyz123"
    monkeypatch.setenv("ANTHROPIC_API_KEY", secret)
    with pytest.raises(ClaudeProviderError) as excinfo:
        ClaudeLLMClient()
    assert secret not in str(excinfo.value)


# ---------------------------------------------------------------------------
# Successful execution
# ---------------------------------------------------------------------------

def test_successful_invocation_parses_candidates(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("llm.client.shutil.which", return_value="/usr/bin/claude"):
        client = ClaudeLLMClient()
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.client.subprocess.run", return_value=_completed(0, envelope, "")) as run_mock:
        candidates = client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])
    assert candidates == [VALID_CANDIDATE]
    run_mock.assert_called_once()


def test_argv_is_a_list_not_shell_and_uses_restricted_mode(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("llm.client.shutil.which", return_value="/usr/bin/claude"):
        client = ClaudeLLMClient()
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.client.subprocess.run", return_value=_completed(0, envelope, "")) as run_mock:
        client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])
    call_kwargs = run_mock.call_args.kwargs
    call_args = run_mock.call_args.args[0]
    assert isinstance(call_args, list)
    assert call_kwargs.get("shell") is False
    assert "--restricted" in call_args
    assert "--output-format" in call_args and "json" in call_args


def test_explicit_timeout_is_always_passed_to_subprocess_run(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("llm.client.shutil.which", return_value="/usr/bin/claude"):
        client = ClaudeLLMClient(timeout_seconds=5.0)
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.client.subprocess.run", return_value=_completed(0, envelope, "")) as run_mock:
        client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])
    assert run_mock.call_args.kwargs.get("timeout") == 5.0


# ---------------------------------------------------------------------------
# Failure handling
# ---------------------------------------------------------------------------

def _client(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("llm.client.shutil.which", return_value="/usr/bin/claude"):
        return ClaudeLLMClient()


def test_non_zero_exit_code_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    with patch("llm.client.subprocess.run", return_value=_completed(1, "", "some CLI error")):
        with pytest.raises(ClaudeProviderError, match="non-zero status"):
            client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])


def test_non_zero_exit_is_never_interpreted_as_success(monkeypatch):
    client = _client(monkeypatch)
    # stdout happens to contain something that WOULD parse as a valid
    # envelope, but the non-zero exit code must still win.
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.client.subprocess.run", return_value=_completed(2, envelope, "")):
        with pytest.raises(ClaudeProviderError, match="non-zero status"):
            client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])


def test_timeout_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    with patch("llm.client.subprocess.run", side_effect=real_subprocess.TimeoutExpired(cmd="claude", timeout=120)):
        with pytest.raises(ClaudeProviderError, match="timed out"):
            client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])


def test_missing_binary_at_call_time_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    with patch("llm.client.subprocess.run", side_effect=OSError("No such file or directory")):
        with pytest.raises(ClaudeProviderError, match="Failed to start"):
            client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])


def test_empty_stdout_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    with patch("llm.client.subprocess.run", return_value=_completed(0, "", "")):
        with pytest.raises(ClaudeProviderError, match="empty stdout"):
            client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])


def test_malformed_envelope_json_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    with patch("llm.client.subprocess.run", return_value=_completed(0, "{not json", "")):
        with pytest.raises(ClaudeProviderError, match="not valid JSON"):
            client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])


def test_is_error_true_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    envelope = _envelope("model reported failure", is_error=True)
    with patch("llm.client.subprocess.run", return_value=_completed(0, envelope, "")):
        with pytest.raises(ClaudeProviderError, match="is_error=true"):
            client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])


def test_missing_result_field_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    envelope = json.dumps({"type": "result", "is_error": False})  # no "result" key
    with patch("llm.client.subprocess.run", return_value=_completed(0, envelope, "")):
        with pytest.raises(ClaudeProviderError, match="'result' field"):
            client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])


def test_result_text_not_valid_json_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    envelope = _envelope("this is not JSON at all")
    with patch("llm.client.subprocess.run", return_value=_completed(0, envelope, "")):
        with pytest.raises(ClaudeProviderError, match="'result' text was not valid JSON"):
            client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])


def test_result_json_not_a_list_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    envelope = _envelope(json.dumps({"not": "a list"}))
    with patch("llm.client.subprocess.run", return_value=_completed(0, envelope, "")):
        with pytest.raises(ClaudeProviderError, match="not a list"):
            client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

def test_requirement_text_with_shell_metacharacters_is_passed_as_a_single_safe_argument(monkeypatch):
    client = _client(monkeypatch)
    dangerous_context = dict(SAMPLE_CONTEXT)
    dangerous_context["requirement_text"] = "; rm -rf / #$(whoami)`id`\nNEWLINE 'quote' \"dquote\" ☺"
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.client.subprocess.run", return_value=_completed(0, envelope, "")) as run_mock:
        client.propose_testcases(dangerous_context, ["POSITIVE"])
    call_args = run_mock.call_args.args[0]
    call_kwargs = run_mock.call_args.kwargs
    # No shell was used, so metacharacters cannot be reinterpreted:
    assert call_kwargs.get("shell") is False
    # The dangerous text must appear intact within exactly one argv
    # element (the JSON-encoded user prompt) — never split into
    # separate shell tokens.
    matching_elements = [a for a in call_args if "rm -rf" in a]
    assert len(matching_elements) == 1
    prompt_arg = call_args[call_args.index("-p") + 1]
    decoded = json.loads(prompt_arg)
    assert decoded["requirement_text"] == dangerous_context["requirement_text"]


def test_credentials_are_never_included_in_argv(monkeypatch):
    client = _client(monkeypatch)
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.client.subprocess.run", return_value=_completed(0, envelope, "")) as run_mock:
        client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])
    call_args = run_mock.call_args.args[0]
    joined = " ".join(call_args)
    assert "ANTHROPIC_API_KEY" not in joined
    assert "sk-" not in joined


# ---------------------------------------------------------------------------
# Output handling — stderr never merged into a successful result
# ---------------------------------------------------------------------------

def test_stderr_present_alongside_success_is_ignored_not_merged(monkeypatch):
    client = _client(monkeypatch)
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.client.subprocess.run", return_value=_completed(0, envelope, "some harmless diagnostic noise")):
        candidates = client.propose_testcases(SAMPLE_CONTEXT, ["POSITIVE"])
    assert candidates == [VALID_CANDIDATE]  # stderr content never leaks into the parsed result
