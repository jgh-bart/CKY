# CKY algorithm, adapted for arithmetic

class CKY_rule:
    # rule object, initiated with LHS symbol as string
    # and RHS symbols as list of strings
    def __init__(self, left, right):
        self.left  = left
        self.right = right
    
    def rule_match(self, symbol_list):
        if symbol_list == self.right:
            return True
        else:
            return False
    
    # if rule not in Chomsky Normal Form (more than 2 terms on RHS), rewrite rule in CNF
    # by recursion: returns set of rewritten rules
    def cnf_rewrite(self, index=0):
        if len(self.right) <= 2:
            return set([self])
        else:
            new_symbol = 'x' + str(index)
            rule_1 = CKY_rule(self.left, [self.right[0], new_symbol])
            rule_2 = CKY_rule(new_symbol, self.right[1:])
            return set([rule_1]).union(rule_2.cnf_rewrite(index + 1))
    
    def printout(self):
        print self.left.ljust(5), "->", self.right

class CKY_table:
    # CKY table represented as a dictionary, keys (i,j)
    # i: span length, j: index of span start
    # each cell holding a (by default empty) list of CKY traces
    def __init__(self, sentence):
        self.sentence = sentence
        self.len   = len(self.sentence)
        self.table = {}
        for i in range(1, self.len + 1):
            for j in range(self.len - i + 1):
                self.table[(i,j)] = []
    
    def get_cell(self, i, j):
        return self.table[(i,j)]
    
    def add_symbol(self, i, j, symbol, trace_text, value=None):
        self.table[(i,j)].append(CKY_trace(symbol, trace_text, value))
    
    def printout(self, cell_width):
        print 'CKY TABLE'
        for i in range(self.len, 0, -1):
            row_string = ''
            for j in range(self.len - i + 1):
                row_string += ' ' + str(j) + '[' + ','.join([trace.symbol for trace in self.table[(i,j)]]).ljust(cell_width) + ']'
            print i, ':', row_string
        # print sentence
        sentence_print = ''
        for word in self.sentence:
            sentence_print += '|' + word.ljust(cell_width + 3)
        print 'SEN ', sentence_print

class CKY_trace:
    # trace object stored in CKY table,
    # with symbol and parse trace attributes, both strings
    # and (added for arithmetic) value attribute, float or bool, default None
    def __init__(self, symbol, trace_text, value=None):
        self.symbol     = symbol
        self.trace_text = trace_text
        self.value      = value

rules = set([CKY_rule('NUM', ['NUM', 'OP', 'NUM']),
            CKY_rule('BOOL', ['NUM', 'EQ', 'NUM'])])

print 'RULES'
for rule in rules:
    rule.printout()

lexicon = {}
for operator in ['+', '-', 'x', '/']:
    lexicon[operator] = 'OP'
for bool_operator in ['=', '<', '>']:
    lexicon[bool_operator] = 'EQ'

operator_bool_dict = {'+': (lambda x, y: x + y),
                      '-': (lambda x, y: x - y),
                      'x': (lambda x, y: x * y),
                      '/': (lambda x, y: x / y),
                      '=': (lambda x, y: True if x == y else False),
                      '<': (lambda x, y: True if x < y else False),
                      '>': (lambda x, y: True if x > y else False)}

# function to check if string is a number (from pythoncentral.io)
def is_number(num):
    try:
        float(num)
        return True
    except ValueError:
        pass
    return False

def cky_algorithm(sentence):
    sentence_len = len(sentence)
    cky = CKY_table(sentence)
    
    # symbols to numbers & operators (row 1)
    for w in range(sentence_len):
        if is_number(sentence[w]):
            symbol = 'NUM'
            value  = float(sentence[w])
        elif sentence[w] in lexicon:
            symbol = lexicon[sentence[w]]
            value  = sentence[w]
        else:
            print 'ERROR: neither number nor operator:', sentence[w]
            break
        trace_text = '[' + symbol + ' ' + sentence[w] + ']'
        cky.add_symbol(1, w, symbol, trace_text, value)
            
    print
    print 'ROW 1: NUMBERS & OPERATORS'
    cky.printout(7)

    # rows 2 upwards
    for span_len in range(2, sentence_len + 1):
        for pos in range(sentence_len - span_len + 1):
            for operator_pos in range(pos + 1, pos + span_len - 1):
                for trace_1 in cky.get_cell(operator_pos - pos, pos):
                    for trace_2 in cky.get_cell(1, operator_pos):
                        for trace_3 in cky.get_cell(pos + span_len - operator_pos - 1, operator_pos + 1):
                            for rule in rules:
                                if rule.rule_match([trace_1.symbol, trace_2.symbol, trace_3.symbol]):
                                    print
                                    rule.printout()
                                    print '(', span_len, pos, ')->(', operator_pos - pos, pos, ')(', 1, operator_pos, ')(', pos + span_len - operator_pos - 1, operator_pos + 1, ')'
                                    value = operator_bool_dict[trace_2.value](trace_1.value, trace_3.value)
                                    trace_text = '[' + rule.left + trace_1.trace_text + trace_2.trace_text + trace_3.trace_text + ']'
                                    print 'TRACE', trace_text
                                    print trace_1.value, trace_2.value, trace_3.value, '; VALUE:', value
                                    cky.add_symbol(span_len, pos, rule.left, trace_text, value)
                                    cky.printout(7)
    return cky.get_cell(sentence_len, 0)

def parse_tree_printout(parse_string, col_width):
    # set up empty table as nested list of empty strings,
    # height 2x bracket levels, width no. words
    word_count        = 0
    bracket_level     = 0
    max_bracket_level = 0
    brackets          = {'[': +1, ']': -1}
    for char in parse_string:
        if char in brackets:
            bracket_level += brackets[char]
            if bracket_level > max_bracket_level:
                max_bracket_level = bracket_level
        elif char == ' ':
            word_count += 1
    parse_table = []
    for n in range(2 * max_bracket_level):
        parse_table.append(word_count * [''])
    # work through parse string, left to right
    col = 0
    row = 0
    idx = 1
    while idx < len(parse_string):
        if row < 0:
            break
        if parse_string[idx] in brackets:
            # row +2 for [, row -2 for ]
            row += 2 * brackets[parse_string[idx]]
            # across to first col empty below current row
            for x_row in parse_table[row:]:
                while len(x_row[col]) > 0 and col < word_count - 1:
                    col += 1
            idx += 1
        elif parse_string[idx] == ' ':
            # word to bottom row of table, in current col
            idx += 1
            word = parse_string[idx:idx + parse_string[idx:].find(']')]
            parse_table[-1][col] = word
            # | from PoS to word, in same col
            for pipe_row in range(row + 1, len(parse_table) - 1):
                parse_table[pipe_row][col] = '|'
            idx += len(word)
        else:
            # add symbol to current cell
            end_idx = idx
            while parse_string[end_idx] not in ['[', ']', ' ']:
                end_idx += 1
            parse_table[row][col] = parse_string[idx:end_idx]
            idx = end_idx
    # add tree lines to odd-numbered rows
        for z_row in range(2 * max_bracket_level - 1):
            if z_row % 2 == 1:
                for z_col in range(word_count):
                    # if symbol below and symbol above, add |
                    if len(parse_table[z_row + 1][z_col]) > 0 and len(parse_table[z_row - 1][z_col]) > 0:
                        parse_table[z_row][z_col] = '|'
                    # if symbol below and no symbol above, add .
                    elif len(parse_table[z_row + 1][z_col]) > 0:
                        parse_table[z_row][z_col] = '-.'
                        # - in all cols left until next symbol
                        dash_col = z_col - 1
                        while len(parse_table[z_row][dash_col]) == 0:
                            parse_table[z_row][dash_col] = '-'
                            dash_col -= 1
    # justify each cell to col_width, and print row by row
    for row_idx in range(len(parse_table)):
        row_string = ''
        for item in parse_table[row_idx]:
            if '-' in item and row_idx < len(parse_table) - 1:
                row_string += item.rjust(col_width, '-')
            else:
                row_string += item.rjust(col_width, ' ')
        print row_string

text = '1 + 3 x 4 = 13'
parses = cky_algorithm(text.split())

print
print 'INPUT:', text
print 'PARSES'
for parse in parses:
    print
    print 'VALUE:', parse.value
    print parse.trace_text
    parse_tree_printout(parse.trace_text, 8)
