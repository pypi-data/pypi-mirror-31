# -*- coding: utf-8 -*-
from __future__ import absolute_import

import copy
import six
from six.moves import map

import dpath.util
from jsonspec.reference import resolve


def schema_var_name(path):
    return ''.join(map(str.capitalize, map(str, path)))


class RefNode(dict):

    def __init__(self, data, ref):
        self.ref = ref
        super(RefNode, self).__init__(data)

    def __repr__(self):
        return schema_var_name(self.ref)


class Swagger(object):

    separator = '\0'

    def __init__(self, data):
        self.data = data
        self.origin_data = copy.deepcopy(data)
        self._definitions = []
        self._resolve_definitions()
        self._get_cached = {}

        self._process_ref()

    def _process_ref(self):
        """
        resolve all references util no reference exists
        """
        while 1:
            li = list(self.search(['**', '$ref']))
            if not li:
                break
            for path, ref in li:
                data = resolve(self.data, ref)
                path = path[:-1]
                self.set(path, data)

    def _resolve_definitions(self):
        """
        ensure there not exists circular references and load definitions
        """

        def get_definition_refs():
            definition_refs_default = {}
            definition_refs = {}
            for path, _ in self.search(['definitions', '*']):
                definition_refs_default[path] = set([])
            for path, ref in self.search(['definitions', '**', '$ref']):
                schema = tuple(path[0:2])
                ref = ref.lstrip('#/').split('/')
                ref = tuple(ref)

                if schema in list(definition_refs.keys()):
                    definition_refs[schema].add(ref)
                else:
                    definition_refs[schema] = set([ref])

            definition_refs_default.update(definition_refs)
            return definition_refs_default

        definition_refs = get_definition_refs()
        while definition_refs:
            ready = {
                definition for definition, refs
                in six.iteritems(definition_refs) if not refs
            }
            if not ready:
                msg = '$ref circular references found!\n'
                raise ValueError(msg)
            for definition in ready:
                del definition_refs[definition]
            for refs in six.itervalues(definition_refs):
                refs.difference_update(ready)

            self._definitions += ready

    def search(self, path):
        for p, d in dpath.util.search(
                self.data, list(path), True, self.separator):
            yield tuple(p.split(self.separator)), d

    def get(self, path):
        key = ''.join(path)
        if key not in self._get_cached:
            value = self.data
            for p in path:
                value = value[p]
            self._get_cached[key] = value
        return self._get_cached[key]

    def set(self, path, data):
        _set(self.data, path, data)

    @property
    def definitions(self):
        return self._definitions

    @property
    def scopes_supported(self):
        for _, data in self.search(['securityDefinitions', '*', 'scopes']):
            return list(data.keys())
        return []

    @property
    def module_name(self):
        return self.base_path.strip('/').replace('/', '_')

    @property
    def base_path(self):
        return self.data.get('basePath', '/v1')


def _set(obj, path, value):
    """
    set value for path in the given obj only if path exists.
    if not, IndexError or KeyError will be raised.
    params:
        obj - dict or list object
        path - list object represents keys in object
        value - value to be set
    """
    target = obj
    for elem in path[:-1]:
        if isinstance(target, list):
            target = target[int(elem)]
        elif isinstance(target, dict):
            if elem not in target:
                # special handler out of int status_code
                # definition in swagger spec
                elem = int(elem)
            target = target[elem]
        else:
            raise TypeError('try to extract `%s` from target %s'
                            % (elem, target))
    idx = path[-1]
    if isinstance(target, dict):
        target[idx] = value
    elif isinstance(target, list):
        target[int(idx)] = value
    else:
        raise TypeError('try to set `%s` for target %s' % (idx, target))
