from contracts.base_artifact import BaseArtifact

artifact = BaseArtifact(
    artifact_type="TestArtifact",
    created_by="Developer"
)

print(artifact)