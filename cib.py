import logging
from lxml import etree

LOG = logging.getLogger(__name__)


class CIB (object):
    def __init__(self, src):
        self.resources = {}
        self.resources_aux = {}
        self.kinds = {}
        self.start_constraints = []
        self.colocation_constraints = []

        if hasattr(src, 'read'):
            self.doc = etree.parse(src)
        else:
            self.doc = etree.fromstring(src)

        self.find_resources_1()
        self.find_resources_2()
        self.find_kinds()
        self.find_start_constraints()
        self.find_colocation_constraints()

    def find_resources_1(self):
        LOG.info('finding top-level resources')
        for rsrc in self.doc.xpath('/cib/configuration/resources/*'):
            id = rsrc.get('id')
            LOG.debug('found top-level resource %s', id)
            self.resources[id] = {
                'id': id,
                'kind': rsrc.tag,
            }

    def find_resources_2(self):
        LOG.info('finding second-level primitives')
        for rsrc in self.doc.xpath('/cib/configuration/resources/*/primitive'):
            id = rsrc.get('id')
            LOG.debug('found second-level resource %s', id)
            self.resources_aux[id] = {
                'id': id,
                'kind': rsrc.tag,
            }

    def find_kinds(self):
        self.kinds = set(rsrc['kind'] for rsrc in
                         self.resources.values() +
                         self.resources_aux.values())

    def find_start_constraints(self):
        for order in self.doc.xpath('/cib/configuration/constraints/rsc_order'):
            if order.get('first-action') != 'start':
                continue
            if order.get('then-action') != 'start':
                continue

            first_id = order.get('first')
            then_id = order.get('then')

            # check that given ids exist
            self.resource(first_id)
            self.resource(then_id)

            self.start_constraints.append((first_id, then_id))

    def find_colocation_constraints(self):
        for coloc in self.doc.xpath('/cib/configuration/constraints/rsc_colocation'):
            r1 = coloc.get('rsc')
            r2 = coloc.get('with-rsc')
            score = coloc.get('score')

            # check that given ids exist
            self.resource(r1)
            self.resource(r2)

            self.colocation_constraints.append((r1, r2, score))

    def resource(self, rid):
        rsrc = self.resources.get(
            rid, self.resources_aux.get(rid))

        if rsrc is None:
            raise KeyError(rsrc)

        return rsrc
