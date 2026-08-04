"""
SvxLink configuration reader test.
"""

from src.modules.configreader import ConfigReader


def main() -> None:
    """
    Load and print the available SvxLink node information.
    """

    reader = ConfigReader()
    node = reader.load()

    print("=" * 60)
    print("SVX Guardian - SvxLink Configuration Test")
    print("=" * 60)

    print(f"Config file   : {node.config_file}")
    print(f"Callsign      : {node.callsign or 'NOT FOUND'}")
    print(f"Description   : {node.description or 'NOT FOUND'}")
    print(f"QTH           : {node.qth or 'NOT FOUND'}")
    print(f"Locator       : {node.locator or 'NOT FOUND'}")
    print(f"Reflector     : {node.reflector or 'NOT FOUND'}")

    if node.modules:
        print(f"Modules       : {', '.join(node.modules)}")
    else:
        print("Modules       : NOT FOUND")

    print("-" * 60)

    if node.callsign:
        print("Configuration reader operational.")
    else:
        print("Configuration file loaded, but callsign was not found.")


if __name__ == "__main__":
    main()
