from typing import List

from fastapi import APIRouter, Depends, HTTPException

from . import models, schemas
from .auth import get_current_user
from .integrations_registry import get_connector_definition, list_connector_definitions

router = APIRouter(prefix="/integrations", tags=["integrations"])


def _serialize_connector(connector) -> schemas.ConnectorDetail:
    return schemas.ConnectorDetail(
        id=connector.id,
        display_name=connector.display_name,
        status=connector.status,
        description=connector.description,
        capabilities=list(connector.capabilities),
        supported_record_types=list(connector.supported_record_types),
        supports_file_upload=connector.supports_file_upload,
        requires_authentication=connector.requires_authentication,
        launch_stage=connector.launch_stage,
    )


@router.get("/connectors", response_model=List[schemas.ConnectorSummary])
def list_connectors(
    current_user: models.User = Depends(get_current_user),
):
    return [
        schemas.ConnectorSummary(
            id=connector.id,
            display_name=connector.display_name,
            status=connector.status,
            description=connector.description,
            capabilities=list(connector.capabilities),
            supports_file_upload=connector.supports_file_upload,
            requires_authentication=connector.requires_authentication,
            launch_stage=connector.launch_stage,
        )
        for connector in list_connector_definitions()
    ]


@router.get("/connectors/{connector_id}", response_model=schemas.ConnectorDetail)
def get_connector(
    connector_id: str,
    current_user: models.User = Depends(get_current_user),
):
    connector = get_connector_definition(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return _serialize_connector(connector)
