from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectorDefinition:
    id: str
    display_name: str
    status: str
    description: str
    capabilities: tuple[str, ...]
    supported_record_types: tuple[str, ...]
    requires_authentication: bool
    supports_file_upload: bool
    launch_stage: str


CONNECTOR_REGISTRY: tuple[ConnectorDefinition, ...] = (
    ConnectorDefinition(
        id="manual",
        display_name="Manual Import",
        status="available",
        description="Paste course history or upload transcript-style files directly into the advisor.",
        capabilities=("completed_courses", "planned_courses", "remaining_courses"),
        supported_record_types=("transcript_text", "degree_audit", "schedule"),
        requires_authentication=False,
        supports_file_upload=True,
        launch_stage="available_now",
    ),
    ConnectorDefinition(
        id="canvas",
        display_name="Canvas",
        status="upload_available",
        description="Use Canvas-style exports today, with authenticated sync planned for future current-course context.",
        capabilities=("current_courses", "assignment_load", "schedule_context"),
        supported_record_types=("canvas_export", "schedule", "current_courses"),
        requires_authentication=False,
        supports_file_upload=True,
        launch_stage="upload_today_sync_later",
    ),
    ConnectorDefinition(
        id="websis",
        display_name="WebSIS",
        status="upload_available",
        description="Use WebSIS-style exports today, with direct sync planned for official degree and transcript data.",
        capabilities=("completed_courses", "official_major", "degree_audit"),
        supported_record_types=("websis_export", "degree_audit", "completed_courses"),
        requires_authentication=False,
        supports_file_upload=True,
        launch_stage="upload_today_sync_later",
    ),
)


def list_connector_definitions() -> tuple[ConnectorDefinition, ...]:
    return CONNECTOR_REGISTRY


def get_connector_definition(connector_id: str) -> ConnectorDefinition | None:
    normalized = (connector_id or "").strip().lower()
    return next((item for item in CONNECTOR_REGISTRY if item.id == normalized), None)
