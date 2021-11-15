import hashlib
from os import remove, listdir, path


def cleanup_dir(dir):
    if path.exists(dir) and path.isdir(dir):
        for f in listdir(dir):
            remove(path.join(dir, f))


def hash(s, l=16):
    return hashlib.md5(s.encode()).hexdigest()[:l]


def filter_list(l, filters):
    if filters and isinstance(filters, dict):
        filtered = []

        for o in l:
            match = True
            for k, v in filters.items:
                if hasattr(o, k):
                    val = getattr(o, k)

                    if isinstance(v, dict):
                        filter_type = v['filter_type']
                        fitler_val = v['filter_val']
                    elif isinstance(v, list) or isinstance(v, tuple):
                        if val not in v:
                            match = False
                            break
                    elif getattr(o, k) == v:
                        match = False
                        break

            if match:
                filtered.append(o)
    else:
        filtered = l

    return filtered


def rangify(x, min, max):
    if x < min:
        return min

    if x > max:
        return max

    return x
