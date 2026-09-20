"""
N1MOX30 background job abstraction.

The production worker can later be backed by Celery/RQ/Arq
without changing callers.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional
import uuid


@dataclass
class Job:
    id: str
    name: str
    payload: dict
    status: str = "queued"
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class JobQueue:
    def __init__(self):
        self.jobs: dict[str, Job] = {}

    def enqueue(
        self,
        name: str,
        payload: Optional[dict] = None,
    ) -> Job:
        job = Job(
            id=str(uuid.uuid4()),
            name=name,
            payload=payload or {},
        )
        self.jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)


queue = JobQueue()
