# Argument Noun
#
# Sublime Text plugin that extends Vintage mode with support
# for treating function arguments (including parameters) as
# an 'a' text noun.
#
# Usage:
#   delete an argument by pressing "daa"
#   change inner argument by pressing "cia"
#   select inner argument by pressing "via"
#
# Copyright (c) 2013 Nils Liberg
# License: MIT License

import sublime, sublime_plugin
import re

def transform_selection_regions(view, f, **kwargs):
    sel = view.sel()
    new_sel = [f(r, **kwargs) for r in sel]
    sel.clear()
    for r in new_sel:
        sel.add(r)

def remove_inner_parenthesis(s):
    ''' removes any inner parenthesis and also cuts off the string at the
        right hand side when the first non-matched ')' is reached '''
    characters = []
    num_lparen = 0
    for c in s:
        if c == '(':
            num_lparen += 1
        elif c == ')':
            num_lparen -= 1
            # stop if end of parameter list reached
            if num_lparen < 0:
                break
        if num_lparen:
            characters.append('_')
        else:
            characters.append(c)
    return ''.join(characters)

def remove_tail(s):
    # remove all characters after semicolon
    s = re.sub(r'(?s);.*', '', s)

    # if there are two adjacent identifiers with only whitespace containing
    # a newline inbetween, assume a right parenthesis is missing after
    # the first identifier and insert one (while preserving character offsets)
    def repl_func(m):
        non_identifiers = [
            'mod', 'div', 'and', 'or', 'xor', 'not', 'if',
            'unless', 'else', 'const',
        ]
        if (m.group(1) not in non_identifiers and m.group(3) not in non_identifiers
              and '\n' in m.group(2) or '\n' in m.group(2)):
            return ''.join([m.group(1), ')', m.group(2)[1:], m.group(3)])
        else:
            return m.group(0)
    s = re.sub(r'([a-zA-Z_0-9]+)(\s+)([a-zA-Z_0-9])', repl_func, s)

    return s

class ViExpandToArguments(sublime_plugin.TextCommand):

    def run(self, edit, outer=False, repeat=1, multiline=True):
        for i in range(repeat):
            transform_selection_regions(
                self.view, self.expand_region_to_argument,
                outer=outer, multiline=multiline
            )

    def expand_region_to_argument(self, region, outer=False, multiline=True):
        # determine where the cursor is placed and what surrounding
        # text fragment region to consider
        pt = region.a
        r = self.view.line(pt)
        if multiline:
            last_line = self.view.rowcol(self.view.size()-1)[0]
            line_no = self.view.rowcol(pt)[0]
            # make the region of interest span 10 lines backwards and forwards
            l_beg, l_end = (max(0,         line_no-10),
                            min(last_line, line_no+10))
            r = self.view.line(self.view.text_point(l_beg, 0)).cover(
                self.view.line(self.view.text_point(l_end, 0)))
            # limit the region just in case the lines are very long
            r = r.intersection(sublime.Region(pt - 4000, pt + 4000))

        # extract the surrounding text and determine the offset
        # from the start of it where the cursor is placed
        s = self.view.substr(r)
        cursor_offset = pt - r.a

        # replace literal strings by placeholders so that offsets are
        # preserved but parenthesis and commmas within strings do not
        # affect the later steps
        s = s.replace("\\'", '_').replace('\\"', '!')  # remove string escape codes
        s = re.sub(r'(?s)""".*?"""', lambda m: '!' * len(m.group(0)), s)
        s = re.sub(r"(?s)'''.*?'''", lambda m: '!' * len(m.group(0)), s)
        s = re.sub(r'".*?"', lambda m: '!' * len(m.group(0)), s)
        s = re.sub(r"'.*?'", lambda m: '!' * len(m.group(0)), s)

        # find offsets to the start of all non-empty argument lists that
        # precede the cursor
        offsets = [m.start(1) for m in re.finditer(
            r'(?x)[a-zA-Z0-9_]+[!?]? \s* \( ( (?!\s*\))[^)] )', s)
            if m.start(1) <= cursor_offset]
        if offsets:
            # pick the last argument list offset
            offset = offsets[-1]
            args_str = s[offset:]

            # trim the right part of the string at semicolons and at suspected
            # missing right parenthesis in order to decrease the risk that we
            # we go too far to the right.
            args_str = remove_tail(args_str)

            # remove any inner parenthesis: "a*min(b, c), d" ==> "a*min______, d"
            args_str = remove_inner_parenthesis(args_str)

            # find arguments by splitting at commas
            args = re.findall(r'[^,]+,?\s*|,\s*', args_str)

            # find the argument that matches the cursor offset
            i = offset
            for arg_i, arg in enumerate(args):
                if cursor_offset <= i + len(arg.rstrip(', ')):
                    # create a region that covers this argument
                    if not outer:
                        arg = arg.rstrip(', \t\r\n')
                    a = region.a - (cursor_offset - i)
                    b = a + len(arg)

                    # if the argument is the last one and outer mode is on,
                    # expand to the left to cover any whitespace or commas
                    if outer and arg_i == len(args)-1: #self.view.substr(b) == ')':
                        while self.view.substr(a - 1) in ', \t\r\n':
                            a -= 1

                    return sublime.Region(a, b)
                else:
                    i += len(arg)

        return region
