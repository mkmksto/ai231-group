from pydantic import BaseModel


class FeedbackInput(BaseModel):
    image_id: str
    label: str
