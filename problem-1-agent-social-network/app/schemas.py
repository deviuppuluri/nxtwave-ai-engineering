from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class AgentCreate(BaseModel):
    company_name: str = Field(min_length=2, max_length=120)
    industry: str = Field(min_length=2, max_length=100)
    interest_description: str = Field(min_length=10, max_length=2000)
    webhook_url: HttpUrl | None = None


class AgentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    industry: str
    interest_description: str
    active: bool


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=5, max_length=5000)


class PostPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    author_id: int


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    agent_id: int
    content: str


class FeedbackCreate(BaseModel):
    engaged: bool
