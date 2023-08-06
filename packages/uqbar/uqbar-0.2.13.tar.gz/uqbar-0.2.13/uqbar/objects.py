import collections
import inspect


def _dispatch_formatting(expr):
    if isinstance(expr, (list, tuple)):
        return _get_sequence_repr(expr)
    return repr(expr)


def _get_object_signature(expr):
    if expr.__new__ != object.__new__:
        return inspect.signature(expr.__new__)
    elif expr.__init__ != object.__init__:
        return inspect.signature(expr.__init__)
    raise TypeError(type(expr))


def _get_sequence_repr(expr):
    prototype = (bool, int, float, str, type(None))
    if all(isinstance(x, prototype) for x in expr):
        result = repr(expr)
        if len(result) < 50:
            return result
    if isinstance(expr, list):
        braces = '[', ']'
    else:
        braces = '(', ')'
    result = [braces[0]]
    for x in expr:
        for line in repr(x).splitlines():
            result.append('    ' + line)
        result[-1] += ','
    result.append('    ' + braces[-1])
    return '\n'.join(result)


def get_hash(expr):
    args, var_args, kwargs = get_vars(expr)
    hash_values = [type(expr)]
    for key, value in args.items():
        if isinstance(value, list):
            value = tuple(value)
        elif isinstance(value, set):
            value = frozenset(value)
        args[key] = value
    hash_values.append(tuple(args.items()))
    hash_values.append(tuple(var_args))
    for key, value in kwargs.items():
        if isinstance(value, list):
            value = tuple(value)
        elif isinstance(value, set):
            value = frozenset(value)
        kwargs[key] = value
    hash_values.append(tuple(sorted(kwargs.items())))
    return hash(tuple(hash_values))


def get_repr(expr, multiline=False):
    """
    Build a repr string for ``expr`` from its vars and signature.

    ::

        >>> class MyObject:
        ...     def __init__(self, arg1, arg2, *var_args, foo=None, bar=None, **kwargs):
        ...         self.arg1 = arg1
        ...         self.arg2 = arg2
        ...         self.var_args = var_args
        ...         self.foo = foo
        ...         self.bar = bar
        ...         self.kwargs = kwargs
        ...
        >>> my_object = MyObject('a', 'b', 'c', 'd', foo='x', quux=['y', 'z'])

    ::

        >>> import uqbar
        >>> print(uqbar.objects.get_repr(my_object))
        MyObject(
            'a',
            'b',
            'c',
            'd',
            foo='x',
            quux=['y', 'z'],
            )

    """
    signature = _get_object_signature(expr)
    defaults = {}
    for name, parameter in signature.parameters.items():
        if parameter.default is not inspect._empty:
            defaults[name] = parameter.default

    new_args, new_var_args, new_kwargs = get_vars(expr)
    args_parts = collections.OrderedDict()
    var_args_parts = []
    kwargs_parts = {}
    has_new_lines = multiline
    parts = []

    # Format keyword-optional arguments.
    for key, value in new_args.items():
        arg_repr = _dispatch_formatting(value)
        if '\n' in arg_repr:
            has_new_lines = True
        # If we don't have *args, we can use key=value formatting.
        # We can also omit arguments which match the signature's defaults.
        if not new_var_args:
            if key in defaults and value == defaults[key]:
                continue
            arg_repr = '{}={}'.format(key, arg_repr)
        args_parts[key] = arg_repr

    # Format *args
    for arg in new_var_args:
        arg_repr = _dispatch_formatting(arg)
        if '\n' in arg_repr:
            has_new_lines = True
        var_args_parts.append(arg_repr)

    # Format **kwargs
    for key, value in sorted(new_kwargs.items()):
        if key in defaults and value == defaults[key]:
            continue
        value = _dispatch_formatting(value)
        arg_repr = '{}={}'.format(key, value)
        has_new_lines = True
        kwargs_parts[key] = arg_repr

    # If we have *args, the initial args cannot use key/value formatting.
    if var_args_parts:
        for part in args_parts.values():
            parts.append(part)
        parts.extend(var_args_parts)
        for _, part in sorted(kwargs_parts.items()):
            parts.append(part)

    # Otherwise, we can combine and sort all key/value pairs.
    else:
        args_parts.update(kwargs_parts)
        for _, part in sorted(args_parts.items()):
            parts.append(part)

    # If we should format on multiple lines, add the appropriate formatting.
    if has_new_lines and parts:
        for i, part in enumerate(parts):
            parts[i] = '\n'.join('    ' + line for line in part.split('\n'))
        parts.append('    )')
        parts = ',\n'.join(parts)
        return '{}(\n{}'.format(type(expr).__name__, parts)

    parts = ', '.join(parts)
    return '{}({})'.format(type(expr).__name__, parts)


def get_vars(expr):
    """
    Get ``args``, ``var args`` and ``kwargs`` for an object ``expr``.

    ::

        >>> class MyObject:
        ...     def __init__(self, arg1, arg2, *var_args, foo=None, bar=None, **kwargs):
        ...         self.arg1 = arg1
        ...         self.arg2 = arg2
        ...         self.var_args = var_args
        ...         self.foo = foo
        ...         self.bar = bar
        ...         self.kwargs = kwargs
        ...
        >>> my_object = MyObject('a', 'b', 'c', 'd', foo='x', quux=['y', 'z'])

    ::

        >>> import uqbar
        >>> args, var_args, kwargs = uqbar.objects.get_vars(my_object)

    ::

        >>> args
        OrderedDict([('arg1', 'a'), ('arg2', 'b')])

    ::

        >>> var_args
        ['c', 'd']

    ::

        >>> kwargs
        {'foo': 'x', 'bar': None, 'quux': ['y', 'z']}

    """
    # print('VARS?', type(expr))
    signature = _get_object_signature(expr)
    # print('SIG?', signature)
    args = collections.OrderedDict()
    var_args = []
    kwargs = {}
    if expr is None:
        return args, var_args, kwargs
    for i, (name, parameter) in enumerate(signature.parameters.items()):
        # print('   ', parameter)
        if i == 0 and name in ('self', 'cls', 'class_', 'klass'):
            continue
        if parameter.kind is inspect._POSITIONAL_ONLY:
            try:
                args[name] = getattr(expr, name)
            except AttributeError:
                args[name] = expr[name]
        elif parameter.kind is inspect._POSITIONAL_OR_KEYWORD:

            found = False
            for x in (name, '_' + name):
                try:
                    args[name] = getattr(expr, x)
                    found = True
                    break
                except AttributeError:
                    continue
            if found:
                continue

            found = False
            for x in (name, '_' + name):
                try:
                    args[name] = expr[x]
                    found = True
                    break
                except KeyError:
                    continue
            if not found:
                raise ValueError('Cannot find value for {!r}'.format(name))

        elif parameter.kind is inspect._VAR_POSITIONAL:
            try:
                var_args.extend(expr[:])
            except TypeError:
                var_args.extend(getattr(expr, name))
        elif parameter.kind is inspect._KEYWORD_ONLY:
            try:
                kwargs[name] = getattr(expr, name)
            except AttributeError:
                kwargs[name] = expr[name]
        elif parameter.kind is inspect._VAR_KEYWORD:
            items = {}
            if hasattr(expr, 'items'):
                items = expr.items()
            elif hasattr(expr, name):
                mapping = getattr(expr, name)
                if not isinstance(mapping, dict):
                    mapping = dict(mapping)
                items = mapping.items()
            elif hasattr(expr, '_' + name):
                mapping = getattr(expr, '_' + name)
                if not isinstance(mapping, dict):
                    mapping = dict(mapping)
                items = mapping.items()
            for key, value in items:
                if key not in args:
                    kwargs[key] = value
    return args, var_args, kwargs


def new(expr, *args, **kwargs):
    """
    Template an object.

    ::

        >>> class MyObject:
        ...     def __init__(self, arg1, arg2, *var_args, foo=None, bar=None, **kwargs):
        ...         self.arg1 = arg1
        ...         self.arg2 = arg2
        ...         self.var_args = var_args
        ...         self.foo = foo
        ...         self.bar = bar
        ...         self.kwargs = kwargs
        ...
        >>> my_object = MyObject('a', 'b', 'c', 'd', foo='x', quux=['y', 'z'])

    ::

        >>> import uqbar
        >>> new_object = uqbar.objects.new(my_object, foo=666, bar=1234)
        >>> print(uqbar.objects.get_repr(new_object))
        MyObject(
            'a',
            'b',
            'c',
            'd',
            bar=1234,
            foo=666,
            quux=['y', 'z'],
            )

    Original object is unchanged:

    ::

        >>> print(uqbar.objects.get_repr(my_object))
        MyObject(
            'a',
            'b',
            'c',
            'd',
            foo='x',
            quux=['y', 'z'],
            )

    """
    # TODO: Clarify old vs. new variable naming here.
    current_args, current_var_args, current_kwargs = get_vars(expr)
    new_kwargs = current_kwargs.copy()

    recursive_arguments = {}
    for key in tuple(kwargs):
        if '__' in key:
            value = kwargs.pop(key)
            key, _, subkey = key.partition('__')
            recursive_arguments.setdefault(key, []).append((subkey, value))

    for key, pairs in recursive_arguments.items():
        recursed_object = current_args.get(key, current_kwargs.get(key))
        if recursed_object is None:
            continue
        kwargs[key] = new(recursed_object, **dict(pairs))

    if args:
        current_var_args = args
    for key, value in kwargs.items():
        if key in current_args:
            current_args[key] = value
        else:
            new_kwargs[key] = value

    new_args = list(current_args.values()) + list(current_var_args)
    return type(expr)(*new_args, **new_kwargs)


def compare_objects(object_one, object_two):
    object_one_values = type(object_one), get_vars(object_one)
    try:
        object_two_values = type(object_two), get_vars(object_two)
    except AttributeError:
        object_two_values = type(object_two), object_two
    return object_one_values == object_two_values
