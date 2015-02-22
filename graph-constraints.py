#!/usr/bin/python

import sys
import argparse
import itertools
from lxml import etree
import logging

import colerator
import cib

LOG = logging.getLogger('dotcib')
args = None


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
    p.add_argument('--start-constraints', '-S',
                   action='store_const',
                   const='start',
                   dest='constraints')
    p.add_argument('--colocation-constraints', '-C',
                   action='store_const',
                   const='colocation',
                   dest='constraints')
    p.add_argument('cib', nargs='?')
    p.set_defaults(loglevel=logging.WARN,
                   constraints='start')
    return p.parse_args()


def find_colors(doc):
    colors = colerator.Simple(len(doc.kinds))
    return dict(zip(doc.kinds, colors))


def graph_start_constraints(doc):
    global args

    # visible_ids is the list of resource ids that will be included
    # in the graph.  That means "all top level resources and also any
    # second-level resources that are part of a dependency".
    visible_ids = set(doc.resources.keys())
    kinds = find_colors(doc)

    for left, right in doc.start_constraints:
        visible_ids.add(left)
        visible_ids.add(right)

    with open(args.output, 'w') if args.output else sys.stdout as fd:
        LOG.info('generating graph')
        print >>fd,  'digraph {'
        print >>fd,  'rankdir=LR'

        LOG.debug('printing nodes')
        nodes = {}
        counter = itertools.count()
        for rid in visible_ids:
            rsrc = doc.resource(rid)
            rsrc['node'] = 'node%d' % counter.next()
            nodes[rsrc['id']] = rsrc['node']
            rsrc['color'] = kinds[rsrc['kind']]

            print >>fd,  '%s [label="%s", color="%s", style="filled"]' % (
                rsrc['node'],
                rsrc['id'],
                rsrc['color'])

        LOG.debug('printing edges')
        for left, right in doc.start_constraints:
            print >>fd,  '%s -> %s' % (nodes[left], nodes[right])
        print >>fd,  '}'

    LOG.info('all done')


def graph_colocation_constraints(doc):
    global args

    # visible_ids is the list of resource ids that will be included
    # in the graph.  That means "all top level resources and also any
    # second-level resources that are part of a dependency".
    visible_ids = set(doc.resources.keys())
    kinds = find_colors(doc)

    for left, right, score in doc.colocation_constraints:
        visible_ids.add(left)
        visible_ids.add(right)

    with open(args.output, 'w') if args.output else sys.stdout as fd:
        LOG.info('generating graph')
        print >>fd,  'digraph {'
        print >>fd,  'rankdir=LR'

        LOG.debug('printing nodes')
        nodes = {}
        counter = itertools.count()
        for rid in visible_ids:
            rsrc = doc.resource(rid)
            rsrc['node'] = 'node%d' % counter.next()
            nodes[rsrc['id']] = rsrc['node']
            rsrc['color'] = kinds[rsrc['kind']]

            print >>fd,  '%s [label="%s", color="%s", style="filled"]' % (
                rsrc['node'],
                rsrc['id'],
                rsrc['color'])

        LOG.debug('printing edges')
        for left, right, score in doc.colocation_constraints:
            print >>fd,  '%s -> %s [label="%s"]' % (
                nodes[left],
                nodes[right],
                score)
        print >>fd,  '}'

    LOG.info('all done')


def main():
    global args

    args = parse_args()
    logging.basicConfig(
        level=args.loglevel)

    if args.constraints not in ['start', 'colocation']:
        raise ValueError(args.constraints)

    with open(args.cib) if args.cib else sys.stdin as fd:
        doc = cib.CIB(fd)

    if args.constraints == 'start':
        graph_start_constraints(doc)
    elif args.constraints == 'colocation':
        graph_colocation_constraints(doc)
    else:
        raise ValueError(args.constraints)


if __name__ == '__main__':
    main()
