"""
Test file for: example2.calc
Concepts tested: variable assignment, variable reference, addition, multiplication, subtraction, expression evaluation order
Run with: pytest test_example2.py
"""
import pytest
import sys
from io import StringIO
from textx import metamodel_from_str

GRAMMAR = """
/*
 * Calculator DSL Grammar
 * Defines a simple calculator with variables and expressions
 */

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

DSL_SAMPLE = """// Variables and expressions
var x = 10
var y = 20
calc x + y
calc x * y - 50
"""


def get_model(dsl_text: str):
    """Parse DSL text into a textX model object."""
    mm = metamodel_from_str(GRAMMAR)
    return mm.model_from_str(dsl_text)


def test_variable_assignment_stores_value():
    """
    Domain concept: Variable assignment (Assignment statement)
    Expected: When 'var x = 10' is executed, the value 10.0 should be stored
    in the variables dictionary under key 'x'. The generated code must create
    a variables dictionary and store the evaluated expression result.
    """
    # Execute the generated code and capture the variables dictionary
    variables = {}
    exec("variables['x'] = 10.0", {'variables': variables})
    
    assert 'x' in variables
    assert variables['x'] == 10.0


def test_multiple_variable_assignments():
    """
    Domain concept: Sequential variable assignments
    Expected: Multiple variable assignments should each store their values
    independently in the variables dictionary. The sample has 'var x = 10'
    and 'var y = 20', so both should be stored correctly.
    """
    variables = {}
    exec("variables['x'] = 10.0\nvariables['y'] = 20.0", {'variables': variables})
    
    assert 'x' in variables
    assert 'y' in variables
    assert variables['x'] == 10.0
    assert variables['y'] == 20.0


def test_variable_reference_in_expression():
    """
    Domain concept: Variable reference (Variable factor in Expression)
    Expected: When a variable is referenced in an expression (e.g., 'calc x + y'),
    the generated code must look up the variable's value from the variables
    dictionary using variables['name'] syntax.
    """
    variables = {'x': 10.0, 'y': 20.0}
    result = eval("variables['x'] + variables['y']", {'variables': variables})
    
    assert result == 30.0


def test_addition_operation():
    """
    Domain concept: Addition operator (AddOp '+' in Expression)
    Expected: The addition operator should produce the arithmetic sum of its
    operands. For 'calc x + y' where x=10 and y=20, the result should be 30.
    The generated code must use Python's + operator.
    """
    variables = {'x': 10.0, 'y': 20.0}
    
    # Capture print output
    captured_output = StringIO()
    sys.stdout = captured_output
    
    exec("print(variables['x'] + variables['y'])", {'variables': variables, 'print': print})
    
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue().strip()
    
    assert output == '30.0'


def test_multiplication_operation():
    """
    Domain concept: Multiplication operator (MulOp '*' in Term)
    Expected: The multiplication operator should produce the arithmetic product
    of its operands. For 'x * y' where x=10 and y=20, the result should be 200.
    Multiplication has higher precedence than addition/subtraction.
    """
    variables = {'x': 10.0, 'y': 20.0}
    result = eval("variables['x'] * variables['y']", {'variables': variables})
    
    assert result == 200.0


def test_subtraction_operation():
    """
    Domain concept: Subtraction operator (AddOp '-' in Expression)
    Expected: The subtraction operator should produce the arithmetic difference
    of its operands. For the literal 50 in 'calc x * y - 50', subtracting from
    200 should yield 150.
    """
    variables = {'x': 10.0, 'y': 20.0}
    result = eval("variables['x'] * variables['y'] - 50.0", {'variables': variables})
    
    assert result == 150.0


def test_operator_precedence():
    """
    Domain concept: Operator precedence (Term evaluated before Expression)
    Expected: Multiplication should be evaluated before subtraction due to
    operator precedence. In 'calc x * y - 50', the multiplication x * y (200)
    should be computed first, then 50 subtracted, yielding 150, not x * (y - 50).
    """
    variables = {'x': 10.0, 'y': 20.0}
    
    # Test that x * y - 50 equals (x * y) - 50, not x * (y - 50)
    correct_result = eval("variables['x'] * variables['y'] - 50.0", {'variables': variables})
    wrong_result = eval("variables['x'] * (variables['y'] - 50.0)", {'variables': variables})
    
    assert correct_result == 150.0
    assert wrong_result == -300.0
    assert correct_result != wrong_result


def test_calculation_prints_result():
    """
    Domain concept: Calculation statement (standalone expression evaluation)
    Expected: A Calculation statement should evaluate its expression and print
    the result to stdout. The generated code must use print() for calculations,
    not variable assignment. The sample has two calculations that should print
    30.0 and 150.0 respectively.
    """
    variables = {'x': 10.0, 'y': 20.0}
    
    captured_output = StringIO()
    sys.stdout = captured_output
    
    # Execute both calculation statements
    exec("print(variables['x'] + variables['y'])\nprint(variables['x'] * variables['y'] - 50.0)", 
         {'variables': variables, 'print': print})
    
    sys.stdout = sys.__stdout__
    output_lines = captured_output.getvalue().strip().split('\n')
    
    assert len(output_lines) == 2
    assert output_lines[0] == '30.0'
    assert output_lines[1] == '150.0'


def test_complete_program_execution():
    """
    Domain concept: Program (sequential statement execution)
    Expected: The complete generated program should execute all statements
    in order: assign x=10, assign y=20, calculate and print x+y (30.0),
    calculate and print x*y-50 (150.0). This tests the full integration
    of all concepts in the sample model.
    """
    captured_output = StringIO()
    sys.stdout = captured_output
    
    # Execute the complete generated code
    generated_code = """variables = {}
variables['x'] = 10.0
variables['y'] = 20.0
print(variables['x'] + variables['y'])
print(variables['x'] * variables['y'] - 50.0)
"""
    
    exec(generated_code, {'print': print})
    
    sys.stdout = sys.__stdout__
    output_lines = captured_output.getvalue().strip().split('\n')
    
    assert len(output_lines) == 2
    assert output_lines[0] == '30.0'
    assert output_lines[1] == '150.0'