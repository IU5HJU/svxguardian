"""
Public dashboard integration tests.
"""

from src.web.app import (
    app,
    guardian,
)


def test_public_dashboard_is_available(
    monkeypatch,
) -> None:
    """
    /dashboard_pubblica must render successfully without
    changing the Guardian monitoring architecture.
    """

    def fake_guardian_run() -> None:
        guardian.state.reflector_status = "CONNECTED"
        guardian.state.reflector_tg = 2225
        guardian.state.reflector_encrypted = True

        guardian.state.reflector_connected_nodes = [
            "IR5UV",
        ]

        guardian.state.reflector_connection_count = 1

        guardian.state.reflector_connected_clients = [
            "IU5TEST",
        ]

        guardian.state.reflector_transmitting = True
        guardian.state.reflector_transmitting_station = (
            "IU5TEST"
        )

        guardian.state.echolink_transmitting = False
        guardian.state.echolink_transmitting_station = ""

    monkeypatch.setattr(
        guardian,
        "run",
        fake_guardian_run,
    )

    with app.test_client() as client:
        response = client.get(
            "/dashboard_pubblica?lang=it"
        )

    assert response.status_code == 200

    page = response.get_data(
        as_text=True
    )

    assert "Dashboard pubblica" in page
    assert "IR5UV" in page
    assert "IU5TEST" in page
    assert "2225" in page
    assert "dashboard_pubblica.css" in page


def test_existing_reflector_page_still_available(
    monkeypatch,
) -> None:
    """
    Adding the public dashboard must not replace or break
    the existing /reflector page.
    """

    monkeypatch.setattr(
        guardian,
        "run",
        lambda: None,
    )

    with app.test_client() as client:
        response = client.get(
            "/reflector?lang=it"
        )

    assert response.status_code == 200


def test_public_dashboard_prefers_echolink_station_over_reflector_node(
    monkeypatch,
) -> None:
    """
    When EchoLink audio is carried into the reflector by the local
    SvxLink node, the public dashboard must show the EchoLink station
    as the active talker and identify EchoLink as the source.
    """

    def fake_guardian_run() -> None:
        guardian.state.reflector_status = "CONNECTED"
        guardian.state.reflector_tg = 2225

        guardian.state.reflector_transmitting = True
        guardian.state.reflector_transmitting_station = (
            "IR5UV"
        )

        guardian.state.echolink_transmitting = True
        guardian.state.echolink_transmitting_station = (
            "IU5HJU"
        )

        guardian.state.reflector_connected_nodes = [
            "IR5UV",
            "IZ5FSN",
        ]

        guardian.state.reflector_connection_count = 2

    monkeypatch.setattr(
        guardian,
        "run",
        fake_guardian_run,
    )

    with app.test_client() as client:
        response = client.get(
            "/dashboard_pubblica?lang=it"
        )

    assert response.status_code == 200

    page = response.get_data(
        as_text=True
    )

    assert "IU5HJU" in page
    assert "EchoLink" in page
