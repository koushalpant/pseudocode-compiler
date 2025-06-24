import tkinter as tk
import customtkinter as ctk
from tkinter import scrolledtext, messagebox
from tkinter import filedialog
import ply.lex as lex
import ply.yacc as yacc
import sys, io

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

def copy_output_code():
    app.clipboard_clear()
    app.clipboard_append(output_text.get("1.0", tk.END).strip())
    copy_btn.configure(text="✅ Copied!")
    app.after(1500, lambda: copy_btn.configure(text="📋 Copy Code"))

def export_python_code():
    code = output_text.get("1.0", tk.END).strip()
    if not code:
        messagebox.showinfo("Empty Output", "There is no code to export.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".py",
                                             filetypes=[("Python Files", "*.py")],
                                             title="Save Python Code")
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        messagebox.showinfo("Success", f"Code saved to:\n{filepath}")

def clear_all():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)
    result_text.delete("1.0", tk.END)


# ---------------- GUI Setup ----------------
def launch_main_app():
    global input_text, output_text, result_text, copy_btn
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")

    app = ctk.CTk()
    app.title("🧠 Pseudocode to Python Compiler")
    app.after(100, lambda: app.state("zoomed"))
    app.geometry("950x800")
    app.resizable(False, False)

    title_font = ctk.CTkFont("Segoe UI", 22, weight="bold")
    label_font = ctk.CTkFont("Segoe UI", 15)
    code_font = ("Consolas", 13)


    top_frame = ctk.CTkFrame(app, fg_color="#1f1f1f")
    top_frame.pack(fill="x", pady=(0, 10))
    ctk.CTkLabel(top_frame, text="🧠  Pseudocode to Python Compiler", font=title_font, text_color="#00e0ff").pack(pady=20)


    input_card = ctk.CTkFrame(app, corner_radius=12, fg_color="#2a2a2a")
    input_card.pack(padx=30, pady=10, fill="x")
    ctk.CTkLabel(input_card, text="Pseudocode Input", font=label_font).pack(anchor="w", padx=15, pady=(10, 5))
    input_text = ctk.CTkTextbox(input_card, height=160, font=code_font, corner_radius=10)
    input_text.pack(padx=15, pady=(0, 15), fill="x")

    compile_btn = ctk.CTkButton(app, text="⚙️ Compile to Python", command=translate, font=label_font,
                                fg_color="#388e3c", hover_color="#00e676", corner_radius=8)
    compile_btn.pack(pady=(0, 15))

    clear_btn = ctk.CTkButton(app, text="🔁 Clear All", command=clear_all, fg_color="#a33", hover_color="#d55")
    clear_btn.pack(pady=(0, 5))

    output_card = ctk.CTkFrame(app, corner_radius=12, fg_color="#2a2a2a")
    output_card.pack(padx=30, pady=10, fill="x")
    ctk.CTkLabel(output_card, text="Generated Python Code", font=label_font).pack(anchor="w", padx=15, pady=(10, 5))
    output_text = ctk.CTkTextbox(output_card, height=160, font=code_font, corner_radius=10)
    output_text.pack(padx=15, pady=(0, 15), fill="x")

    copy_btn = ctk.CTkButton(output_card, text="📋 Copy Code", command=copy_output_code,
                            font=label_font, fg_color="#444", hover_color="#555", corner_radius=8, width=120)
    copy_btn.pack(pady=(0, 10), padx=15, anchor="e")


    execute_btn = ctk.CTkButton(app, text="▶️ Execute Python Code", command=execute, font=label_font,
                                fg_color="#2962ff", hover_color="#448aff", corner_radius=8)
    execute_btn.pack(pady=(0, 15))

    export_btn = ctk.CTkButton(output_card, text="💾 Export to .py", command=export_python_code,
                            font=label_font, fg_color="#555", hover_color="#666", corner_radius=8)
    export_btn.pack(pady=(0, 15), padx=15, anchor="e")




    result_card = ctk.CTkFrame(app, corner_radius=12, fg_color="#2a2a2a")
    result_card.pack(padx=30, pady=10, fill="x")
    ctk.CTkLabel(result_card, text="Program Output", font=label_font).pack(anchor="w", padx=15, pady=(10, 5))
    result_text = ctk.CTkTextbox(result_card, height=120, font=code_font, corner_radius=10)
    result_text.pack(padx=15, pady=(0, 15), fill="x")

    def maximize():
        app.state("zoomed")

    app.after(100, maximize)  
    app.mainloop()

def show_welcome():
    welcome = ctk.CTk()
    welcome.title("Welcome")
    welcome.after(100, lambda: welcome.state("zoomed")) 
    welcome.resizable(False, False)


    ctk.CTkLabel(welcome, text="🧠 Welcome to Pseudocode Compiler", 
                font=ctk.CTkFont(size=30, weight="bold")).pack(pady=20)

    ctk.CTkLabel(welcome, text="Convert simple structured pseudocode into executable Python code.\n", 
                font=ctk.CTkFont(size=22), wraplength=500).pack()
    
    ctk.CTkButton(
    welcome, 
    text="🚀 Start Compiler", 
    command=lambda: [welcome.destroy(), launch_main_app()],
    fg_color="#2962ff", 
    hover_color="#448aff", 
    font=ctk.CTkFont(size=18, weight="bold"),  # Bigger font
    corner_radius=10, 
    width=220, 
    height=50 ).pack(pady=30)

    # Syntax Guide Section
    syntax_frame = ctk.CTkFrame(welcome, corner_radius=10, fg_color="#2a2a2a")
    syntax_frame.pack(padx=30, pady=10, fill="both", expand=True)

    syntax_text = """
📘 Pseudocode Syntax Guide:
• set x to 5
• print x
• input name
• if x > 10 then
    print "big"
end
• while x < 5 do
    set x to x + 1
end
• function greet()
    print "Hello"
end
• call greet()
• return x
"""
    ctk.CTkLabel(syntax_frame, text=syntax_text, justify="left", 
                font=("Consolas", 26)).pack(padx=20, pady=20)

    welcome.mainloop()

show_welcome()
