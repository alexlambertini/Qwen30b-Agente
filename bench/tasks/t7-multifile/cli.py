import argparse

from service import InventoryService


def main(argv, service: InventoryService) -> int:
    parser = argparse.ArgumentParser(prog="inv")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_add = sub.add_parser("add")
    p_add.add_argument("name")
    p_add.add_argument("--qty", type=int, default=0)
    p_add.add_argument("--price", type=float, default=0.0)
    sub.add_parser("list")
    args = parser.parse_args(argv)
    if args.cmd == "add":
        service.add_item(args.name, args.qty, args.price)
    elif args.cmd == "list":
        for item in sorted(service.repo.all(), key=lambda i: i.name):
            print(f"{item.name}\t{item.quantity}")
    return 0
