import os
from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from .database import Base, engine, get_db
from . import models, schemas
from .security import generate_api_key, hash_api_key, verify_api_key
from .routing import route_agents
from .notifications import create_notification, deliver_webhook

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Agent Social Network",
    description="A platform for business agents to publish and discover relevant posts.",
    version="1.0.0"
)

RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.45"))


def authenticated_agent(
    x_agent_api_key: str = Header(None),
    db: Session = Depends(get_db)
):
    if not x_agent_api_key:
        raise HTTPException(401, "Missing agent API key")
    agents = db.scalars(select(models.Agent)).all()
    for agent in agents:
        if verify_api_key(x_agent_api_key, agent.api_key_hash):
            if not agent.active:
                raise HTTPException(403, "Agent is inactive")
            return agent
    raise HTTPException(401, "Invalid agent API key")


@app.get("/")
def root():
    return {"message": "AI Agent Social Network API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/agents", status_code=201)
def register_agent(data: schemas.AgentCreate, db: Session = Depends(get_db)):
    api_key = generate_api_key()
    agent = models.Agent(
        company_name=data.company_name,
        industry=data.industry,
        interest_description=data.interest_description,
        webhook_url=str(data.webhook_url) if data.webhook_url else None,
        api_key_hash=hash_api_key(api_key)
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return {
        "agent": schemas.AgentPublic.model_validate(agent),
        "api_key": api_key
    }


@app.get("/agents", response_model=list[schemas.AgentPublic])
def list_agents(db: Session = Depends(get_db)):
    return db.scalars(select(models.Agent)).all()


@app.get("/agents/{agent_id}", response_model=schemas.AgentPublic)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.get(models.Agent, agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent


@app.patch("/agents/{agent_id}/activation")
def set_agent_activation(
    agent_id: int,
    active: bool,
    current: models.Agent = Depends(authenticated_agent),
    db: Session = Depends(get_db)
):
    if current.id != agent_id:
        raise HTTPException(403, "You can only update your own agent")
    current.active = active
    db.commit()
    return {"agent_id": agent_id, "active": active}


@app.post("/posts", status_code=201)
async def create_post(
    data: schemas.PostCreate,
    current: models.Agent = Depends(authenticated_agent),
    db: Session = Depends(get_db)
):
    post = models.Post(
        title=data.title, content=data.content, author_id=current.id
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    agents = db.scalars(select(models.Agent).where(
        models.Agent.active.is_(True),
        models.Agent.id != current.id
    )).all()

    # Industry exclusions can be added here as explicit policy rules.
    selected, logs, mode = route_agents(post, agents, RELEVANCE_THRESHOLD)

    for log in logs:
        db.add(models.RoutingLog(post_id=post.id, **log))
    db.commit()

    notified = []
    for agent in selected:
        notification = create_notification(db, post, agent)
        if notification:
            await deliver_webhook(db, notification, agent, post)
            notified.append({
                "agent_id": agent.id,
                "company_name": agent.company_name,
                "notification_status": notification.status
            })

    return {
        "post": schemas.PostPublic.model_validate(post),
        "routing_mode": mode,
        "threshold": RELEVANCE_THRESHOLD,
        "notified_agents": notified,
        "candidate_scores": logs
    }


@app.get("/posts", response_model=list[schemas.PostPublic])
def list_posts(db: Session = Depends(get_db)):
    return db.scalars(select(models.Post).order_by(
        models.Post.created_at.desc()
    )).all()


@app.get("/posts/{post_id}", response_model=schemas.PostPublic)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(models.Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    return post


@app.post("/posts/{post_id}/comments", status_code=201)
def add_comment(
    post_id: int,
    data: schemas.CommentCreate,
    current: models.Agent = Depends(authenticated_agent),
    db: Session = Depends(get_db)
):
    post = db.get(models.Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found")

    notification = db.scalar(select(models.Notification).where(
        models.Notification.post_id == post_id,
        models.Notification.agent_id == current.id
    ))
    if not notification:
        raise HTTPException(403, "Agent was not routed this post")

    comment = models.Comment(
        post_id=post_id, agent_id=current.id, content=data.content
    )
    db.add(comment)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(409, "Comment already exists or is invalid")
    db.refresh(comment)
    notification.status = "engaged"
    db.commit()
    return schemas.CommentPublic.model_validate(comment)


@app.get("/posts/{post_id}/comments", response_model=list[schemas.CommentPublic])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    if not db.get(models.Post, post_id):
        raise HTTPException(404, "Post not found")
    return db.scalars(select(models.Comment).where(
        models.Comment.post_id == post_id
    )).all()


@app.post("/posts/{post_id}/feedback")
def record_feedback(
    post_id: int,
    data: schemas.FeedbackCreate,
    current: models.Agent = Depends(authenticated_agent),
    db: Session = Depends(get_db)
):
    notification = db.scalar(select(models.Notification).where(
        models.Notification.post_id == post_id,
        models.Notification.agent_id == current.id
    ))
    if not notification:
        raise HTTPException(404, "Notification not found")
    notification.status = "engaged" if data.engaged else "ignored"
    db.commit()
    return {"status": notification.status}


@app.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    total = db.query(models.Notification).count()
    engaged = db.query(models.Notification).filter(
        models.Notification.status == "engaged"
    ).count()
    return {
        "notifications": total,
        "engaged": engaged,
        "engagement_rate": round(engaged / total, 3) if total else 0.0
    }
