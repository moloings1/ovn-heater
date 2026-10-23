#!/usr/bin/env python3

import argparse
import errno
import ipaddress
from pyroute2 import IPRoute


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vrf-dev', required=True)
    parser.add_argument('--nexthop', required=True)
    parser.add_argument('--table', type=int, required=True)
    parser.add_argument('--n-routes', type=int, required=True)
    parser.add_argument('--base', required=True)
    args = parser.parse_args()

    ipr = IPRoute()
    try:
        idx = ipr.link_lookup(ifname=args.vrf_dev)[0]
        try:
            ipr.addr('add', index=idx, address=args.nexthop, prefixlen=32)
        except Exception as e:
            # The nexthop is already configured from an earlier injection
            # into the same VRF.
            if getattr(e, 'code', None) != errno.EEXIST:
                raise

        base_ip = ipaddress.IPv4Address(args.base)

        for r in range(args.n_routes):
            dst = f"{base_ip + r}/32"
            ipr.route(
                'add',
                dst=dst,
                gateway=args.nexthop,
                oif=idx,
                table=args.table,
                proto=186,
            )
    finally:
        ipr.close()


if __name__ == '__main__':
    main()
