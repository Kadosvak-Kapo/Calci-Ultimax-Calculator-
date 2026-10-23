import tkinter as tk
from sympy import *
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application
)

# ------------------ SYMPY SETUP ------------------
x, y, z, a, b, c, m, w, u, i, p, q, n = symbols('x y z a b c m w u i p q n')
transformations = standard_transformations + (implicit_multiplication_application,)

def smart_parse(expr_str):
    expr_str = expr_str.replace("^", "**")
    # If user types a decimal, this helps SymPy treat it as a fraction internally
    return parse_expr(expr_str, transformations=transformations)

# ------------------ UNIVERSAL FACTORING LOGIC ------------------

def try_split(term_list):
    count = len(term_list)
    if count < 4 or count % 2 != 0:
        return None
    half = count // 2
    g1 = Add(*term_list[:half])
    g2 = Add(*term_list[half:])
    f1, f2 = factor(g1), factor(g2)
    common = gcd(f1, f2)
    if common != 1:
        return common * simplify((f1/common) + (f2/common))
    return None

def universal_factor(expr):
    try:
        expr = simplify(expr)
        if not isinstance(expr, Add):
            return factor(expr)
        terms = expr.as_ordered_terms()
        n_terms = len(terms)
        if n_terms == 3:
            return factor(expr)
        if n_terms >= 4 and n_terms % 2 == 0:
            res = try_split(terms)
            if res: return res
            sorted_terms = sorted(terms, key=lambda t: str(t.free_symbols))
            res = try_split(sorted_terms)
            if res: return res
        return factor(expr)
    except:
        return factor(expr)

# ------------------ GUI FUNCTIONS ------------------
current_result = None
original_question = None
is_toggled = False 

def solve_input(event=None):
    global current_result, original_question, is_toggled
    user_input = entry.get().strip()
    if not user_input:
        output_var.set("")
        convert_btn.grid_remove()
        return
    try:
        if "," in user_input:
            parts = user_input.split(",")
            eqs = [Eq(smart_parse(p.split('=')[0]), smart_parse(p.split('=')[1] if '=' in p else "0")) for p in parts]
            current_result = solve(eqs)
            original_question = user_input
        else:
            expr = smart_parse(user_input)
            mode = angle_mode.get()
            if mode == "deg":
                expr = expr.replace(sin, lambda s: sin(s * pi/180)).replace(cos, lambda s: cos(s * pi/180)).replace(tan, lambda s: tan(s * pi/180))
            elif mode == "grad":
                expr = expr.replace(sin, lambda s: sin(s * pi/200)).replace(cos, lambda s: cos(s * pi/200)).replace(tan, lambda s: tan(s * pi/200))
            
            original_question = expr
            # If it's an equation like x^2+3x+9=0, solve it. If just expression, factor it.
            if "=" in user_input:
                lhs, rhs = user_input.split("=")
                current_result = solve(Eq(smart_parse(lhs), smart_parse(rhs)))
            else:
                current_result = universal_factor(expr)

        output_var.set(str(current_result))
        is_toggled = False
        convert_btn.grid()
    except Exception as e:
        output_var.set(f"Error: {str(e)}")
        convert_btn.grid_remove()

def convert_value():
    global current_result, original_question, is_toggled
    if current_result is None: return
    try:
        if not is_toggled:
            # Force Decimal Conversion
            res_sym = sympify(current_result)
            output_var.set(str(N(res_sym, 4))) # Show 4 decimal places
        else:
            # Back to Fraction / Symbolic
            # nsimplify tries to turn decimals like 0.75 back into 3/4
            output_var.set(str(nsimplify(current_result)))
        is_toggled = not is_toggled
    except:
        output_var.set(str(current_result))

def clear_input():
    global current_result, original_question, is_toggled
    entry.delete(0, tk.END)
    output_var.set("")
    current_result, original_question = None, None
    is_toggled = False
    convert_btn.grid_remove()

# ------------------ GUI SETUP ------------------
root = tk.Tk()
root.title("Calci - Universal Math Solver")
root.geometry("650x500")
root.configure(bg="#1e1e1e")

angle_mode = tk.StringVar(value="rad")
radio_frame = tk.Frame(root, bg="#1e1e1e")
radio_frame.pack(pady=10)
for text, val in [("Rad", "rad"), ("Deg", "deg"), ("Grad", "grad")]:
    tk.Radiobutton(radio_frame, text=text, variable=angle_mode, value=val, bg="#1e1e1e", fg="white", selectcolor="#444").pack(side="left", padx=15)

title = tk.Label(root, text="Calci", font=("Arial", 26, "bold"), fg="#ffffff", bg="#1e1e1e")
title.pack(pady=10)

entry = tk.Entry(root, font=("Arial", 16), width=40, bg="#2d2d2d", fg="#ffffff", insertbackground="white")
entry.pack(pady=10, ipady=8)
entry.bind("<Return>", solve_input)

btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=10)

solve_btn = tk.Button(btn_frame, text="SOLVE", command=solve_input, width=12, bg="#4CAF50", fg="white")
solve_btn.grid(row=0, column=0, padx=8)
clear_btn = tk.Button(btn_frame, text="CLEAR", command=clear_input, width=12, bg="#f44336", fg="white")
clear_btn.grid(row=0, column=1, padx=8)
convert_btn = tk.Button(btn_frame, text="DECIMAL / FRAC", command=convert_value, width=20, bg="#2196F3", fg="white")
convert_btn.grid(row=0, column=2, padx=8)
convert_btn.grid_remove()

output_var = tk.StringVar()
output_label = tk.Label(root, textvariable=output_var, font=("Consolas", 16), fg="#00ffcc", bg="#1e1e1e", wraplength=600)
output_label.pack(pady=40)

root.mainloop()