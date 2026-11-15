import json
import httpx
from sqlalchemy.exc import IntegrityError
from .models import Notification
from .security import sign_webhook


def create_notification(db, post, agent):
    notification = Notification(post_id=post.id, agent_id=agent.id)
    db.add(notification)
    try:
        db.commit()
        db.refresh(notification)
        return notification
    except IntegrityError:
        db.rollback()
        return None


async def deliver_webhook(db, notification, agent, post):
    if not agent.webhook_url:
        notification.status = "recorded"
        db.commit()
        return

    payload = {
        "notification_id": notification.id,
        "post_id": post.id,
        "title": post.title,
        "content": post.content
    }
    body = json.dumps(payload).encode("utf-8")
    notification.attempts += 1

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                str(agent.webhook_url),
                content=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": sign_webhook(
                        "development-webhook-secret", body
                    )
                }
            )
            response.raise_for_status()
        notification.status = "delivered"
        notification.last_error = None
    except Exception as exc:
        notification.status = "failed"
        notification.last_error = str(exc)[:500]

    db.commit()
