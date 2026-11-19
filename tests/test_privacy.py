"""The privacy promise, turned into tests that can fail.

``test_probe_detects_a_simulated_leak`` is the positive control. Without it a
broken hook passes every other test here silently, and the suite becomes a
certificate for something nobody verified.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from memori.oral.net import LocalOnlyViolation, assert_loopback_host, is_loopback_address

PROBE = Path(__file__).resolve().parent / "privacy_probe.py"


def _run_probe(mode: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.lower().endswith("_proxy")}
    env["OLLAMA_HOST"] = "http://127.0.0.1:11434"
    env["NO_PROXY"] = "*"
    return subprocess.run(
        [sys.executable, str(PROBE), mode],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )


def test_probe_detects_a_simulated_leak():
    proc = _run_probe("leak")
    assert proc.returncode == 3, f"expected a caught leak, got {proc.returncode}\n{proc.stdout}{proc.stderr}"
    assert json.loads(proc.stdout)["violations"]


def test_storage_path_makes_no_network_calls():
    proc = _run_probe("db")
    assert proc.returncode == 0, f"{proc.stdout}{proc.stderr}"


def test_ollama_client_stays_on_loopback():
    proc = _run_probe("ollama")
    assert proc.returncode == 0, f"{proc.stdout}{proc.stderr}"


def test_refuses_a_public_bind():
    for host in ("0.0.0.0", "192.168.1.10", "::", "example.com"):
        with pytest.raises(LocalOnlyViolation):
            assert_loopback_host(host)


def test_accepts_a_loopback_bind():
    for host in ("127.0.0.1", "::1", "localhost"):
        assert assert_loopback_host(host) == host


def test_address_judgement():
    assert is_loopback_address(("127.0.0.1", 11434))
    assert is_loopback_address(("::1", 8000))
    assert is_loopback_address("/tmp/socket.sock")
    assert not is_loopback_address(("example.com", 443))
    assert not is_loopback_address(("8.8.8.8", 53))
