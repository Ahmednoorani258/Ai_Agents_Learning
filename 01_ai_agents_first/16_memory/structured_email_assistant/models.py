from pydantic import BaseModel, Field
from typing_extensions import Literal
from prompts import email

class UserInfo(BaseModel):
    username: str

class Email(BaseModel):
    from_: str = Field(alias="from")
    to: str
    subject: str
    body: str


class Router(BaseModel):
    """Analyze the unread email and route it according to its content."""

    reasoning: str = Field(
        description="Step-by-step reasoning behind the classification."
    )
    classification: Literal["ignore", "respond", "notify"] = Field(
        description="The classification of an email: 'ignore' for irrelevant emails, "
        "'notify' for important information that doesn't need a response, "
        "'respond' for emails that need a reply",
    )
    
email_model = Email(**email)