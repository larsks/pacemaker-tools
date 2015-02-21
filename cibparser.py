#!/usr/bin/python

import os
import sys
import argparse
import itertools
from lxml import etree


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--debug', '-d',
                   action='store_true')
    p.add_argument('cib', nargs='?')
    return p.parse_args()


def main():
    args = parse_args()

    with open(args.cib) if args.cib else sys.stdin as fd:
        doc = etree.parse(fd)

    constraints = []
    resources = set()
    for order in doc.xpath('/cib/configuration/constraints/rsc_order'):
        if order.get('first-action') != 'start':
            continue
        if order.get('then-action') != 'start':
            continue

        constraints.append((order.get('first'), order.get('then')))
        resources.add(order.get('first'))
        resources.add(order.get('then'))

    if args.debug:
        import pprint
        pprint.pprint(constraints, stream=sys.stderr)

    print 'digraph {'
    print 'rankdir=LR'
    rids = {}
    counter = itertools.count()
    for resource in resources:
        rids[resource] = 'node%d' % counter.next()
        print '%s [label="%s"]' % (rids[resource], resource)

    for left, right in constraints:
        print '%s -> %s' % (rids[left], rids[right])
    print '}'


if __name__ == '__main__':
    main()
