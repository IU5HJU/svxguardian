from src.core.state import NodeState
from src.modules.reflector import ReflectorMonitor
from src.services.reflector_events import ReflectorEventTracker


def append_line(log_file, line: str) -> None:
    with log_file.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(line + "\n")


def test_tracker_ignores_historical_events(tmp_path):
    log_file = tmp_path / "svxlink.log"

    log_file.write_text(
        (
            "Sat Aug 22 07:28:06 2026: "
            "ReflectorLogic: Node joined: OLDCLIENT\n"
        ),
        encoding="utf-8",
    )

    tracker = ReflectorEventTracker(
        log_file=log_file
    )

    tracker.sync()

    assert tracker.connected_clients == []


def test_tracker_follows_latry_session(tmp_path):
    log_file = tmp_path / "svxlink.log"
    log_file.write_text("", encoding="utf-8")

    tracker = ReflectorEventTracker(
        log_file=log_file
    )

    tracker.sync()

    append_line(
        log_file,
        (
            "Sat Aug 22 07:28:06 2026: "
            "ReflectorLogic: Node joined: IU5HJU"
        ),
    )

    tracker.sync()

    assert tracker.connected_clients == ["IU5HJU"]
    assert tracker.transmitting is False
    assert tracker.transmitting_station == ""

    append_line(
        log_file,
        (
            "Sat Aug 22 07:28:12 2026: "
            "ReflectorLogic: Talker start on TG #2225: IU5HJU"
        ),
    )

    tracker.sync()

    assert tracker.connected_clients == ["IU5HJU"]
    assert tracker.transmitting is True
    assert tracker.transmitting_station == "IU5HJU"
    assert tracker.transmitting_tg == 2225

    append_line(
        log_file,
        (
            "Sat Aug 22 07:28:17 2026: "
            "ReflectorLogic: Talker stop on TG #2225: IU5HJU"
        ),
    )

    tracker.sync()

    assert tracker.connected_clients == ["IU5HJU"]
    assert tracker.transmitting is False
    assert tracker.transmitting_station == ""
    assert tracker.transmitting_tg is None

    append_line(
        log_file,
        (
            "Sat Aug 22 07:28:22 2026: "
            "ReflectorLogic: Node left: IU5HJU"
        ),
    )

    tracker.sync()

    assert tracker.connected_clients == []


def test_tracker_does_not_duplicate_joined_client(tmp_path):
    log_file = tmp_path / "svxlink.log"
    log_file.write_text("", encoding="utf-8")

    tracker = ReflectorEventTracker(
        log_file=log_file
    )

    tracker.sync()

    append_line(
        log_file,
        "ReflectorLogic: Node joined: IU5HJU",
    )

    append_line(
        log_file,
        "ReflectorLogic: Node joined: IU5HJU",
    )

    tracker.sync()

    assert tracker.connected_clients == ["IU5HJU"]


def test_node_left_clears_active_talker(tmp_path):
    log_file = tmp_path / "svxlink.log"
    log_file.write_text("", encoding="utf-8")

    tracker = ReflectorEventTracker(
        log_file=log_file
    )

    tracker.sync()

    append_line(
        log_file,
        "ReflectorLogic: Node joined: IU5HJU",
    )

    append_line(
        log_file,
        (
            "ReflectorLogic: "
            "Talker start on TG #2225: IU5HJU"
        ),
    )

    tracker.sync()

    assert tracker.transmitting is True

    append_line(
        log_file,
        "ReflectorLogic: Node left: IU5HJU",
    )

    tracker.sync()

    assert tracker.connected_clients == []
    assert tracker.transmitting is False
    assert tracker.transmitting_station == ""
    assert tracker.transmitting_tg is None


def test_reflector_monitor_exports_live_client_state(tmp_path):
    log_file = tmp_path / "svxlink.log"
    log_file.write_text("", encoding="utf-8")

    monitor = ReflectorMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    append_line(
        log_file,
        (
            "Sat Aug 22 07:28:06 2026: "
            "ReflectorLogic: Node joined: IU5HJU"
        ),
    )

    monitor.check(state)

    assert state.reflector_connected_clients == [
        "IU5HJU"
    ]

    assert state.reflector_connected_nodes == []


def test_reflector_monitor_exports_live_talker_state(tmp_path):
    log_file = tmp_path / "svxlink.log"
    log_file.write_text("", encoding="utf-8")

    monitor = ReflectorMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    append_line(
        log_file,
        "ReflectorLogic: Node joined: IU5HJU",
    )

    append_line(
        log_file,
        (
            "ReflectorLogic: "
            "Talker start on TG #2225: IU5HJU"
        ),
    )

    monitor.check(state)

    assert state.reflector_connected_clients == [
        "IU5HJU"
    ]

    assert state.reflector_transmitting is True

    assert (
        state.reflector_transmitting_station
        == "IU5HJU"
    )

    append_line(
        log_file,
        (
            "ReflectorLogic: "
            "Talker stop on TG #2225: IU5HJU"
        ),
    )

    monitor.check(state)

    assert state.reflector_connected_clients == [
        "IU5HJU"
    ]

    assert state.reflector_transmitting is False
    assert state.reflector_transmitting_station == ""

def test_reflector_monitor_detects_modern_connected_log(tmp_path):
    log_file = tmp_path / "svxlink.log"

    log_file.write_text(
        (
            "Sun 23 Aug 2026 17:54:06 CEST: "
            "ReflectorLogic: Connecting to service\n"
            "Sun 23 Aug 2026 17:54:06 CEST: "
            "NOTICE[ReflectorLogic]: "
            "Connected to 192.168.1.36:5300 (primary)\n"
        ),
        encoding="utf-8",
    )

    monitor = ReflectorMonitor(
        log_file=log_file
    )

    state = NodeState()

    monitor.check(state)

    assert state.reflector_status.value == "CONNECTED"
    assert state.reflector_host == "192.168.1.36"
    assert state.reflector_port == 5300
