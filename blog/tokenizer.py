import re
from collections import OrderedDict


class Tokenizer(object):

    types = OrderedDict([
        ("newline", re.compile("\n")),
        ("indentation", re.compile(" +")),
        ("section", re.compile(":")),
        ("list_item", re.compile("\-")),
        ("code_block", re.compile("`(.*)`", flags=re.DOTALL)),
        ("bold_toggle", re.compile("\*")),
        ("link_start", re.compile("\[")),
        ("link_end", re.compile("\]")),
        ("word", re.compile(".+"))
    ])

    def __init__(self):
        pass

    def determine_type(self, word):
        for key, value in Tokenizer.types.items():
            if re.match(value, word) is not None:
                return key
        return "word"

    def tokenize(self, text):
        tokens = []
        word = ""
        line_start = True
        in_code = False

        for c in text:
            if c == '`':
                if not in_code:
                    if len(word) > 0:
                        tokens.append((word, self.determine_type(word)))
                        word = ""
                in_code = not in_code
                word += c
            elif in_code:
                word += c
            elif c == " ":
                if line_start:
                    word += " "
                elif len(word) > 0:
                    tokens.append((word, self.determine_type(word)))
                    word = ""
            elif c in ['[', ']', '*', '-', ':', '\n']:
                if len(word) > 0:
                    tokens.append((word, self.determine_type(word)))
                    word = ""
                tokens.append((c, self.determine_type(c)))
                line_start = False
                if c == '\n':
                    line_start = True
            else:
                if line_start is True and len(word) > 0:
                    tokens.append((word, self.determine_type(word)))
                    word = ""
                line_start = False
                word += c
        return tokens
