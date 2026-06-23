from __future__ import annotations

from datetime import datetime, timedelta
from threading import Event, Thread

from app.config import settings
from app.services.paper_service import collect_papers


class DailyScheduler:
    def __init__(self) -> None:
        self.stop_event = Event()
        self.thread: Thread | None = None

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.thread = Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()

    def _run_loop(self) -> None:
        while not self.stop_event.is_set():
            wait_seconds = self._seconds_until_next_run()
            if self.stop_event.wait(timeout=wait_seconds):
                return
            for domain in settings.default_domains:
                try:
                    collect_papers(domain, None, None, settings.collect_max_results)
                except Exception:
                    continue

    def _seconds_until_next_run(self) -> float:
        now = datetime.now()
        next_run = now.replace(
            hour=settings.scheduler_hour,
            minute=settings.scheduler_minute,
            second=0,
            microsecond=0,
        )
        if next_run <= now:
            next_run = next_run + timedelta(days=1)
        return max((next_run - now).total_seconds(), 1.0)


scheduler = DailyScheduler()


def start_scheduler() -> None:
    if settings.scheduler_enabled:
        scheduler.start()


def stop_scheduler() -> None:
    scheduler.stop()
