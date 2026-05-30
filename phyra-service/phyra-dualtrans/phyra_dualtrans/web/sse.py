"""SSE bridge: async event generator → text/event-stream with heartbeat.

The heartbeat must NOT cancel the underlying event generator. A naive
``asyncio.wait_for(it.__anext__(), timeout=HEARTBEAT_SEC)`` cancels the
in-flight ``__anext__()`` on every timeout — and since that coroutine is
suspended inside the subscriber generator's ``await queue.get()``, the
``CancelledError`` unwinds the generator (running its ``finally``) and
closes it. The next ``__anext__()`` then raises ``StopAsyncIteration`` and
the SSE stream ends prematurely — i.e. the live progress bar dies on the
first >15 s quiet gap, which every real (LLM-paced) translation has.

So we keep a single in-flight ``__anext__()`` task alive ACROSS heartbeat
timeouts: on timeout we emit a ping and keep awaiting the SAME task; only a
real client disconnect cancels it.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
from collections.abc import AsyncIterator

from fastapi.responses import StreamingResponse

HEARTBEAT_SEC = 15


def sse_response(events: AsyncIterator[dict]) -> StreamingResponse:
    async def stream():
        it = events.__aiter__()
        nxt: asyncio.Task | None = None
        try:
            while True:
                if nxt is None:
                    nxt = asyncio.ensure_future(it.__anext__())
                done, _ = await asyncio.wait({nxt}, timeout=HEARTBEAT_SEC)
                if not done:
                    # Still pending — emit a heartbeat and keep the SAME
                    # task; never cancel it (that would kill the generator).
                    yield ": ping\n\n"
                    continue
                try:
                    ev = nxt.result()
                except StopAsyncIteration:
                    break
                finally:
                    nxt = None
                payload = json.dumps(ev, ensure_ascii=False)
                yield f"event: {ev.get('type', 'message')}\ndata: {payload}\n\n"
        finally:
            if nxt is not None:
                nxt.cancel()
                with contextlib.suppress(BaseException):
                    await nxt
            with contextlib.suppress(BaseException):
                await it.aclose()

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
