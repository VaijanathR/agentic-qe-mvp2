"""
CP-MVP2-04 — Claude test-data provider adapter tests.

Mirrors tests/test_cp_mvp2_03_claude_provider.py exactly: every test
mocks `llm.test_data_client.subprocess.run` and
`llm.test_data_client.shutil.which` — no real `claude` process, no
subscription usage, no network call anywhere in this file.
"""
from __future__ import annotations

import json
import subprocess as real_subprocess
from unittest.mock import patch

import pytest

from llm.client import ClaudeProviderError
from llm.test_data_client import ClaudeTestDataClient

VALID_CANDIDATE = {
    "data_category": "POSITIVE",
    "purpose": "valid registration data",
    "validity": "VALID",
    "fields": [{"field_name": "first_name", "field_value": "Synthetic"}],
}

SAMPLE_CONTEXT = {
    "testcase_id": "TC-REQ-REG-01-01",
    "requirement_id": "REQ-REG-01",
    "requested_categories": ["POSITIVE"],
    "field_specs": [{"field_name": "first_name", "value_type": "STRING", "mandatory": True}],
}


def _completed(returncode=0, stdout="", stderr=""):
    return real_subprocess.CompletedProcess(args=["claude"], returncode=returncode, stdout=stdout, stderr=stderr)


def _envelope(result_text, is_error=False):
    return json.dumps({"type": "result", "is_error": is_error, "result": result_text})


def _client(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("llm.test_data_client.shutil.which", return_value="/usr/bin/claude"):
        return ClaudeTestDataClient()


# ---------------------------------------------------------------------------
# Provider availability / billing safety
# ---------------------------------------------------------------------------

def test_missing_executable_raises_provider_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("llm.test_data_client.shutil.which", return_value=None):
        with pytest.raises(ClaudeProviderError, match="not found on PATH"):
            ClaudeTestDataClient()


def test_anthropic_api_key_present_raises_before_touching_cli(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-totally-fake")
    with patch("llm.test_data_client.shutil.which") as which_mock:
        with pytest.raises(ClaudeProviderError, match="ANTHROPIC_API_KEY"):
            ClaudeTestDataClient()
        which_mock.assert_not_called()


def test_anthropic_api_key_value_never_appears_in_error_message(monkeypatch):
    secret = "sk-ant-fake-secret-xyz"
    monkeypatch.setenv("ANTHROPIC_API_KEY", secret)
    with pytest.raises(ClaudeProviderError) as excinfo:
        ClaudeTestDataClient()
    assert secret not in str(excinfo.value)


# ---------------------------------------------------------------------------
# Successful execution / subprocess safety
# ---------------------------------------------------------------------------

def test_successful_invocation_parses_candidates(monkeypatch):
    client = _client(monkeypatch)
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.test_data_client.subprocess.run", return_value=_completed(0, envelope, "")) as run_mock:
        candidates = client.propose_field_values(SAMPLE_CONTEXT)
    assert candidates == [VALID_CANDIDATE]
    run_mock.assert_called_once()


def test_argv_is_a_list_not_shell_and_uses_restricted_mode(monkeypatch):
    client = _client(monkeypatch)
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.test_data_client.subprocess.run", return_value=_completed(0, envelope, "")) as run_mock:
        client.propose_field_values(SAMPLE_CONTEXT)
    call_args = run_mock.call_args.args[0]
    call_kwargs = run_mock.call_args.kwargs
    assert isinstance(call_args, list)
    assert call_kwargs.get("shell") is False
    assert "--restricted" in call_args


def test_explicit_timeout_is_always_passed(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("llm.test_data_client.shutil.which", return_value="/usr/bin/claude"):
        client = ClaudeTestDataClient(timeout_seconds=5.0)
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.test_data_client.subprocess.run", return_value=_completed(0, envelope, "")) as run_mock:
        client.propose_field_values(SAMPLE_CONTEXT)
    assert run_mock.call_args.kwargs.get("timeout") == 5.0


# ---------------------------------------------------------------------------
# Failure handling
# ---------------------------------------------------------------------------

def test_non_zero_exit_code_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    with patch("llm.test_data_client.subprocess.run", return_value=_completed(1, "", "cli error")):
        with pytest.raises(ClaudeProviderError, match="non-zero status"):
            client.propose_field_values(SAMPLE_CONTEXT)


def test_timeout_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    with patch("llm.test_data_client.subprocess.run", side_effect=real_subprocess.TimeoutExpired(cmd="claude", timeout=120)):
        with pytest.raises(ClaudeProviderError, match="timed out"):
            client.propose_field_values(SAMPLE_CONTEXT)


def test_empty_stdout_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    with patch("llm.test_data_client.subprocess.run", return_value=_completed(0, "", "")):
        with pytest.raises(ClaudeProviderError, match="empty stdout"):
            client.propose_field_values(SAMPLE_CONTEXT)


def test_malformed_envelope_json_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    with patch("llm.test_data_client.subprocess.run", return_value=_completed(0, "{not json", "")):
        with pytest.raises(ClaudeProviderError, match="not valid JSON"):
            client.propose_field_values(SAMPLE_CONTEXT)


def test_is_error_true_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    envelope = _envelope("model failure", is_error=True)
    with patch("llm.test_data_client.subprocess.run", return_value=_completed(0, envelope, "")):
        with pytest.raises(ClaudeProviderError, match="is_error=true"):
            client.propose_field_values(SAMPLE_CONTEXT)


def test_result_not_a_list_raises_provider_error(monkeypatch):
    client = _client(monkeypatch)
    envelope = _envelope(json.dumps({"not": "a list"}))
    with patch("llm.test_data_client.subprocess.run", return_value=_completed(0, envelope, "")):
        with pytest.raises(ClaudeProviderError, match="not a list"):
            client.propose_field_values(SAMPLE_CONTEXT)


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

def test_dataset_context_with_shell_metacharacters_is_passed_as_single_safe_argument(monkeypatch):
    client = _client(monkeypatch)
    dangerous_context = dict(SAMPLE_CONTEXT)
    dangerous_context["evidence_note"] = "; rm -rf / #$(whoami)`id`\nNEWLINE 'quote' \"dquote\" ☺"
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.test_data_client.subprocess.run", return_value=_completed(0, envelope, "")) as run_mock:
        client.propose_field_values(dangerous_context)
    call_args = run_mock.call_args.args[0]
    call_kwargs = run_mock.call_args.kwargs
    assert call_kwargs.get("shell") is False
    prompt_arg = call_args[call_args.index("-p") + 1]
    decoded = json.loads(prompt_arg)
    assert decoded["evidence_note"] == dangerous_context["evidence_note"]


def test_credentials_never_included_in_argv(monkeypatch):
    client = _client(monkeypatch)
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.test_data_client.subprocess.run", return_value=_completed(0, envelope, "")) as run_mock:
        client.propose_field_values(SAMPLE_CONTEXT)
    joined = " ".join(run_mock.call_args.args[0])
    assert "ANTHROPIC_API_KEY" not in joined
    assert "sk-" not in joined


# ---------------------------------------------------------------------------
# Output handling
# ---------------------------------------------------------------------------

def test_stderr_present_alongside_success_is_ignored_not_merged(monkeypatch):
    client = _client(monkeypatch)
    envelope = _envelope(json.dumps([VALID_CANDIDATE]))
    with patch("llm.test_data_client.subprocess.run", return_value=_completed(0, envelope, "harmless diagnostic noise")):
        candidates = client.propose_field_values(SAMPLE_CONTEXT)
    assert candidates == [VALID_CANDIDATE]
