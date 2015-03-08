class Parser(object):

    def __init__(self, tokens):
        self.default = {}
        self.default["each_indentation"] = 2
        self.default["header_level"] = 2
        self.indentation = 0
        self.header_level = self.default["header_level"]

        self.tokens = tokens
        self.tokens_pos = 0
        self.in_list = False
        self.last_newline = False
        self.output = ""
        self.attributes = {}

    def parse(self):
        try:
            while True:
                self.parse_section()
        except IndexError as e:
            pass

    def parse_section(self):
        name = []
        found = False
        while True:
            if self.match_token('section'):
                found = True
                break
            elif self.match_token('newline'):
                if self.last_newline:
                    self.output += "<br>"
                    self.last_newline = False
                else:
                    self.last_newline = True
                found = False
                break
            self.last_newline = False
            name.append(self.peek_token())
            self.next_token()
        self.next_token()
        if found:
            if not self.match_token('newline'):
                value = []
                while True:
                    if self.match_token('newline'):
                        break
                    value.append(self.peek_token())
                    self.next_token()
                self.attributes["_".join([a[0] for a in name])] = "".join([a[0] for a in value])
                return
            self.output += "<h{0}>{1}</h{0}>".format(self.header_level,
                                            " ".join([a[0] for a in name]))
            self.header_level += 1;
            self.consume_token('newline')
            indentation = self.increase_indentation()
            while self.has_indentation(indentation):
                self.parse_section()
            self.header_level -= 1
            self.decrease_indentation()
        else:
            self.parse_line(name)

    def parse_formattings(self, line):
        in_bold = False
        in_link = False
        in_link_name = False
        space_pls = True
        for ind, token in enumerate(line):
            if in_link_name:
                self.output += token[0] + "\">"
                in_link_name = False
                space_pls = False
            elif token[1] == 'bold_toggle':
                if in_bold:
                    self.output += "</strong>"
                else:
                    if space_pls and ind > 0:
                        self.output += " "
                    self.output += "<strong>"
                in_bold = not in_bold
                space_pls = not in_bold
            elif token[1] == 'link_start':
                if space_pls and ind > 0:
                    self.output += " "
                in_link = True
                in_link_name = True
                self.output += "<a href=\""
            elif token[1] == 'link_end':
                in_link = False
                self.output += "</a>"
            elif token[1] == 'code_block':
                self.output += "<code>{}</code>".format(token[0][1:-1])
            else:
                if space_pls and ind > 0:
                    self.output += " "
                self.output += token[0]
                space_pls = True


    def parse_line(self, line):
        if len(line) == 0:
            return
        while len(line) > 0 and line[0][1] == 'indentation':
            line.pop(0)
        if line[0][1] == 'list_item':
            line.pop(0)
            self.ensure_list()
            self.output += "<li>"
            self.parse_formattings(line)
            self.output += "</li>\n"
        else:
            self.kill_list()
            self.parse_formattings(line)
            self.output += "\n"

    def ensure_list(self):
        if not self.in_list:
            self.output += "<ul>\n"
            self.in_list = True

    def kill_list(self):
        if self.in_list:
            self.output += "</ul>\n"
            self.in_list = False

    def increase_indentation(self):
        self.indentation += self.default["each_indentation"]
        return self.indentation

    def decrease_indentation(self):
        self.indentation -= self.default["each_indentation"]
        assert self.indentation >= 0

    def has_indentation(self, amount):
        if self.match_token('indentation'):
            tru = len(self.peek_token()[0]) >= amount
            if tru:
                self.next_token()
            return tru
        return self.match_token('newline')

    def consume_token(self, type):
        token = self.peek_token()
        if self.match_token(type):
            self.next_token()
            return token
        else:
            raise Exception("Unexpected token encountered", token)

    def match_token(self, type):
        return self.peek_token()[1] == type

    def peek_token(self):
        return self.tokens[self.tokens_pos]

    def next_token(self):
        self.tokens_pos += 1
