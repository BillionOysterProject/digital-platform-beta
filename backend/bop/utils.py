from __future__ import absolute_import
from __future__ import unicode_literals
import re
import sys
import collections
from six import string_types

PARAM_OR_RETURNS_REGEX = re.compile(r':(?:param|returns)')
RETURNS_REGEX = re.compile(r':returns: (?P<doc>.*)', re.S)
PARAM_REGEX = re.compile(r':param (?P<name>[\*\w]+): (?P<doc>.*?)(?:(?=:param)|(?=:return)|(?=:raises)|\Z)', re.S)

def as_bool(value):
    return ('{}'.format(value).lower() in ['true', '1', 'yes'])

# borrowed from openstack/rally:
# https://github.com/openstack/rally/blob/7153e0cbc5b0e6433313a3bc6051b2c0775d3804/rally/common/plugin/info.py#L63-L110
# See LICENSE.openstack at the root of this project for license details.
#
def trim(docstring):
    """trim function from PEP-257"""
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    # Current code/unittests expects a line return at
    # end of multiline docstrings
    # workaround expected behavior from unittests
    if "\n" in docstring:
        trimmed.append("")

    # Return a single string:
    return "\n".join(trimmed)


def reindent(string):
    return "\n".join(l.strip() for l in string.strip().split("\n"))


def parse_docstring(docstring):
    """Parse the docstring into its components.
    :returns: a dictionary of form
              {
                  "short_description": ...,
                  "long_description": ...,
                  "params": [{"name": ..., "doc": ...}, ...],
                  "returns": ...
              }
    """

    short_description = long_description = returns = ""
    params = []

    if docstring:
        docstring = trim(docstring)

        lines = docstring.split("\n", 1)
        short_description = lines[0]

        if len(lines) > 1:
            long_description = lines[1].strip()

            params_returns_desc = None

            match = PARAM_OR_RETURNS_REGEX.search(long_description)
            if match:
                long_desc_end = match.start()
                params_returns_desc = long_description[long_desc_end:].strip()
                long_description = long_description[:long_desc_end].rstrip()

            if params_returns_desc:
                params = [
                    {"name": name, "doc": trim(doc)}
                    for name, doc in PARAM_REGEX.findall(params_returns_desc)
                ]

                match = RETURNS_REGEX.search(params_returns_desc)
                if match:
                    returns = reindent(match.group("doc"))

    return {
        "short_description": short_description,
        "long_description": long_description,
        "params": params,
        "returns": returns
    }


def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def compact(source, keep_if=lambda k, v: v is not None):
    """
    Takes a dictionary and returns a copy with elements matching a given lambda removed. The
    default behavior will remove any values that are `None`.

    Args:
        source (dict): The dictionary to operate on.

        keep_if (lambda(k,v), optional): A function or lambda that will be called for each
            (key, value) pair.  If the function returns truthy, the element will be left alone,
            otherwise it will be removed.
    """
    if isinstance(source, dict):
        return {
            k: v for k, v in source.items() if v is not None and keep_if(k, v)
        }

    raise ValueError("Expected: dict, got: {0}".format(type(source)))


def mutate_dict(
    inValue,
    keyFn=lambda k: k,
    valueFn=lambda v: v,
    keyTypes=None,
    valueTypes=None,
    **kwargs
):
    """
    Takes an input dict or list-of-dicts and applies ``keyfn`` function to all of the keys in
    both the top-level and any nested dicts or lists, and ``valuefn`` to all
    If the input value is not of type `dict` or `list`, the value will be returned as-is.
    Args:
        inValue (any): The dict to mutate.
        keyFn (lambda): The function to apply to keys.
        valueFn (lambda): The function to apply to values.
        keyTypes (tuple, optional): If set, only keys of these types will be mutated
            with ``keyFn``.
        valueTypes (tuple, optional): If set, only values of these types will be mutated
            with ``valueFn``.
    Returns:
        A recursively mutated dict, list of dicts, or the value as-is (described above).
    """

    # this is here as a way of making sure that the various places where recursion is done always
    # performs the same call, preserving all arguments except for value (which is what changes
    # between nested calls).
    def recurse(value):
        return mutate_dict(
            value,
            keyFn=keyFn,
            valueFn=valueFn,
            keyTypes=keyTypes,
            valueTypes=valueTypes,
            **kwargs
        )

    # handle dicts
    if isinstance(inValue, dict):
        # create the output dict
        outputDict = dict()

        # for each dict item...
        for k, v in inValue.items():
            # apply the keyFn to some or all of the keys we encounter
            if keyTypes is None or (isinstance(keyTypes, tuple) and isinstance(k, keyTypes)):
                # prepare the new key
                k = keyFn(k, **kwargs)

            # apply the valueFn to some or all of the values we encounter
            if valueTypes is None or (isinstance(valueTypes, tuple) and isinstance(v, valueTypes)):
                v = valueFn(v)

            # recurse depending on the value's type
            #
            if isinstance(v, dict):
                # recursively call mutate_dict() for nested dicts
                outputDict[k] = recurse(v)
            elif isinstance(v, list):
                # recursively call mutate_dict() for each element in a list
                outputDict[k] = [recurse(i) for i in v]
            else:
                # set the value straight up
                outputDict[k] = v

        # return the now-populated output dict
        return outputDict

    # handle lists-of-dicts
    elif isinstance(inValue, list) and len(inValue) > 0:
        return [recurse(i) for i in inValue]

    else:
        # passthrough non-dict value as-is
        return inValue


def autotype(value):
    if isinstance(value, string_types):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            try:
                return int(value)
            except ValueError:
                pass

            try:
                return float(value)
            except ValueError:
                pass

    return value


class dotdict(dict):
    """
    Provides dot.notation access to dictionary attributes
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__