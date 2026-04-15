def test_connector_endpoints_return_expected_registry(client, auth_headers):
    response = client.get("/integrations/connectors", headers=auth_headers)
    assert response.status_code == 200

    payload = response.json()
    connector_ids = {connector["id"] for connector in payload}
    assert {"manual", "canvas", "websis"}.issubset(connector_ids)

    canvas = next(connector for connector in payload if connector["id"] == "canvas")
    assert canvas["status"] == "upload_available"
    assert "current_courses" in canvas["capabilities"]
    assert canvas["supports_file_upload"] is True


def test_connector_detail_endpoint_returns_metadata(client, auth_headers):
    response = client.get("/integrations/connectors/websis", headers=auth_headers)
    assert response.status_code == 200

    payload = response.json()
    assert payload["id"] == "websis"
    assert payload["display_name"] == "WebSIS"
    assert payload["requires_authentication"] is False
    assert "degree_audit" in payload["supported_record_types"]


def test_unknown_connector_returns_404(client, auth_headers):
    response = client.get("/integrations/connectors/unknown", headers=auth_headers)
    assert response.status_code == 404
