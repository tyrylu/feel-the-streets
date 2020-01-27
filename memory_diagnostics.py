import os
import pdb
import collections
import gc
import sys
import psutil

def print_summary(label, limit=None):
    print(label)
    print("{0} gc tracked objects".format(len(gc.get_objects())))
    proc = psutil.Process(os.getpid())
    info = proc.memory_full_info()
    print("Current resident set: {0} bytes, peak resideent set: {1} bytes".format(info.rss, info.peak_wset))
    summary = get_summary()
    summary.sort(key=lambda i: i[2], reverse=True)
    if limit:
        summary = summary[:limit]
    for name, count, size, biggest, _ in summary:
        print("{0}: {1} instances taking {2} bytes, biggest takes {3} bytes".format(name, count, size, biggest))
    pdb.set_trace()
def get_summary():
    obj_list = gc.get_objects()
    res = []
    per_class_counts = collections.Counter()
    per_class_objects = collections.defaultdict(list)
    for o in obj_list:
        per_class_counts[type(o).__qualname__] += 1
        per_class_objects[type(o).__qualname__].append(o)
    for name, count in per_class_counts.most_common():
        class_size = 0
        biggest = 0
        biggest_obj = None
        for o in per_class_objects[name]:
            try:
                size = sys.getsizeof(o)
                class_size += size
                if size > biggest:
                    biggest = size
                    biggest_obj = o
            except:
                failures += 1
        res.append((name, count, class_size, biggest, biggest_obj))

    return res