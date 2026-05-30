"""Regression: the SSE heartbeat must not tear down the event generator.

Bug (pre-fix): sse_response used asyncio.wait_for(it.__anext__(), timeout=
HEARTBEAT_SEC); on every timeout it cancelled the in-flight __anext__(),
which (being suspended inside the subscriber generator's `await
queue.get()`) unwound that generator via its `finally` and closed it. The
next __anext__() raised StopAsyncIteration and the stream ended — so the
live progress bar froze on the first >15 s quiet gap, which every real
LLM-paced translation has.
"""

from __future__ import annotations

import asyncio

from phyra_dualtrans.web import sse


def test_heartbeat_does_not_kill_stream(monkeypatch):
    monkeypatch.setattr(sse, "HEARTBEAT_SEC", 0.05)
    closed = {"v": False}

    async def source():
        # Mirrors JobManager.subscribe(): a try/finally around a wait that
        # is longer than several heartbeats (emulates a slow LLM call while
        # the subscriber sits in `await queue.get()`).
        try:
            yield {"type": "progress", "overall_pct": 10}
            await asyncio.sleep(0.25)
            yield {"type": "done", "outputs": {}}
        finally:
            closed["v"] = True

    async def drive():
        resp = sse.sse_response(source())
        return [c async for c in resp.body_iterator]

    text = "".join(asyncio.run(drive()))

    assert "event: progress" in text
    assert ": ping\n\n" in text                  # heartbeat fired
    assert text.count(": ping\n\n") >= 2         # across the whole quiet gap
    assert "event: done" in text                 # survived it (the regression)
    assert closed["v"] is True                   # source cleanly finalized


def test_client_disconnect_cancels_pending_anext():
    """If the consumer stops early, the in-flight __anext__ is cancelled and
    the source generator is closed (no leaked subscriber)."""
    monkeypatch_done = {"closed": False}

    async def source():
        try:
            yield {"type": "progress"}
            await asyncio.sleep(10)        # would hang if not cancelled
            yield {"type": "done"}
        finally:
            monkeypatch_done["closed"] = True

    async def drive():
        resp = sse.sse_response(source())
        ait = resp.body_iterator.__aiter__()
        first = await ait.__anext__()         # the progress event
        await ait.aclose()                    # consumer goes away mid-stream
        return first

    first = asyncio.run(drive())
    assert "event: progress" in first
    assert monkeypatch_done["closed"] is True
