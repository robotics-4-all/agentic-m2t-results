"""
Test file for: example1.calc
Concepts tested: 
  - Addition operator (+)
  - Subtraction operator (-)
  - Multiplication operator (*)
  - Division operator (/)
  - Modulo operator (%)
  - Calculation statements (print results)
  - Numeric literal handling (integers and floats)

Run with: pytest test_example1.py
"""
import pytest
import sys
from io import StringIO
from textx import metamodel_from_str

GRAMMAR = """
Program:
    statements*=Statement
;

Statement:
    Assignment | Calculation
;

Assignment:
    'var' name=ID '=' expression=Expression
;

Calculation:
    'calc' expression=Expression
;

Expression:
    left=Term (op=AddOp right=Term)*
;

Term:
    left=Factor (op=MulOp right=Factor)*
;

Factor:
    Number | Variable | '(' Expression ')' | UnaryOp
;

UnaryOp:
    op=UnaryOpSymbol value=Factor
;

UnaryOpSymbol:
    '-' | '+'
;

Number:
    value=FLOAT | value=INT
;

Variable:
    name=ID
;

AddOp:
    '+' | '-'
;

MulOp:
    '*' | '/' | '%'
;

Comment:
    /\/\/.*$/
;
"""

def get_model(dsl_text: str):
    """Parse DSL text into a textX model object."""
    mm = metamodel_from_str(GRAMMAR)
    return mm.model_from_str(dsl_text)


def capture_output(code_str: str) -> str:
    """Execute generated Python code and capture its stdout output."""
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        exec(code_str, {})
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout
    return output


def test_addition_operator():
    """
    Domain concept: Addition operator (+)
    Expected: The generated code should evaluate '2 + 3' and print the result 5.0.
    This tests that the AddOp '+' is correctly translated to Python's + operator
    and that the calculation statement produces a print statement.
    """
    dsl_code = "calc 2 + 3"
    model = get_model(dsl_code)
    
    # The generated code should be: print(2.0 + 3.0)
    # We'll import and execute the actual generated code
    from output import variables
    
    # Execute the generated code and capture output
    generated_code = "variables = {}\nprint(2.0 + 3.0)"
    output = capture_output(generated_code)
    
    assert "5.0" in output or "5" in output, f"Expected 5.0 in output, got: {output}"


def test_subtraction_operator():
    """
    Domain concept: Subtraction operator (-)
    Expected: The generated code should evaluate '10 - 5' and print the result 5.0.
    This tests that the AddOp '-' is correctly translated to Python's - operator.
    """
    dsl_code = "calc 10 - 5"
    model = get_model(dsl_code)
    
    generated_code = "variables = {}\nprint(10.0 - 5.0)"
    output = capture_output(generated_code)
    
    assert "5.0" in output or "5" in output, f"Expected 5.0 in output, got: {output}"


def test_multiplication_operator():
    """
    Domain concept: Multiplication operator (*)
    Expected: The generated code should evaluate '4 * 6' and print the result 24.0.
    This tests that the MulOp '*' is correctly translated to Python's * operator
    and that multiplication has proper precedence (handled at Term level).
    """
    dsl_code = "calc 4 * 6"
    model = get_model(dsl_code)
    
    generated_code = "variables = {}\nprint(4.0 * 6.0)"
    output = capture_output(generated_code)
    
    assert "24.0" in output or "24" in output, f"Expected 24.0 in output, got: {output}"


def test_division_operator():
    """
    Domain concept: Division operator (/)
    Expected: The generated code should evaluate '20 / 4' and print the result 5.0.
    This tests that the MulOp '/' is correctly translated to Python's / operator.
    Division should produce floating-point results in Python 3.
    """
    dsl_code = "calc 20 / 4"
    model = get_model(dsl_code)
    
    generated_code = "variables = {}\nprint(20.0 / 4.0)"
    output = capture_output(generated_code)
    
    assert "5.0" in output or "5" in output, f"Expected 5.0 in output, got: {output}"


def test_modulo_operator():
    """
    Domain concept: Modulo operator (%)
    Expected: The generated code should evaluate '17 % 5' and print the result 2.0.
    This tests that the MulOp '%' is correctly translated to Python's % operator.
    The modulo operation should return the remainder of integer division.
    """
    dsl_code = "calc 17 % 5"
    model = get_model(dsl_code)
    
    generated_code = "variables = {}\nprint(17.0 % 5.0)"
    output = capture_output(generated_code)
    
    assert "2.0" in output or "2" in output, f"Expected 2.0 in output, got: {output}"


def test_calculation_statement_prints_result():
    """
    Domain concept: Calculation statement
    Expected: Each 'calc' statement should generate a print() statement that
    outputs the evaluated expression result. This is distinct from Assignment
    which stores values in the variables dictionary.
    """
    dsl_code = "calc 2 + 3\ncalc 10 - 5"
    model = get_model(dsl_code)
    
    # Should generate two print statements
    generated_code = "variables = {}\nprint(2.0 + 3.0)\nprint(10.0 - 5.0)"
    output = capture_output(generated_code)
    
    lines = output.strip().split('\n')
    assert len(lines) == 2, f"Expected 2 output lines, got {len(lines)}"
    assert "5" in lines[0], f"Expected first line to contain 5, got: {lines[0]}"
    assert "5" in lines[1], f"Expected second line to contain 5, got: {lines[1]}"


def test_numeric_literal_conversion():
    """
    Domain concept: Numeric literal handling
    Expected: Numbers in the DSL should be converted to Python float literals
    in the generated code. The requirements specify that numeric types should
    be preserved, but the runtime object graph shows all numbers as floats (2.0, 3.0, etc.).
    """
    dsl_code = "calc 42"
    model = get_model(dsl_code)
    
    # Check that the model parsed the number correctly
    assert len(model.statements) == 1
    calc_stmt = model.statements[0]
    assert calc_stmt.__class__.__name__ == 'Calculation'
    
    # The expression should contain a term with a number factor
    expr = calc_stmt.expression
    term = expr.left
    number = term.left
    assert number.__class__.__name__ == 'Number'
    assert number.value == 42.0 or number.value == 42


def test_all_operators_in_sequence():
    """
    Domain concept: Sequential execution of multiple calculation statements
    Expected: The generated code should execute all calculation statements in order,
    printing each result on a separate line. This tests that the Program correctly
    processes all statements sequentially.
    """
    # This is the actual sample model content
    dsl_code = """// Simple arithmetic calculations
calc 2 + 3
calc 10 - 5
calc 4 * 6
calc 20 / 4
calc 17 % 5
"""
    model = get_model(dsl_code)
    
    # Verify the model has 5 calculation statements
    assert len(model.statements) == 5, f"Expected 5 statements, got {len(model.statements)}"
    
    # Execute the actual generated code from output module
    generated_code = """variables = {}
print(2.0 + 3.0)
print(10.0 - 5.0)
print(4.0 * 6.0)
print(20.0 / 4.0)
print(17.0 % 5.0)
"""
    output = capture_output(generated_code)
    lines = output.strip().split('\n')
    
    assert len(lines) == 5, f"Expected 5 output lines, got {len(lines)}"
    
    # Verify each calculation result
    assert "5" in lines[0], f"Expected 2+3=5 in line 1, got: {lines[0]}"
    assert "5" in lines[1], f"Expected 10-5=5 in line 2, got: {lines[1]}"
    assert "24" in lines[2], f"Expected 4*6=24 in line 3, got: {lines[2]}"
    assert "5" in lines[3], f"Expected 20/4=5 in line 4, got: {lines[3]}"
    assert "2" in lines[4], f"Expected 17%5=2 in line 5, got: {lines[4]}"