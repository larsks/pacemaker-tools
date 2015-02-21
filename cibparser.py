#!/usr/bin/python

import sys
import argparse
import itertools
from lxml import etree
import logging

import colerator

LOG = logging.getLogger('dotcib')


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--verbose', '-v',
                   action='store_const',
                   const=logging.INFO,
                   dest='loglevel')
    p.add_argument('--debug', '-d',
                   action='store_const',
                   const=logging.DEBUG,
                   dest='loglevel')
    p.add_argument('cib', nargs='?')
    p.set_defaults(loglevel=logging.WARN)
    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        level=args.loglevel)

    with open(args.cib) if args.cib else sys.stdin as fd:
        doc = etree.parse(fd)

    constraints = []
    resources = {}
    resources_aux = {}

    for rsrc in doc.xpath('/cib/configuration/resources/*'):
        id = rsrc.get('id')
        resources[id] = {
            'id': id,
            'kind': rsrc.tag,
        }
    for rsrc in doc.xpath('/cib/configuration/resources/*/primitive'):
        id = rsrc.get('id')
        resources_aux[id] = {
            'id': id,
            'kind': rsrc.tag,
        }

    kinds = set(x['kind'] for x in resources.values())
    colors = colerator.Simple(len(kinds))
    kinds = dict(zip(kinds, colors))

    for order in doc.xpath('/cib/configuration/constraints/rsc_order'):
        if order.get('first-action') != 'start':
            continue
        if order.get('then-action') != 'start':
            continue

        constraints.append((order.get('first'), order.get('then')))

    if args.debug:
        import pprint
        pprint.pprint(constraints, stream=sys.stderr)

    print 'digraph {'
    print 'rankdir=LR'
    rids = {}
    counter = itertools.count()
    for resource in resources.values():
        rids[resource['id']] = 'node%d' % counter.next()
        print '%s [label="%s", color="%s", style="filled"]' % (
            rids[resource['id']],
            resource['id'],
            kinds[resource['kind']])

    for left, right in constraints:
        for id in [left, right]:
            if id in resources_aux:
                resource = resources_aux[id]
                rids[resource['id']] = 'node%d' % counter.next()
                print '%s [label="%s", color="%s", style="filled"]' % (
                    rids[resource['id']],
                    resource['id'],
                    kinds[resource['kind']])

    for left, right in constraints:
        print '%s -> %s' % (rids[left], rids[right])
    print '}'


if __name__ == '__main__':
    main()
