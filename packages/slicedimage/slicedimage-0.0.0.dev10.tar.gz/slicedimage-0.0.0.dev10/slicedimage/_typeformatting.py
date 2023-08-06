import enum


def format_tile_dimensions(tile_dimensions):
    """
    Given a dictionary mapping keys to values, where the keys may either be strings or enums, and the values may either
    be iterables or not, return a new dictionary with the same contents, except the keys are converted to strings and
    the values that are iterables are converted to tuples.
    """
    result = dict()
    for name, value in tile_dimensions.items():
        try:
            iter(value)
            result[_str_or_enum_to_str(name)] = tuple(value)
        except TypeError:
            result[_str_or_enum_to_str(name)] = _str_or_enum_to_str(value)
    return result


def format_imagepartition_dimensions(imagepartition_dimensions):
    """
    Given an iterable of strings or enums, return a frozenset consisting of the same values, except all converted to
    strings.
    """
    return frozenset(_str_or_enum_to_str(imagepartition_dimension)
                     for imagepartition_dimension in imagepartition_dimensions)


def format_imagepartition_shape(d):
    """
    Given a dictionary mapping keys to values, where the keys may either be strings or enums, return a new dictionary
    where the keys are all converted to strings.
    """
    result = dict()
    for name, value in d.items():
        result[_str_or_enum_to_str(name)] = value
    return result


def _str_or_enum_to_str(value):
    """
    Given a scalar dimension, return the enumeration  mapping names to values that may either be iterables or not, return a new dictionary with the
    same contents, except the values that are iterables are converted to tuples.
    """
    if isinstance(value, enum.Enum):
        return value.value
    else:
        return value
