class CKY_rule:
    def __init__(self, left, right):
        self.left  = left
        self.right = right.split()
    
    def rule_match(self, symbol_list):
        if symbol_list == self.right:
            return True
        else:
            return False
    
    def printout(self):
        print self.left.ljust(3), "->", self.right

class CKY_table:
    def __init__(self, sentence):
        self.sentence = sentence
        self.len   = len(self.sentence)
        self.table = {}
        for i in range(1, self.len + 1):
            for j in range(self.len - i + 1):
                self.table[(i,j)] = []
    
    def cell_trace_list(self, i, j):
        return self.table[(i,j)]
    
    def add_symbol(self, i, j, symbol, trace_text):
        self.table[(i,j)].append(CKY_trace(symbol, trace_text))
    
    def printout(self):
        print 'CKY TABLE'
        for i in range(self.len, 0, -1):
            row_string = ''
            for j in range(self.len - i + 1):
                row_string += ' ' + str(j) + '[' + ','.join([trace.symbol for trace in self.table[(i,j)]]).ljust(5) + ']'
            print i, ':', row_string
        # print sentence
        sentence_print = ''
        for word in self.sentence:
            sentence_print += '|' + word.ljust(8)
        print 'SEN ', sentence_print

class CKY_trace:
    def __init__(self, symbol, trace_text):
        self.symbol     = symbol
        self.trace_text = trace_text

# list of rewrite rules
rules_string = 'S->NP VP; VP->VP PP; VP->V NP; PP->P NP; NP->Det N; NP->NP PP'
rules = [CKY_rule(rule[:rule.find('->')],
                  rule[rule.find('->') + 2:]) for rule in rules_string.split('; ')]
print 'RULES'
for rule in rules:
    rule.printout()

lexicon = {'she': ['NP'],
           'eats': ['V', 'VP'],
           'with': ['P'],
           'fish': ['N'],
           'fork': ['N'],
           'a': ['Det']}

def cky_algorithm(sentence):
    sentence_len = len(sentence)
    cky = CKY_table(sentence)
    
    # words to PoS (row 1)
    for w in range(sentence_len):
        for symbol in lexicon[sentence[w]]:
            trace_text = '[' + symbol + ' ' + sentence[w] + ']'
            cky.add_symbol(1, w, symbol, trace_text)
    print
    print 'ROW 1: PARTS OF SPEECH'
    cky.printout()

    # rows 2 upwards
    for span_len in range(2, sentence_len + 1):
        for pos in range(sentence_len - span_len + 1):
            for split in range(pos + 1, pos + span_len):
                #print 'LEN', span_len, ', SPAN', pos, '-', pos + span_len, ', SPLIT', split, '(', split - pos, pos, ')(', pos + span_len - split, split, ')'
                for rule in rules:
                    for trace_1 in cky.cell_trace_list(split - pos, pos):
                        for trace_2 in cky.cell_trace_list(pos + span_len - split, split):
                            if rule.rule_match([trace_1.symbol, trace_2.symbol]):
                                print
                                rule.printout()
                                print '(', span_len, pos, ')->(', split - pos, pos, ')(', pos + span_len - split, split, ')'
                                trace_text = '[' + rule.left + trace_1.trace_text + trace_2.trace_text + ']'
                                print 'TRACE', trace_text
                                cky.add_symbol(span_len, pos, rule.left, trace_text)
                                cky.printout()
    
    return cky.cell_trace_list(sentence_len, 0)

text = 'she eats a fish with a fork'
parses = cky_algorithm(text.split())

print
print 'INPUT:', text
print 'PARSES'
for parse in parses:
    print parse.trace_text
