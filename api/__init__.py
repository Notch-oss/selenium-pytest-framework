"""HTTP API client layer for the AutomationExercise public REST API.

Mirrors the page-object philosophy used in `pages/`: `BaseApiClient` owns the
HTTP mechanics (session, retries, timeouts, response parsing), while
`AutomationExerciseApiClient` exposes one intent-revealing method per documented
endpoint. Tests speak to the client, never to `requests` directly.
"""
from api.automation_exercise_api import AutomationExerciseApiClient
from api.base_client import ApiResponse, BaseApiClient

__all__ = ["AutomationExerciseApiClient", "ApiResponse", "BaseApiClient"]
