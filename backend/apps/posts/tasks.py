from celery import shared_task


@shared_task
def expire_posts():
    """
    Hook for future work (e.g. push notifications when a post expires).
    Feed filtering is done at query time via expires_at__gt=now,
    so no DB writes are needed here for Phase 0.
    """
    pass
