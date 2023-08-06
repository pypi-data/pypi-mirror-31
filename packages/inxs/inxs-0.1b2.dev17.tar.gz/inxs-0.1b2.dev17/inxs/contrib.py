""" This module contains transformations that are supposedly of common interest. """

from lxml import etree

from inxs import (
    TRAVERSE_DEPTH_FIRST, TRAVERSE_BOTTOM_TO_TOP, TRAVERSE_LEFT_TO_RIGHT, lib, utils,
    Not, Rule,
    SkipToNextElement, Transformation,
)

__all__ = []


# reduce_whitespaces


def _reduce_whitespace_handler(element):
    if element.text:
        element.text = utils.reduce_whitespaces(element.text, strip='')
    if element.tail:
        element.tail = utils.reduce_whitespaces(element.tail, strip='')


reduce_whitespaces = Transformation(
    Rule('*', _reduce_whitespace_handler)
)
"""
Normalizes any whitespace character of element's text and tail to a simple space and
reduces consecutives to one.
"""
__all__.append('reduce_whitespaces')


# remove_empty_elements


def _append_tail_to_previous_in_stream(element, skip_elements):
    if etree.QName(element).localname in skip_elements:
        raise SkipToNextElement
    if not element.tail:
        return
    previous = element.getprevious()
    if previous is None:
        element.getparent().text += element.tail
    elif previous.tail is None:
        previous.tail = element.tail
    else:
        previous.tail += element.tail


remove_empty_elements = Transformation(
    Rule(Not(lib.has_children, lib.has_text, lib.has_attributes, '/'),
         (_append_tail_to_previous_in_stream, lib.remove_element)),
    name='remove_empty_elements', context={'skip_elements': []},
    traversal_order=(
            TRAVERSE_DEPTH_FIRST | TRAVERSE_LEFT_TO_RIGHT | TRAVERSE_BOTTOM_TO_TOP
    )
)
"""
Removes elements without attributes, text, tail and children from the (sub-)tree.
"""
__all__.append('remove_empty_elements')
