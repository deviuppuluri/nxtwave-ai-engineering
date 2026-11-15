from functools import lru_cache
import numpy as np

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def relevance_scores(post_text: str, agents: list) -> tuple[list[float], str]:
    """
    Compare a post with agent interest descriptions using local embeddings.
    Industry and active-agent exclusions are applied before this function.
    """
    if not agents:
        return [], "no_candidates"

    try:
        model = get_model()
        texts = [post_text] + [a.interest_description for a in agents]
        vectors = model.encode(texts, normalize_embeddings=True)
        scores = np.dot(vectors[1:], vectors[0])
        return [float(x) for x in scores], "sentence-transformers"
    except Exception:
        # Safe fallback if the model is not installed or cannot be downloaded.
        # This is explicitly not semantic matching; install the model for it.
        return [0.0 for _ in agents], "embedding_unavailable"


def route_agents(post, agents, threshold: float = 0.45):
    post_text = f"{post.title}. {post.content}"
    candidates = [
        agent for agent in agents
        if agent.active and agent.id != post.author_id
    ]

    scores, mode = relevance_scores(post_text, candidates)
    selected = []
    logs = []

    for agent, score in zip(candidates, scores):
        match = score >= threshold
        reason = (
            "semantic similarity above threshold"
            if match else "semantic similarity below threshold"
        )
        logs.append({
            "agent_id": agent.id,
            "score": round(score * 100),
            "selected": match,
            "reason": f"{reason}; mode={mode}"
        })
        if match:
            selected.append(agent)

    return selected, logs, mode
