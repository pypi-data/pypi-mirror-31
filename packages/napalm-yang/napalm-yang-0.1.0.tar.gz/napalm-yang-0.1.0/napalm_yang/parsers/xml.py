from builtins import super

from napalm_yang.parsers.jsonp import JSONParser

import xmltodict


class XMLParser(JSONParser):

    def init_native(self, native):
        resp = []
        for n in native:
            if isinstance(n, dict):
                resp.append(n)
            else:
                resp.append(xmltodict.parse(n, force_cdata=True))

        return resp

    def _parse_leaf_default(self, attribute, mapping, data):
        attribute = mapping.get("attribute", None)
        path = mapping.get("path", None)
        if attribute and path:
            attribute = "@{}".format(attribute)
            mapping["path"] = "{}.{}".format(mapping["path"], attribute)
        elif "present" not in mapping and path:
            attribute = "#text"
            mapping["path"] = "{}.{}".format(mapping["path"], "#text")
        return super()._parse_leaf_default(attribute, mapping, data)
