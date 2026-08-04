"""
SvxLink node information reader test.
"""

from src.core.nodeinfo import NodeInfo
from src.modules.nodeinforeader import NodeInfoReader


def main() -> None:
    """
    Read and display node_info.json data.
    """

    node = NodeInfo(
        callsign="IR5UV",
    )

    reader = NodeInfoReader()
    node = reader.enrich(node)

    print("=" * 60)
    print("SVX Guardian - Node Information Test")
    print("=" * 60)

    print(f"Node info file : {node.node_info_file}")
    print(f"Callsign       : {node.callsign or 'NOT FOUND'}")
    print(f"Location       : {node.node_location or 'NOT FOUND'}")
    print(f"Class          : {node.node_class or 'NOT FOUND'}")
    print(f"Hidden         : {node.hidden}")
    print(f"Sysop          : {node.sysop or 'NOT FOUND'}")
    print(f"QTH            : {node.qth or 'NOT FOUND'}")
    print(f"Locator        : {node.locator or 'NOT FOUND'}")

    if node.latitude is not None:
        print(f"Latitude       : {node.latitude}")
    else:
        print("Latitude       : NOT FOUND")

    if node.longitude is not None:
        print(f"Longitude      : {node.longitude}")
    else:
        print("Longitude      : NOT FOUND")

    print(f"RX name        : {node.rx_name or 'NOT FOUND'}")
    print(f"RX frequency   : {node.rx_frequency or 'NOT FOUND'}")
    print(f"RX SQL type    : {node.rx_sql_type or 'NOT FOUND'}")

    if node.rx_ctcss_frequencies:
        print(
            "RX CTCSS       : "
            + ", ".join(node.rx_ctcss_frequencies)
        )
    else:
        print("RX CTCSS       : NOT FOUND")

    print(f"TX name        : {node.tx_name or 'NOT FOUND'}")
    print(f"TX frequency   : {node.tx_frequency or 'NOT FOUND'}")
    print(f"TX power       : {node.tx_power or 'NOT FOUND'}")
    print(
        f"TX CTCSS       : "
        f"{node.tx_ctcss_frequency or 'NOT FOUND'}"
    )

    print("-" * 60)

    if node.tone_to_talkgroup:
        print("Tone to TalkGroup:")

        for tone, talkgroup in node.tone_to_talkgroup.items():
            print(f"  {tone} Hz -> TG {talkgroup}")
    else:
        print("Tone to TalkGroup: NOT FOUND")

    print("-" * 60)
    print("Node information reader operational.")


if __name__ == "__main__":
    main()
