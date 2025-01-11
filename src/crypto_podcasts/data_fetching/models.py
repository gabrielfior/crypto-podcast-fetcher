import typing as t

from pydantic import BaseModel, computed_field

class Transcript(BaseModel):
    text: str

class PodcastEpisode(BaseModel):
    uuid: str
    #datePublished: int
    #name: str
    #audioUrl: str
    #videoUrl: str | None
    #duration: int | None
    transcript: str | None = None
    #prediction_id: str | None = None
    #prediction_status: str | None = None

    @computed_field
    @property
    def id(self) -> str:
        return self.uuid

    @staticmethod
    def from_json_response(data: dict[t.Any, t.Any]) -> "PodcastEpisode":
        return PodcastEpisode(**data)
