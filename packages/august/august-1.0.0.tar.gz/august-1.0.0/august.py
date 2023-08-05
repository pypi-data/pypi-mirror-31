#!/usr/bin/env python3
import collections
import math
import re
import textwrap
from typing import Callable, List, MutableMapping, Union

import bs4

WHITESPACE_PATTERN = re.compile(r'\s+', re.MULTILINE)

StrMap = MutableMapping[str, str]
SoupElem = Union[bs4.BeautifulSoup, bs4.Tag]
InlineFunc = Callable[[str, StrMap, StrMap], str]
SizeHint = collections.namedtuple(
    'SizeHint', ['length', 'max_width', 'height'])


class Node:
    """Basic element of the DOM

    All nodes are either text nodes or block elements
    """
    def __str__(self):
        raise NotImplementedError()

    def size_hint(self) -> SizeHint:
        raise NotImplementedError


class NodeList(list):
    """A list of sibling nodes

    This mainly exists to handle some funny whitespace rules for when
    text nodes are beside each other
    """

    def trimmed(self) -> str:
        had_whitespace = False
        for node in self:
            text = str(node)
            if had_whitespace:
                yield text.lstrip()
            else:
                yield text
            had_whitespace = text != text.rstrip()

    def block_clean(self):
        had_whitespace = True
        last_idx = len(self) - 1
        for idx, node in enumerate(self):
            if isinstance(node, Text):
                if node.text.strip(' ') == '':
                    del self[idx]
                    if idx == last_idx:
                        self.block_clean()
                    continue
                if had_whitespace:
                    node.text = node.text.lstrip(' ')
                if idx == last_idx:
                    node.text = node.text.rstrip(' ')
                had_whitespace = node.text != node.text.lstrip(' ')
            else:
                had_whitespace = True

    def __str__(self):
        return ''.join(self.trimmed())


class Text(Node):

    def __init__(self, text: str):
        self.text = text
        self.empty = text.strip() == ''

    @staticmethod
    def from_text(text):
        text = WHITESPACE_PATTERN.sub(' ', text)
        return Text(text)

    @staticmethod
    def from_nodes(children: NodeList):
        return Text(str(children))

    def is_empty(self):
        return self.empty

    def __str__(self):
        return self.text

    def size_hint(self):
        lines = self.text.split('\n')
        max_width = max(len(line) for line in lines)
        length = len(self.text)
        return SizeHint(length, max_width, len(lines))


def formatted_element(fmt: str) -> InlineFunc:
    def inner(text: str, _attrs: StrMap, _ctx: StrMap) -> str:
        return fmt.format(text)
    return inner


def s_element(text: str, _attrs: StrMap, _ctx: StrMap) -> str:
    if len(text) > 10:
        wordcount = len(text.split())
        suffix = wordcount * '^W'
    else:
        suffix = len(text) * '^H'
    return text + suffix


def a_element(text: str, attrs: StrMap, _ctx: StrMap) -> str:
    href = attrs.get('href')
    if href is None:
        return text
    scheme = href.split(':')[0]
    if scheme not in {'mailto', 'http', 'https'}:
        return text
    if scheme == 'mailto':
        return '{} <{}>'.format(text, href[7:])
    return '{} ({})'.format(text, href)


def abbr_element(text: str, attrs: StrMap, context: StrMap) -> str:
    title = attrs.get('title')
    if title is None:
        return text
    context_key = 'abbr ' + text
    if context.get(context_key) == title:
        return text
    context[context_key] = title
    suffix = ' ({})'.format(title)
    return text + suffix


def img_element(_text: str, _attrs: StrMap, _context: StrMap) -> str:
    return _attrs.get('alt', '')


def br_element(_text: str, _attrs: StrMap, _context: StrMap) -> str:
    return '\n'


class BlockElement(Node):

    _wrapper = textwrap.TextWrapper(
        expand_tabs=False, replace_whitespace=False)
    LINE_SEP = '\n'
    LINE_PREFIX = ''
    BLOCK_SEP = '\n\n'

    def __init__(self, children: NodeList, _attrs: StrMap):
        idx = len(children) - 1
        last_idx = idx
        while idx > 0:
            child = children[idx]
            if isinstance(child, Text):
                if idx == last_idx:
                    child.text = child.text.rstrip(' ')
                if isinstance(children[idx-1], Text):
                    nodes = NodeList((children[idx-1], child))
                    new = Text.from_nodes(nodes)
                    children[idx-1] = new
                    del children[idx]
                elif child.is_empty():
                    del children[idx]
            idx -= 1
        if idx == 0:
            child = children[0]
            if isinstance(child, Text):
                child.text = child.text.lstrip(' ')
                if child.is_empty():
                    del children[0]
        max_width = 0
        height = 0
        for child in children:
            sub_size_hint = child.size_hint()
            max_width = max(max_width, sub_size_hint.max_width)
            height = max(height, sub_size_hint.height)

        self.children = children
        self._size_hint = SizeHint(max_width, max_width, height)

    def get_first_line_prefix(self):
        return self.LINE_PREFIX

    def get_next_line_prefix(self):
        return self.LINE_PREFIX

    def block_text(self, width: int) -> str:
        self._wrapper.width = width
        first_line_prefix = self.get_first_line_prefix()
        next_line_prefix = self.get_next_line_prefix()
        sub_width = width - len(first_line_prefix)
        sep = self.LINE_SEP + next_line_prefix
        blocks = []
        last_inline_text = ''
        had_whitespace = True
        for child in self.children:
            if isinstance(child, BlockElement):
                if last_inline_text.strip() != '':
                    lines = last_inline_text.split(self.LINE_SEP)
                    wrapped_lines = (nl for line in lines
                                     for nl in self._wrapper.wrap(line))
                    blocks.append(sep.join(wrapped_lines))
                block_lines = child.block_text(sub_width).split(self.LINE_SEP)
                blocks.append(first_line_prefix + sep.join(block_lines))
                last_inline_text = ''
                had_whitespace = True
            else:
                text = str(child)
                if had_whitespace:
                    text = text.lstrip(' ')
                last_inline_text += text
                had_whitespace = text != text.rstrip(' ')
        if last_inline_text.strip() != '':
            lines = last_inline_text.rstrip(' ').split(self.LINE_SEP)
            wrapped_lines = []
            for line in lines:
                if line == '':
                    wrapped_lines.append('')
                else:
                    for nl in self._wrapper.wrap(line):
                        wrapped_lines.append(nl)
            blocks.append(first_line_prefix + sep.join(wrapped_lines))

        return self.BLOCK_SEP.join(blocks)

    def __str__(self):
        return ''.join(str(n) for n in self.children)

    def size_hint(self):
        return self._size_hint


class BlockquoteElement(BlockElement):

    LINE_PREFIX = '> '
    BLOCK_SEP = '\n>\n'


class UlElement(BlockElement):
    BLOCK_SEP = '\n'


class OlElement(UlElement):

    def __init__(self, children: NodeList, attrs: StrMap):
        super().__init__(children, attrs)
        items = [c for c in children if isinstance(c, LiElement)]
        count = len(items)
        count_length = len(str(count))
        for idx, item in enumerate(items):
            item.set_ordering(idx+1, count_length)


class LiElement(BlockElement):

    def __init__(self, children: NodeList, attrs: StrMap):
        super().__init__(children, attrs)
        self.ordered = False
        self.count = 0
        self.count_length = 0

    def set_ordering(self, count, count_length):
        self.ordered = True
        self.count = count
        self.count_length = count_length

    def get_first_line_prefix(self):
        if self.ordered:
            return '{:>{length}}. '.format(
                self.count, length=self.count_length)
        return '* '

    def get_next_line_prefix(self):
        if self.ordered:
            return ' ' * (self.count_length+2)
        return '  '


class HrElement(BlockElement):

    def block_text(self, width: int):
        return '-' * width

    def size_hint(self):
        return SizeHint(79, 79, 1)


class HeaderElement(BlockElement):

    def block_text(self, width: int):
        return super().block_text(width).upper()


class TableElement(BlockElement):

    BLOCK_SEP = '\n'

    def __init__(self, children: NodeList, attrs: StrMap):
        for idx, child in enumerate(children):
            if not isinstance(child, TrElement):
                tr_children = NodeList((child,))
                tr_children.block_clean()
                if tr_children:
                    children[idx] = TrElement(tr_children, {})
                else:
                    del children[idx]
        super().__init__(children, attrs)

    @staticmethod
    def recalculate_widths(widths: List[int], max_width) -> List[int]:
        len_widths = len(widths)
        len_sep = len(TrElement.ROW_SEP)
        usable_max = max_width - len_sep * (len_widths - 1)
        desired_max = sum(widths)
        if usable_max >= desired_max:
            return widths
        ratio = usable_max / desired_max
        float_widths = sorted(
            ((idx, width * ratio) for (idx, width) in enumerate(widths)),
            key=lambda key: key[1] % 1)
        balance = 0
        start_idx = 0
        end_idx = len_widths - 1
        for _idx in range(len_widths):
            if balance > 0:  # remove from bottom
                idx = start_idx
                start_idx += 1
            else:  # add to top
                idx = end_idx
                end_idx -= 1
            width_idx, width_value = float_widths[idx]
            if balance > 0:  # remove from bottom
                new_width = math.floor(width_value)
            else:  # add to top
                new_width = math.ceil(width_value)
            balance += new_width - width_value
            width_value = new_width
            float_widths[idx] = width_idx, width_value
        return [i[1] for i in
                sorted(float_widths, key=lambda k: k[0])]

    def column_widths(self) -> List[int]:
        widths = []
        for child in self.children:
            if isinstance(child, TrElement):
                widths_len = len(widths)
                for idx, width in enumerate(child.column_widths()):
                    if idx < widths_len:
                        widths[idx] = max(widths[idx], width)
                    else:
                        widths.append(width)
        return widths

    def block_text(self, width: int):
        col_widths = self.recalculate_widths(
            self.column_widths(), width)
        blocks = []
        for child in self.children:
            assert isinstance(child, TrElement)
            block = child.block_row(col_widths)
            blocks.append(block)
        return self.BLOCK_SEP.join(blocks)


class TrElement(BlockElement):

    ROW_SEP = '  '

    def column_widths(self) -> List[int]:
        for child in self.children:
            yield child.size_hint().max_width

    def block_row(self, column_widths: List[int]):
        # list of lists of lines
        cells = []
        for idx, child in enumerate(self.children):
            width = column_widths[idx]
            if isinstance(child, BlockElement):
                lines = child.block_text(width).split(self.LINE_SEP)
            else:
                self._wrapper.width = width
                lines = self._wrapper.wrap(str(child))
            lines = [line.ljust(width) for line in lines]
            cells.append(lines)
        height = max(len(cell) for cell in cells)
        for idx, cell in enumerate(cells):
            cell_height = len(cell)
            if height > cell_height:
                cells[idx] = cell + [''] * (height-cell_height)
        row_lines = (self.ROW_SEP.join(cell).rstrip() for cell in zip(*cells))
        return self.LINE_SEP.join(row_lines)


class Document(BlockElement):
    pass


# Mapping[str, InlineFunc]
INLINE_TAGS = {
    'b': formatted_element('*{}*'),
    'strong': formatted_element('*{}*'),
    'i': formatted_element('/{}/'),
    'em': formatted_element('/{}/'),
    'u': formatted_element('_{}_'),
    's': s_element,
    'a': a_element,
    'abbr': abbr_element,
    'img': img_element,
    'br': br_element,
}

# Mapping[str, BlockElement]
BLOCK_TAGS = {
    'p': BlockElement,
    'div': BlockElement,
    'blockquote': BlockquoteElement,
    'h1': HeaderElement,
    'h2': HeaderElement,
    'h3': HeaderElement,
    'h4': HeaderElement,
    'h5': HeaderElement,
    'h6': HeaderElement,
    'hr': HrElement,
    'table': TableElement,
    'tr': TrElement,
    'th': HeaderElement,
    'td': BlockElement,
    'ul': UlElement,
    'ol': OlElement,
    'li': LiElement,
}


def convert(html: str, width: int = 79) -> str:
    soup = bs4.BeautifulSoup(html, 'html.parser')
    body = soup.find('body')
    context = {}
    if body is None:
        body = soup
    nodes = soup_to_nodes(body, context)
    doc = Document(nodes, {})
    return doc.block_text(width)


def soup_to_nodes(soup: SoupElem, context: dict) -> NodeList:
    result = NodeList()
    for elem in soup:
        if isinstance(elem, bs4.NavigableString):
            result.append(Text.from_text(elem))
        elif isinstance(elem, bs4.Tag):
            children = soup_to_nodes(elem, context)
            if elem.name in INLINE_TAGS:
                text = INLINE_TAGS[elem.name](
                    str(children), elem.attrs, context)
                result.append(Text(text))
            elif elem.name in BLOCK_TAGS:
                children.block_clean()
                parent = BLOCK_TAGS[elem.name](children, elem.attrs)
                result.append(parent)
            else:
                for child in children:
                    result.append(child)
    return result


if __name__ == "__main__":
    import optparse
    import sys
    options = optparse.OptionParser(
        description='HTML->text converter. HTML in stdin; text in stdout.'
    )
    options.add_option(
        '--width', dest='width', action='store', type='int', default='79',
        help='Word wrapping width')
    (opts, _args) = options.parse_args()
    print(convert(sys.stdin.read(), opts.width))
