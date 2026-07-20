from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from contracts.enums import ArtifactStatus


class BaseArtifact(BaseModel):
    """
    Base class for every artifact produced by an agent.
    """

    artifact_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this artifact"
    )

    artifact_type: str = Field(
        description="Type of artifact (DatasetProfile, TransformationPlan, etc.)"
    )

    version: str = Field(
        default="1.0.0",
        description="Artifact version"
    )

    status: ArtifactStatus = Field(
        default=ArtifactStatus.DRAFT,
        description="Current artifact status"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Artifact creation timestamp"
    )

    created_by: str = Field(
        description="Agent responsible for creating the artifact"
    )