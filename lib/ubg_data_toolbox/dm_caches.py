import os
import json


class md_cache_default_values(object):
    """
    A cache object for default values. This is basically a key-value storage
    """
    def __init__(self, filename):
        self.cache = {}
        self.filename = filename

        if self.filename is not None and os.path.isfile(self.filename):
            self.load_cache()

    def load_cache(self):
        try:
            with open(self.filename, 'r') as fid:
                self.cache = json.load(fid)
        except json.JSONDecodeError:
            pass

    def save_cache(self):
        if self.filename is None:
            return
        with open(self.filename, 'w') as fid:
            json.dump(self.cache, fid)

        # import IPython
        # IPython.embed()
    def get(self, key):
        """Get the item associated with a given key"""
        return self.cache.get(key, '')

    def set(self, key, value):
        self.cache[key] = value
        self.save_cache()

    def __str__(self):
        out_str = '<red>' + 80 * '=' + '</red>\n'
        out_str += 'Cache object'
        out_str += 'Items:\n'
        for key, item in sorted(self.cache.items()):
            out_str += ' ' * 4 + '{}: {}\n'.format(key, item)
        out_str += '<red>' + 80 * '=' + '</red>\n'
        return out_str

    def merge_with_cache(self, other_cache):
        """
        Integrate all entries of the other cache object into this one,
        prioritizing the other cache entries
        """
        if other_cache is None:
            return
        self.cache.update(other_cache.cache)

    def import_md_dict(self, md_dict):
        for section in md_dict.keys():
            for name, item in md_dict[section].items():
                if item.value is not None:
                    self.cache[name] = item.value
