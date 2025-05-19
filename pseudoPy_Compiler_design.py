import tkinter as tk
from tkinter import scrolledtext, messagebox
import ply.lex as lex
import ply.yacc as yacc
import sys
import io

# ----------- LEXER -----------
keywords = {
    'set': 'SET',
    'to': 'TO',
    'print': 'PRINT',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'end': 'END',
    'while': 'WHILE',
    'do': 'DO',
    'function': 'FUNCTION',
    'return': 'RETURN',
    'call': 'CALL',
    'input': 'INPUT'
}

tokens = list(keywords.values()) + [
    'ID', 'NUMBER', 'STRING',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'EQ', 'GT', 'LT', 'GE', 'LE', 'NE',
    'LPAREN', 'RPAREN', 'COMMA', 'NEWLINE'
]

t_ignore = ' \t'


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = keywords.get(t.value.lower(), 'ID')
    return t


def t_STRING(t):
    r'"[^"\n]*"'
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Symbols

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQ = r'=='
t_GT = r'>'
t_LT = r'<'
t_GE = r'>='
t_LE = r'<='
t_NE = r'!='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA = r','

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

def t_error(t):
    raise SyntaxError(f"Illegal character: {t.value[0]}")

lexer = lex.lex()

# ----------- PARSER -----------
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def p_program(p):
    '''program : statement_list'''
    p[0] = '\n'.join(p[1])

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def indent(lines):
    return '\n'.join('    ' + line for line in lines)

def p_statement(p):
    '''statement : simple_stmt NEWLINE
                 | compound_stmt'''
    p[0] = p[1]

def p_simple_stmt(p):
    '''simple_stmt : SET ID TO expression
                   | PRINT expression
                   | RETURN expression
                   | INPUT ID
                   | CALL ID'''
    if p[1].lower() == 'set':
        p[0] = f"{p[2]} = {p[4]}"
    elif p[1].lower() == 'print':
        p[0] = f"print({p[2]})"
    elif p[1].lower() == 'return':
        p[0] = f"return {p[2]}"
    elif p[1].lower() == 'input':
        p[0] = f"{p[2]} = input()"
    elif p[1].lower() == 'call':
        p[0] = f"{p[2]}()"

def p_compound_stmt(p):
    '''compound_stmt : if_stmt
                     | while_stmt
                     | func_def'''
    p[0] = p[1]

def p_if_stmt(p):
    '''if_stmt : IF expression THEN NEWLINE statement_list END NEWLINE
               | IF expression THEN NEWLINE statement_list ELSE NEWLINE statement_list END NEWLINE'''
    if len(p) == 8:
        p[0] = f"if {p[2]}:\n{indent(p[5])}"
    else:
        p[0] = f"if {p[2]}:\n{indent(p[5])}\nelse:\n{indent(p[8])}"

def p_while_stmt(p):
    '''while_stmt : WHILE expression DO NEWLINE statement_list END NEWLINE'''
    p[0] = f"while {p[2]}:\n{indent(p[5])}"

def p_func_def(p):
    '''func_def : FUNCTION ID LPAREN RPAREN NEWLINE statement_list END NEWLINE'''
    p[0] = f"def {p[2]}():\n{indent(p[6])}"

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EQ expression
                  | expression GT expression
                  | expression LT expression
                  | expression GE expression
                  | expression LE expression
                  | expression NE expression'''
    p[0] = f"({p[1]} {p[2]} {p[3]})"

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = f"({p[2]})"

def p_expression_atom(p):
    '''expression : NUMBER
                  | STRING
                  | ID'''
    p[0] = str(p[1])

def p_error(p):
    raise SyntaxError("Syntax error in input!")

parser = yacc.yacc()

# ----------- GUI -----------
def translate():
    try:
        pseudocode = input_text.get("1.0", tk.END)
        result = parser.parse(pseudocode + '\n')
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, result)
    except SyntaxError as e:
        messagebox.showerror("Syntax Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", str(e))

def execute():
    try:
        code = output_text.get("1.0", tk.END)
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        exec(code, {})
        sys.stdout = old_stdout
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, mystdout.getvalue())
    except Exception as e:
        messagebox.showerror("Runtime Error", str(e))
    finally:
        sys.stdout=old_stdout   


root = tk.Tk()
root.title("Pseudocode Compiler")
root.configure(bg="#f5f5f5")

tk.Label(root, text="Pseudocode Input", font=("Arial", 12), bg="#f5f5f5").pack(pady=(10, 0))
input_text = scrolledtext.ScrolledText(root, height=10, width=80, font=("Consolas", 11), bg="#ffffff", bd=1, relief="solid")
input_text.pack(padx=10, pady=5)

tk.Button(root, text="Compile to Python", command=translate, bg="#4caf50", fg="white", font=("Arial", 11)).pack(pady=5)

tk.Label(root, text="Generated Python Code", font=("Arial", 12), bg="#f5f5f5").pack()
output_text = scrolledtext.ScrolledText(root, height=10, width=80, font=("Consolas", 11), bg="#f0f0f0", bd=1, relief="solid")
output_text.pack(padx=10, pady=5)

tk.Button(root, text="Execute Python Code", command=execute, bg="#2196f3", fg="white", font=("Arial", 11)).pack(pady=5)

tk.Label(root, text="Program Output", font=("Arial", 12), bg="#f5f5f5").pack()
result_text = scrolledtext.ScrolledText(root, height=8, width=80, font=("Consolas", 11), bg="#e8e8e8", bd=1, relief="solid")
result_text.pack(padx=10, pady=5)

root.mainloop()
