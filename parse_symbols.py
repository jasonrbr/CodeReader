import re

# raw symbols and their translations when passing to say
# must be in decreasing order to enforce
symbol_list = {
    r'cout': 'see out', r'cin': 'see in', r'endl': 'endline',
    r'!=': ' is not equal to ', r'==': ' is equal to ',
    r'-=': ' minus equals ', r'->': ' arrow ',
    r'*=': ' times equals ', r'/=': ' divide equals ',
    r'<<': ',', r'>>': ',', r'--': ' minus minus ', r';': ',',
    r'<=': ' less than or equal to ',
    r'//': ' comment: ', r'/*': ' comment: ', r'*/': ' end comment: ',
    r'>=': ' greater than or equal to ',
    r'*': ' star ', r'&': ' ampersand ', r'(': ' ', r')': ' ',
    r'|': ' bar ', ' < ': ' less than ', r' > ': ' greater than ',
}

# Need to sort by descending length
symbols = sorted(symbol_list.keys(), key=len, reverse=True)


# temp function for dynamic templated container parsing
# separate from symbol list for now to lower design complexity
def temp_container_parsing(input_str):
    pattern = re.compile('(\w+)\s?\<\s?(\w+)\>')
    while re.search(pattern, input_str):
        m = re.search(pattern, input_str)
        original_match = m.group(0)
        container_type = m.group(1)
        template_type = m.group(2)
        repl = '{} of type {}'.format(container_type, template_type)
        input_str = re.sub(original_match, repl, input_str)
    return input_str


# Returns a stripped string with symbols mapped to their
# appropriate English words
def parse_symbols(input_str):
    pattern = re.compile('|'.join(re.escape(key) for key in symbols))
    parsed = pattern.sub(lambda x: symbol_list[x.group()], input_str)
    # separate parsing for templated containers
    return parsed.strip()
    parsed = temp_container_parsing(parsed)
