"""
This module contains common functions that can be used for either :class:`~inxs.Rule`
s' tests, as handler functions or simple transformation steps.

Community contributions are highly appreciated, but it's hard to layout hard criteria
for what belongs here and what not. In doubt open a pull request with your proposal
as far as it proved functional to you, it doesn't need to be polished at that point.
"""

# TODO indicate use area in function's docstrings; and whether they return something
# TODO delete unneeded symbols in setup functions' locals
# TODO check whether recently additions could be singleton_handler


import logging
import re
from copy import deepcopy
from typing import Callable, Dict, List, Mapping, Sequence, Tuple, Union

from lxml import builder, etree
from lxml.html import builder as html_builder


from inxs import dot_lookup, lxml_utils, Ref, singleton_handler
from inxs.utils import is_Ref, resolve_Ref_values_in_mapping

# helpers


logger = logging.getLogger(__name__)
dbg = logger.debug
nfo = logger.info

__all__ = []


def export(func):
    __all__.append(func.__name__)
    return func


# the actual lib

@export
@singleton_handler
def add_html_classes(*classes, target=Ref('element')):
    """ Adds the string tokens passed as positional arguments to the
        ``classes`` attribute of an element specified by ``target``.
        Per default that is a :func:`~inxs.Ref` to the matching element of a
        rule. """

    def add_items(_set, value):
        if isinstance(value, str):
            _set.add(value)
        elif isinstance(value, Sequence):
            _set.update(value)
        else:
            raise RuntimeError

    def processor(transformation):
        if not classes:
            return

        # TODO input type specialized handlers
        _classes = set()
        for cls in classes:
            if not cls:
                continue
            if is_Ref(cls):
                add_items(_classes, cls(transformation))
            else:
                add_items(_classes, cls)

        element = target(transformation)
        value = element.attrib.get('class', '').strip()
        _classes.update(x.strip() for x in value.split() if x)
        element.attrib['class'] = ' '.join(sorted(_classes))
    return processor


@export
@singleton_handler
def append(name, symbol=Ref('previous_result'), copy_element=False):
    """ Appends the object referenced by ``symbol`` (default: the result of the previous
        :term:`handler function`) to the that is object available as ``name`` in the
        :attr:`Transformation._available_symbols`. If the object is an element and
        ``copy_element`` is ``True``, a copy is appended to the target. """

    def handler(previous_result, transformation):
        obj = symbol(transformation)
        if copy_element and isinstance(obj, etree._Element):
            obj = deepcopy(obj)

        if '.' in name:
            namespace, path = name.split('.', 1)
            target = transformation._available_symbols[namespace]
            target = dot_lookup(target, path)
        else:
            target = transformation._available_symbols[name]

        target.append(obj)

        return previous_result

    return handler


@export
def cleanup_namespaces(root, previous_result):
    """ Cleanup the namespaces of the root element. This should always be used at the
        end of a transformation when elements' namespaces have been changed. """
    etree.cleanup_namespaces(root)
    return previous_result


@export
def clear_attributes(element, previous_result):
    """ Deletes all attributes of an element. """
    element.attrib.clear()
    return previous_result


@export
@singleton_handler
def concatenate(*parts):
    """ Concatenate the given parts which may be lists or strings as well as callables
        returning such. """

    def handler(transformation) -> str:
        result = ''
        for part in parts:
            if callable(part):
                _part = part(transformation)
            elif isinstance(part, (str, List)):
                _part = part
            else:
                raise RuntimeError(f'Unhandled type: {type(part)}')
            result += _part
        return result

    return handler


@export
@singleton_handler
def debug_dump_document(name='tree'):
    """ Dumps all contents of the element referenced by ``name`` from the
        :attr:`inxs.Transformation._available_symbols` to the log at info level. """

    def handler(transformation):
        try:
            nfo(etree.tounicode(transformation._available_symbols[name]))
        except KeyError:
            nfo(f"No symbol named '{name}' found.")
        return transformation.states.previous_result

    return handler


@export
@singleton_handler
def debug_message(msg):
    """ Logs the provided message at info level. """

    def handler(previous_result):
        nfo(msg)
        return previous_result

    return handler


@export
@singleton_handler
def debug_symbols(*names):
    """ Logs the representation strings of the objects referenced by ``names`` in
        :attr:`inxs.Transformation._available_symbols` at info level. """

    def handler(transformation):
        for name in names:
            nfo(f'symbol {name}: {transformation._available_symbols[name]!r}')
        return transformation.states.previous_result

    return handler


# REMOVE?
@export
def drop_siblings(left_or_right):
    """ Removes all elements ``left`` or ``right`` of the processed element depending
        which keyword was given. The same is applied to all ancestors. Think of it like
        cutting a hedge from one side. It can be used as a processing step to strip the
        document to a chunk between two elements that don't have the same parent node.
    """
    if left_or_right == 'left':
        preceding = True
    elif left_or_right == 'right':
        preceding = False
    else:
        raise RuntimeError("'left_or_right' must be 'left' or …")

    def processor(element):
        if lxml_utils.is_root_element(element):
            return
        lxml_utils.remove_elements(*element.itersiblings(preceding=preceding))
        parent = element.getparent()
        if parent is not None:
            processor(parent)

    return processor


@export
def extract_text(include_tail: bool = False, reduce_whitespace: bool = True):
    """ Returns the extracted text by :func:`~inxs.lxml_utils.extract_text`. See its
        docs regarding possible keyword arguments. """

    def handler(element):
        return lxml_utils.extract_text(
            element, include_tail=include_tail, reduce_whitespaces=reduce_whitespace
        )

    return handler


@export
def f(func, *args, **kwargs):
    """ Wraps the callable ``func`` which will be called as ``func(*args, **kwargs)``,
        the function and any argument can be given as :func:`inxs.Ref`. """

    def wrapper(transformation):
        if is_Ref(func):
            _func = func(transformation)
        else:
            _func = func
        _args = ()
        for arg in args:
            if is_Ref(arg):
                _args += (arg(transformation),)
            else:
                _args += (arg,)

        _kwargs = resolve_Ref_values_in_mapping(kwargs, transformation)

        return _func(*_args, **_kwargs)

    return wrapper


@export
@singleton_handler
def get_attribute(name):
    """ Gets the value of the element's attribute named ``name``. """

    def evaluator(element):
        return element.attrib.get(name)

    return evaluator


@export
def get_localname(element):
    """ Gets the element's local tag name. """
    return etree.QName(element).localname


@export
def get_tail(element):
    """ Returns the tail of the matched element. """
    return element.tail


@export
def get_text(element):
    """ Returns the text of the matched element. """
    return element.text


@export
@singleton_handler
def get_variable(name):
    """ Gets the object referenced as ``name`` from the :term:`context`. It is then
        available as symbol ``previous_result``. """

    def handler(context):
        return dot_lookup(context, name)

    return handler


@export
def has_attributes(element, _):
    """ Returns ``True`` if the element has attributes. """
    return bool(element.attrib)


@export
def has_children(element, _):
    """ Returns ``True`` if the element has descendants. """
    return bool(len(element))


@export
@singleton_handler
def has_matching_text(pattern):
    """ Returns ``True`` if the element has a text that matches the provided
        ``pattern``. """
    pattern = re.compile(pattern)

    def evaluator(element, _):
        return element.text is not None and pattern.match(element.text)

    return evaluator


@export
def has_tail(element, _):
    """ Returns ``True`` if the element has a tail. """
    return bool(element.tail)


@export
def has_text(element, _):
    """ Returns ``True`` if the element has text content. """
    return bool(element.text)


@export
def init_elementmaker(name: str = 'e', **kwargs):
    """ Adds a :class:`lxml.builder.ElementMaker` as ``name`` to the context.
        ``kwargs`` for its initialization can be passed. """
    if 'namespace' in kwargs and 'nsmap' not in kwargs:
        kwargs['nsmap'] = {None: kwargs['namespace']}

    def wrapped(context, previous_result):
        setattr(context, name, builder.ElementMaker(**kwargs))
        return previous_result

    return wrapped


@export
@singleton_handler
def insert_fontawesome_icon(name: str, position: str, spin: bool = False):
    """ Inserts the html markup for an icon from the fontawesome set with the given
        ``name`` at ``position`` of which only ``after`` is implemented atm.

        It employs semantics for Font Awesome 5. """
    def after_handler(element):
        classes = f'fas fa-{name}'
        if spin:
            classes += ' fa-spin'
        element.append(html_builder.I(html_builder.CLASS(classes)))

    return {
        'after': after_handler,
    }[position]


@export
def join_to_string(separator: str = ' ', symbol='previous_result'):
    """ Joins the object referenced by ``symbol`` around the given
        ``separator`` and returns it. """

    def handler(transformation):
        return separator.join(transformation._available_symbols[symbol])

    return handler


@export
def lowercase(previous_result):
    """ Processes ``previous_result`` to be all lower case. """
    return previous_result.lower()


@export
def make_element(tag, namespace_s=None, attributes=None, text=None):
    """ This handler creates an empty element with the given ``tag``. The tag can
        have a prefix. If ``namespace_s`` is ``None`` the namespace mapping of the
        :term:`transformation root` is used as context. If given as :term:`mapping`,
        this is used as context. It can also be provided as string, which is then used
        as default namespace. """

    def handler(transformation, nsmap):
        if is_Ref(tag):
            _tag = tag(transformation)
        else:
            _tag = tag

        if namespace_s is None:
            _namespace_s = nsmap
        elif is_Ref(namespace_s):
            _namespace_s = namespace_s(transformation)
        else:
            _namespace_s = namespace_s

        if attributes is None:
            extra = {}
        else:
            extra = resolve_Ref_values_in_mapping(attributes, transformation)

        if isinstance(_namespace_s, str):
            result = etree.Element('{' + _namespace_s + '}' + _tag, **extra)
        else:
            if ':' in _tag:
                prefix, _tag = _tag.split(':', 1)
                _tag = '{' + _namespace_s[prefix] + '}' + _tag
            result = etree.Element(_tag, nsmap=_namespace_s, **extra)

        if is_Ref(text):
            _text = text(transformation)
        else:
            _text = text
        result.text = _text

        return result

    return handler


@export
@singleton_handler
def merge(src='previous_result', dst='root'):
    """ A wrapper around :func:`inxs.lxml_util.merge_nodes` that passes the objects
        referenced by ``src`` and ``dst``. """

    def handler(transformation):
        _src = transformation._available_symbols[src]
        _dst = transformation._available_symbols[dst]
        assert etree.QName(_src).text == etree.QName(_dst).text, \
            f'{etree.QName(_src).text} != {etree.QName(_dst).text}'
        lxml_utils.merge_nodes(_src, _dst)

    return handler


@export
@singleton_handler
def pop_attribute(name: str):
    """ Pops the element's attribute named ``name``. """

    def handler(element) -> str:
        return element.attrib.pop(name)

    return handler


@export
@singleton_handler
def pop_attributes(*names: str, ignore_missing=False):
    """ Pops all attributes with name from ``names`` and returns a mapping with names
        and values. When ``ignore_missing`` is ``True`` ``KeyError`` exceptions pass
        silently. """
    handlers = {x: pop_attribute(x) for x in names}
    del names

    def handler(element) -> Dict[str, str]:
        result = {}
        for name, _handler in handlers.items():
            try:
                result[name] = _handler(element)
            except KeyError:
                if not ignore_missing:
                    raise
        return result

    return handler


@export
def prefix_attributes(prefix: str, *attributes: str):
    """ Prefixes the ``attributes`` with ``prefix``. """
    return rename_attributes({x: prefix + x for x in attributes})


@export
@singleton_handler
def put_variable(name, value=Ref('previous_result')):
    """ Puts ``value``as ``name`` to the :term:`context` namespace, by default the
        value is determined by a :func:`inxs.Ref` to ``previous_result``. """

    def ref_handler(transformation):
        setattr(transformation.context, name, value(transformation))
        return transformation.states.previous_result

    def ref_handler_dot_lookup(transformation):
        setattr(dot_lookup(transformation.context, name), value(transformation))
        return transformation.states.previous_result

    def simple_handler(transformation):
        setattr(transformation.context, name, value)
        return transformation.states.previous_result

    def simple_handler_dot_lookup(transformation):
        setattr(dot_lookup(transformation.context, name), value)
        return transformation.states.previous_result

    if is_Ref(value):
        if '.' in name:
            return ref_handler_dot_lookup
        return ref_handler
    elif '.' in name:
        return simple_handler_dot_lookup
    else:
        return simple_handler


@export
def remove_element(element):  # REMOVE?
    """ A very simple handler that just removes an element from a tree. """
    lxml_utils.remove_elements(element)


@export
@singleton_handler
def remove_elements(references, keep_children=False, preserve_text=False,
                    preserve_tail=False,
                    clear_ref=True):
    """ Removes all elements from the document that are referenced in a list that is
        available as ``references``. ``keep_children`` and ``preserve_texte`` are
        passed to
        :func:`inxs.lxml_utils.remove_element`. The reference list is cleared
        afterwards if
        ``clear_ref`` is ``True``. """

    def handler(transformation):
        elements = transformation._available_symbols[references]
        lxml_utils.remove_elements(*elements, keep_children=keep_children,
                                   preserve_text=preserve_text,
                                   preserve_tail=preserve_tail)
        if clear_ref:
            elements.clear()
        return transformation.states.previous_result

    return handler


@singleton_handler
def _rename_attributes(translation_map: Tuple[Tuple[str, str], ...]) -> Callable:
    def handler(element) -> None:
        for _from, to in translation_map:
            element.attrib[to] = element.attrib.pop(_from)

    return handler


@export
def rename_attributes(translation_map: Mapping[str, str]) -> Callable:
    """ Renames the attributes of an element according to the provided
        ``translation_table`` that consists of old name keys and new name values. """
    return _rename_attributes(tuple((k, v) for k, v in translation_map.items()))


@export
@singleton_handler
def replace_text(old: Union[str, Callable], new: Union[str, Callable],
                 text=True, tail=False) -> Callable:
    """ Replaces the substring ``old`` in an element's text and tail (depending on
        the boolean arguments with that name) with the string given as ``new``,
        both strings can
        be provided as references to a transformation's symbols. """

    # TODO input type specialized handlers
    def handler(element, transformation):
        _old = old(transformation) if is_Ref(old) else old
        _new = new(transformation) if is_Ref(new) else new
        if text and element.text:
            element.text = element.text.replace(_old, _new)
        if tail and element.tail:
            element.tail = element.tail.replace(_old, _new)
        return transformation.states.previous_result

    return handler


@export
@singleton_handler
def resolve_xpath_to_element(*names):
    """ Resolves the objects from the context (which are supposed to be XPath
        expressions) referenced by ``names`` with the *one* element that the XPaths
        yield or
        ``None``. This is useful when a copied tree is processed and 'XPath pointers'
        are passed to the
        :term:`context` when a :class:`inxs.Transformation` is called. """

    def resolver(context, transformation):
        for name in names:
            xpath = getattr(context, name)
            if not xpath:
                setattr(context, name, None)
                continue
            resolved_elements = transformation.xpath_evaluator(xpath)
            if not resolved_elements:
                setattr(context, name, None)
            elif len(resolved_elements) == 1:
                setattr(context, name, resolved_elements[0])
            else:
                raise RuntimeError(f'More than one element matched {xpath}')
        return transformation.states.previous_result

    return resolver


@export
@singleton_handler
def set_attribute(name, value=Ref('previous_result')):
    """ Sets an attribute ``name`` with ``value``. """

    def simple_handler(element, previous_result):
        element.attrib[name] = value
        return previous_result

    def resolving_handler(element, previous_result, transformation):
        element.attrib[name] = value(transformation)
        return previous_result

    if isinstance(value, str):
        return simple_handler
    elif is_Ref(value):
        return resolving_handler


@export
@singleton_handler
def set_localname(name):
    """ Sets the element's localname to ``name``. """

    def handler(element, previous_result):
        namespace = etree.QName(element).namespace
        if namespace is None:
            qname = etree.QName(name)
        else:
            qname = etree.QName(namespace, name)
        element.tag = qname.text
        return previous_result

    return handler


@export
@singleton_handler
def set_text(text=Ref('previous_result')):
    """ Sets the element's text to the one provided as ``text``, it can also be a
        :func:`inxs.Ref`."""

    def ref_handler(element, transformation):
        element.text = text(transformation)
        return transformation.states.previous_result

    def static_handler(element, previous_result):
        element.text = text
        return previous_result

    return ref_handler if is_Ref(text) else static_handler


@export
@singleton_handler
def sorter(name: str = 'previous_result', key: Callable = lambda x: x):
    """ Sorts the object referenced by ``name`` in the :term:`context` using ``key`` as
        :term:`key function`. """

    def handler(context):
        return sorted(getattr(context, name), key=key)

    return handler


@export
@singleton_handler
def strip_attributes(*names):
    """ Strips all attributes with the keys provided as ``names`` from the element. """

    def handler(element, previous_result):
        for name in names:
            element.attrib.pop(name, None)
        return previous_result

    return handler


@export
def strip_namespace(element, previous_result):
    """ Removes the namespace from the element.
        When used, :func:`cleanup_namespaces` should be applied at the end of the
        transformation. """
    element.tag = etree.QName(element).localname
    return previous_result


@export
def sub(*args, **kwargs):
    """ A wrapper around :func:`inxs.lxml_utils.subelement` for usage as
        :term:`handler function`. """
    return f(lxml_utils.subelement, *args, **kwargs)


@export
@singleton_handler
def text_equals(text):
    """ Tests whether the evaluated element's text matches ``text``. """

    def evaluator(element, _):
        return element.text == text

    return evaluator
