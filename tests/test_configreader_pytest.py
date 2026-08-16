from src.modules.configreader import ConfigReader


def test_configreader_reads_custom_svxlink_config(tmp_path):
    config_file = tmp_path / "svxlink.conf"

    config_file.write_text(
        """
[GLOBAL]
LOGICS=SimplexLogic,ReflectorLogic

[SimplexLogic]
TYPE=Simplex
RX=Rx1
TX=Tx1
MODULES=ModuleHelp,ModuleParrot,ModuleEchoLink
CALLSIGN=IR5UV

[ReflectorLogic]
TYPE=Reflector
HOSTS=127.0.0.1
HOST_PORT=5300
DEFAULT_TG=2225
CALLSIGN=IR5UV
""".strip(),
        encoding="utf-8",
    )

    reader = ConfigReader(config_file)
    node = reader.load()

    assert node.config_file == str(config_file)

    assert node.logics == [
        "SimplexLogic",
        "ReflectorLogic",
    ]

    assert node.callsign == "IR5UV"

    assert node.modules == [
        "ModuleHelp",
        "ModuleParrot",
        "ModuleEchoLink",
    ]

    assert node.reflector_configured is True
    assert node.reflector_logic_name == "ReflectorLogic"
    assert node.reflector_hosts == ["127.0.0.1"]
    assert node.reflector_port == 5300
    assert node.reflector_default_tg == 2225
    assert node.reflector_mode == "local"

    assert (
        node.reflector
        == "127.0.0.1:5300 - TG 2225"
    )
