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
    p.add_argument('--output', '-o')
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

    LOG.info('finding top-level resources')
    for rsrc in doc.xpath('/cib/configuration/resources/*'):
        id = rsrc.get('id')
        LOG.debug('found top-level resource %s', id)
        resources[id] = {
            'id': id,
            'kind': rsrc.tag,
        }

    # this loop find second-level primitives (primitives contained by
    # a top-level container such as a clone or resource group).  These
    # are only displayed on the graph if they are part of an explicit
    # dependency with another resource.
    LOG.info('finding second-level primitives')
    for rsrc in doc.xpath('/cib/configuration/resources/*/primitive'):
        id = rsrc.get('id')
        LOG.debug('found second-level resource %s', id)
        resources_aux[id] = {
            'id': id,
            'kind': rsrc.tag,
        }

    LOG.info('calculating colors')
    kinds = set(x['kind'] for x in
                resources.values() +
                resources_aux.values())
    colors = colerator.Simple(len(kinds))
    kinds = dict(zip(kinds, colors))

    # visible_ids is the list of resource ids that will be included
    # in the graph.  That means "all top level resources and also any
    # second-level resources that are part of a dependency".
    visible_ids = set(resources.keys())

    LOG.info('finding start constraints')
    for order in doc.xpath('/cib/configuration/constraints/rsc_order'):
        if order.get('first-action') != 'start':
            continue
        if order.get('then-action') != 'start':
            continue

        first_id = order.get('first')
        then_id = order.get('then')

        visible_ids.add(first_id)
        visible_ids.add(then_id)
        constraints.append((first_id, then_id))

    with open(args.output, 'w') if args.output else sys.stdout as fd:
        LOG.info('generating graph')
        print >>fd,  'digraph {'
        print >>fd,  'rankdir=LR'

        LOG.debug('print >>fd, ing nodes')
        nodes = {}
        counter = itertools.count()
        for rid in visible_ids:
            rsrc = resources.get(rid, resources_aux.get(rid))
            if rsrc is None:
                raise KeyError(rsrc)
            rsrc['node'] = 'node%d' % counter.next()
            nodes[rsrc['id']] = rsrc['node']
            rsrc['color'] = kinds[rsrc['kind']]

            print >>fd,  '%s [label="%s", color="%s", style="filled"]' % (
                rsrc['node'],
                rsrc['id'],
                rsrc['color'])

        LOG.debug('print >>fd, ing edges')
        for left, right in constraints:
            print >>fd,  '%s -> %s' % (nodes[left], nodes[right])
        print >>fd,  '}'

    LOG.info('all done')


if __name__ == '__main__':
    main()
