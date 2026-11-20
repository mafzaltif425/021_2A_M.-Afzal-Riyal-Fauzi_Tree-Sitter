"""
[PENGAYAAN TUGAS 4]
Konverter AST DSL Filter ke SQL WHERE Clause Terparameterisasi (?)
Mencegah kerentanan SQL Injection dengan memisahkan struktur query dan nilai parameter.
"""

import re
import json

class NodeFilter:
    def __init__(self, tipe, text="", children=None, field=None):
        self.type = tipe
        self.text = text
        self.children = children or []
        self.field = field

def parse_filter_tokens(dsl_text):
    """
    Parser deterministik yang memetakan sintaks DSL filter ke struktur AST Tree-sitter
    sebagaimana didefinisikan di grammar.js.
    """
    tokens = []
    # Tokenizer sederhana untuk DSL filter
    token_spec = [
        ('STRING', r'"[^"]*"'),
        ('NUMBER', r'\d+(\.\d+)?'),
        ('OPERATOR', r'!=|>=|<=|=|>|<'),
        ('KEYWORD', r'\b(and|or|not|in|contains|true|false)\b'),
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_.]*'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('COMMA', r','),
        ('WS', r'\s+'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)
    for mo in re.finditer(tok_regex, dsl_text):
        kind = mo.lastgroup
        val = mo.group()
        if kind == 'WS':
            continue
        tokens.append((kind, val))
    return tokens

class FilterASTBuilder:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def consume(self, expected_kind=None, expected_val=None):
        kind, val = self.peek()
        if kind is None:
            raise SyntaxError("Unexpected end of input")
        if expected_kind and kind != expected_kind:
            raise SyntaxError(f"Expected token {expected_kind}, got {kind} ({val})")
        if expected_val and val.lower() != expected_val.lower():
            raise SyntaxError(f"Expected '{expected_val}', got '{val}'")
        self.pos += 1
        return kind, val

    def parse(self):
        expr = self.parse_or()
        return NodeFilter("query", children=[expr])

    def parse_or(self):
        left = self.parse_and()
        while self.pos < len(self.tokens) and self.peek()[1] == 'or':
            self.consume('KEYWORD', 'or')
            right = self.parse_and()
            left = NodeFilter("or_expression", children=[left, right])
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.pos < len(self.tokens) and self.peek()[1] == 'and':
            self.consume('KEYWORD', 'and')
            right = self.parse_not()
            left = NodeFilter("and_expression", children=[left, right])
        return left

    def parse_not(self):
        if self.pos < len(self.tokens) and self.peek()[1] == 'not':
            self.consume('KEYWORD', 'not')
            operand = self.parse_primary()
            return NodeFilter("not_expression", children=[operand])
        return self.parse_primary()

    def parse_primary(self):
        kind, val = self.peek()
        if kind == 'LPAREN':
            self.consume('LPAREN')
            sub = self.parse_or()
            self.consume('RPAREN')
            return NodeFilter("parenthesized", children=[sub])
        elif kind == 'IDENTIFIER':
            field_name = val
            self.consume('IDENTIFIER')
            next_kind, next_val = self.peek()

            if next_kind == 'OPERATOR':
                op_kind, op = self.consume('OPERATOR')
                val_kind, val_lit = self.consume_value()
                val_node = NodeFilter(val_kind.lower(), text=val_lit)
                comp = NodeFilter("comparison", children=[
                    NodeFilter("identifier", text=field_name, field="field"),
                    val_node
                ])
                comp.operator = op
                return comp

            elif next_kind == 'KEYWORD' and next_val.lower() == 'in':
                self.consume('KEYWORD', 'in')
                self.consume('LPAREN')
                val_nodes = []
                vk, vl = self.consume_value()
                val_nodes.append(NodeFilter(vk.lower(), text=vl))
                while self.peek()[0] == 'COMMA':
                    self.consume('COMMA')
                    vk, vl = self.consume_value()
                    val_nodes.append(NodeFilter(vk.lower(), text=vl))
                self.consume('RPAREN')
                in_node = NodeFilter("in_expression", children=[
                    NodeFilter("identifier", text=field_name, field="field")
                ] + val_nodes)
                return in_node

            elif next_kind == 'KEYWORD' and next_val.lower() == 'contains':
                self.consume('KEYWORD', 'contains')
                str_kind, str_lit = self.consume('STRING')
                contains_node = NodeFilter("contains_expression", children=[
                    NodeFilter("identifier", text=field_name, field="field"),
                    NodeFilter("string", text=str_lit)
                ])
                return contains_node
            else:
                raise SyntaxError(f"Unexpected token after identifier: {next_val}")
        else:
            raise SyntaxError(f"Unexpected token in expression: {val}")

    def consume_value(self):
        kind, val = self.peek()
        if kind in ('STRING', 'NUMBER'):
            return self.consume(kind)
        elif kind == 'KEYWORD' and val in ('true', 'false'):
            return self.consume('KEYWORD')
        raise SyntaxError(f"Expected value literal, got {kind} ({val})")

def ast_ke_sql(node):
    """
    Menelusuri node AST secara rekursif dan menghasilkan (sql_clause, params)
    """
    if node.type == "query":
        return ast_ke_sql(node.children[0])

    elif node.type == "or_expression":
        sql_l, p_l = ast_ke_sql(node.children[0])
        sql_r, p_r = ast_ke_sql(node.children[1])
        return f"({sql_l} OR {sql_r})", p_l + p_r

    elif node.type == "and_expression":
        sql_l, p_l = ast_ke_sql(node.children[0])
        sql_r, p_r = ast_ke_sql(node.children[1])
        return f"{sql_l} AND {sql_r}", p_l + p_r

    elif node.type == "not_expression":
        sql_op, p_op = ast_ke_sql(node.children[0])
        return f"NOT ({sql_op})", p_op

    elif node.type == "parenthesized":
        sql_in, p_in = ast_ke_sql(node.children[0])
        return f"({sql_in})", p_in

    elif node.type == "comparison":
        field = node.children[0].text
        op = getattr(node, 'operator', '=')
        # Konversi literal
        raw_val = node.children[1].text
        if node.children[1].type == "string":
            parsed_val = raw_val[1:-1] # buang tanda petik
        elif node.children[1].type == "number":
            parsed_val = float(raw_val) if '.' in raw_val else int(raw_val)
        else:
            parsed_val = True if raw_val.lower() == 'true' else False
        return f"{field} {op} ?", [parsed_val]

    elif node.type == "in_expression":
        field = node.children[0].text
        vals = []
        for child in node.children[1:]:
            rv = child.text
            if child.type == "string":
                vals.append(rv[1:-1])
            elif child.type == "number":
                vals.append(float(rv) if '.' in rv else int(rv))
            else:
                vals.append(True if rv.lower() == 'true' else False)
        placeholders = ", ".join(["?"] * len(vals))
        return f"{field} IN ({placeholders})", vals

    elif node.type == "contains_expression":
        field = node.children[0].text
        str_val = node.children[1].text[1:-1]
        # SQL LIKE parameterisasi: '%nilai%'
        return f"{field} LIKE ?", [f"%{str_val}%"]

    raise ValueError(f"Tipe node AST tidak dikenali: {node.type}")

def demo_konversi():
    contoh_input = 'status = "open" and (priority > 2 or owner = "budi") and category in ("bug", "incident") and not archived = true and description contains "timeout"'
    print("=" * 70)
    print("DEMO KONVERSI DSL FILTER KE SQL WHERE CLAUSE TERPARAMETERISASI")
    print("=" * 70)
    print(f"Input DSL:\n{contoh_input}\n")

    tokens = parse_filter_tokens(contoh_input)
    ast = FilterASTBuilder(tokens).parse()
    sql_where, params = ast_ke_sql(ast)

    print("Hasil SQL WHERE Clause:")
    print(f"WHERE {sql_where}\n")
    print("Parameter Query (?):")
    print(json.dumps(params, indent=2))
    print("\nKeuntungan Keamanan:")
    print("1. Nilai input pengguna tidak pernah disambung langsung (string concatenation).")
    print("2. Sepenuhnya kebal terhadap serangan SQL Injection (SQLi).")
    print("3. Query plan dapat di-cache oleh RDBMS untuk kinerja optimal.")
    print("=" * 70)

if __name__ == "__main__":
    demo_konversi()
