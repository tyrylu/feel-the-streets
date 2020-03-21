import re
from app.humanization_utils import format_class_name, underscored_to_words

def extract_xrc(fileobj, keywords, comment_tags, options):
    """Extract messages from xrc files.

    :param fileobj: the file-like object the messages should be extracted
                    from
    :param keywords: a list of keywords (i.e. function names) that should
                     be recognized as translation functions, ignored
    :param comment_tags: a list of translator tags to search for and
                         include in the results, ignored
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message, comments)``
             tuples
    :rtype: ``iterator``
    """
    tags_having_translatable_text = ["title", "label"]
    joined_tags = "|".join(tags_having_translatable_text)
    matching_regexp = r"<({0})>(.*)</({0})".format(joined_tags).encode("ascii")
    matching_re = re.compile(matching_regexp)
    for lineno, line in enumerate(fileobj):
        match = matching_re.search(line)
        if match:
            yield (lineno, None, match.group(2).decode("utf-8").replace("&amp;", "&"), [])


def extract_entity_related_strings(fileobj, keywords, comment_tags, options):
    """Extracts the entity, property and enum value names for translation.

    :param fileobj: the file-like object the messages should be extracted
                    from
    :param keywords: a list of keywords (i.e. function names) that should
                     be recognized as translation functions, ignored
    :param comment_tags: a list of translator tags to search for and
                         include in the results, ignored
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message, comments)``
             tuples
    :rtype: ``iterator``
    """
    for lineno, line in enumerate(fileobj):
        line = line.strip().decode("UTF-8")
        if not line:
            continue
        key, value = line.rsplit(":", 1)
        if key[0].isupper() and "entities.yml" in fileobj.name:
            yield (lineno, "", format_class_name(key), [])
        elif key[0].islower() and key not in {"fields", "display_template", "inherits"}:
            yield(lineno, "", underscored_to_words(key), [])

