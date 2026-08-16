import json

from src.core.nodeinfo import NodeInfo
from src.modules.nodeinforeader import NodeInfoReader


def test_nodeinforeader_enriches_custom_node_info(tmp_path):
    node_info_file = tmp_path / "node_info.json"

    node_info_file.write_text(
        json.dumps(
            {
                "nodeLocation": "Test site",
                "nodeClass": "Test",
                "hidden": False,
                "sysop": "IU5HJU",
                "toneToTalkgroup": {
                    "127.3": 2225,
                },
                "qth": [
                    {
                        "name": "LAB",
                        "pos": {
                            "lat": 43.0,
                            "long": 11.0,
                            "loc": "JN53",
                        },
                        "rx": {
                            "Rx1": {
                                "name": "RX LAB",
                                "freq": 145500000,
                                "sqlType": "GPIOD",
                                "ctcssFreq": [127.3],
                            }
                        },
                        "tx": {
                            "Tx1": {
                                "name": "TX LAB",
                                "freq": 145500000,
                                "pwr": 5,
                                "ctcssFreq": 127.3,
                            }
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    node = NodeInfo(callsign="IR5UV")

    reader = NodeInfoReader(node_info_file)
    node = reader.enrich(node)

    assert node.node_info_file == str(node_info_file)
    assert node.callsign == "IR5UV"
    assert node.node_location == "Test site"
    assert node.node_class == "Test"
    assert node.hidden is False
    assert node.sysop == "IU5HJU"
    assert node.qth == "LAB"
    assert node.locator == "JN53"
    assert node.latitude == 43.0
    assert node.longitude == 11.0
    assert node.rx_name == "RX LAB"
    assert node.rx_frequency == "145500000"
    assert node.rx_sql_type == "GPIOD"
    assert node.rx_ctcss_frequencies == ["127.3"]
    assert node.tx_name == "TX LAB"
    assert node.tx_frequency == "145500000"
    assert node.tx_power == "5"
    assert node.tx_ctcss_frequency == "127.3"
    assert node.tone_to_talkgroup == {
        "127.3": 2225,
    }
