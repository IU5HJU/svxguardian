from src.modules.configreader import ConfigReader


def test_configreader_reads_node_info_file_from_reflector(tmp_path):
    config_file = tmp_path / "svxlink.conf"

    config_file.write_text(
        """
[GLOBAL]
LOGICS=SimplexLogic,ReflectorLogic

[SimplexLogic]
TYPE=Simplex
RX=Rx1
TX=Tx1
CALLSIGN=IR5UV

[ReflectorLogic]
TYPE=Reflector
HOSTS=127.0.0.1
HOST_PORT=5300
DEFAULT_TG=2225
CALLSIGN=IR5UV
NODE_INFO_FILE=/custom/etc/svxlink/node_info.json

[Rx1]
TYPE=Dummy

[Tx1]
TYPE=Dummy
""".strip(),
        encoding="utf-8",
    )

    reader = ConfigReader(config_file)
    node = reader.load()

    assert (
        node.node_info_file
        == "/custom/etc/svxlink/node_info.json"
    )
