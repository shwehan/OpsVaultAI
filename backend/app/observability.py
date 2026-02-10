from __future__ import annotations

import json
import time
import uuid
from typing import Callable

from fastapi import Request, Response


def _get_or_create_request_id(request: Request) -> str:
    rid = request.headers.get("x-request-id")
    if rid:
        return rid
    return uuid.uuid4().hex


async def request_id_and_timing_middleware(request: Request, call_next: Callable):
    """
    Adds:
      - X-Request-ID response header
      - structured JSON log line including method/path/status/latency
    """
    request_id = _get_or_create_request_id(request)
    start = time.perf_counter()

    try:
        response: Response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        latency_ms = (time.perf_counter() - start) * 1000.0

        log = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": getattr(locals().get("response", None), "status_code", None),
            "latency_ms": round(latency_ms, 2),
        }
        print(json.dumps(log, ensure_ascii=False))

        # Ensure response exists before setting header (in case of exception)
        if "response" in locals() and locals()["response"] is not None:
            locals()["response"].headers["X-Request-ID"] = request_id