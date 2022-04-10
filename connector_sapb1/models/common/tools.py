# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import hashlib


def list2hash(l):
    hash = hashlib.sha256()
    for e in l:
        if isinstance(e, int):
            e9 = str(e)
            try:
                b = int(e9)
            except:
                raise
            if b != e:
                raise Exception("Unexpected")
        elif isinstance(e, str):
            e9 = e
        elif e is None:
            e9 = ''
        else:
            raise Exception("Unexpected type for a key: type %" % type(e))
        hash.update(e9.encode('utf8'))
    return hash.hexdigest()
