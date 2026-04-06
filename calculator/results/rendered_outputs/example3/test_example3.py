"""
Test file for: example3.calc
Concepts tested: parenthesized expressions, operator precedence, complex nested expressions, variable assignment with expressions, variable reference in calculations
Run with: pytest test_example3.py
"""
import pytest
import sys
from io import StringIO

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


def test_parenthesized_addition_then_multiplication():
    """
    Domain concept: Parenthesized expressions override default operator precedence
    Expected: (2 + 3) * 4 should evaluate to 5 * 4 = 20, not 2 + 12 = 14
    
    This tests that parentheses in the DSL are correctly translated to parentheses
    in the generated Python code, ensuring the addition happens before multiplication.
    """
    # Capture stdout to verify the print statement output
    captured_output = StringIO()
    sys.stdout = captured_output
    
    # Execute the generated code
    exec(open('output.py').read())
    
    sys.stdout = sys.__stdout__
    output_lines = captured_output.getvalue().strip().split('\n')
    
    # First calculation: (2 + 3) * 4 = 20.0
    assert float(output_lines[0]) == 20.0


def test_division_with_parenthesized_denominator():
    """
    Domain concept: Parentheses in denominator ensure correct division order
    Expected: 10 / (2 + 3) should evaluate to 10 / 5 = 2, not 5 + 3 = 8
    
    This tests that parenthesized expressions in the right operand of division
    are evaluated first, preventing incorrect left-to-right evaluation.
    """
    captured_output = StringIO()
    sys.stdout = captured_output
    
    exec(open('output.py').read())
    
    sys.stdout = sys.__stdout__
    output_lines = captured_output.getvalue().strip().split('\n')
    
    # Second calculation: 10 / (2 + 3) = 2.0
    assert float(output_lines[1]) == 2.0


def test_nested_parentheses_with_multiple_operators():
    """
    Domain concept: Deeply nested parenthesized expressions with mixed operators
    Expected: ((5 + 3) * 2) - 4 should evaluate to (8 * 2) - 4 = 16 - 4 = 12
    
    This tests that multiple levels of parentheses are correctly preserved in the
    generated code, ensuring operations are performed in the correct order from
    innermost to outermost parentheses.
    """
    captured_output = StringIO()
    sys.stdout = captured_output
    
    exec(open('output.py').read())
    
    sys.stdout = sys.__stdout__
    output_lines = captured_output.getvalue().strip().split('\n')
    
    # Third calculation: ((5 + 3) * 2) - 4 = 12.0
    assert float(output_lines[2]) == 12.0


def test_variable_assignment_with_complex_expression():
    """
    Domain concept: Variable assignment stores the result of a complex expression
    Expected: result = (100 - 20) / 4 should store 80 / 4 = 20 in the variables dictionary
    
    This tests that assignments evaluate the entire expression (including parentheses)
    and store the computed value in the variables dictionary for later use.
    """
    # Create a clean namespace for execution
    namespace = {}
    exec(open('output.py').read(), namespace)
    
    # Fourth statement is an assignment: var result = (100 - 20) / 4
    assert 'variables' in namespace
    assert 'result' in namespace['variables']
    assert namespace['variables']['result'] == 20.0


def test_calculation_using_stored_variable():
    """
    Domain concept: Variable references retrieve stored values in calculations
    Expected: calc result + 10 should evaluate to 20 + 10 = 30
    
    This tests that variable references in calculations correctly look up the value
    from the variables dictionary and use it in the expression evaluation.
    """
    captured_output = StringIO()
    sys.stdout = captured_output
    
    exec(open('output.py').read())
    
    sys.stdout = sys.__stdout__
    output_lines = captured_output.getvalue().strip().split('\n')
    
    # Fifth calculation: result + 10 where result = 20, so 20 + 10 = 30.0
    assert float(output_lines[3]) == 30.0


def test_operator_precedence_preserved_in_parentheses():
    """
    Domain concept: Operator precedence within parentheses follows standard rules
    Expected: In (2 + 3), the addition is performed as a single unit
    
    This tests that even within parentheses, the generated code maintains proper
    operator semantics and doesn't introduce spurious operations.
    """
    captured_output = StringIO()
    sys.stdout = captured_output
    
    exec(open('output.py').read())
    
    sys.stdout = sys.__stdout__
    output_lines = captured_output.getvalue().strip().split('\n')
    
    # Verify first calculation again to ensure (2 + 3) evaluates to 5 before multiplication
    # (2 + 3) * 4: if precedence were wrong, we might get 2 + (3 * 4) = 14
    result = float(output_lines[0])
    assert result == 20.0
    assert result != 14.0  # Confirm it's not the wrong precedence


def test_all_calculations_produce_output():
    """
    Domain concept: Calculation statements produce printed output
    Expected: Four calc statements should produce four lines of output
    
    This tests that the generated code correctly distinguishes between assignments
    (which store values) and calculations (which print values), as specified in
    the requirements.
    """
    captured_output = StringIO()
    sys.stdout = captured_output
    
    exec(open('output.py').read())
    
    sys.stdout = sys.__stdout__
    output_lines = captured_output.getvalue().strip().split('\n')
    
    # Should have exactly 4 print outputs (4 calc statements)
    assert len(output_lines) == 4


def test_variables_dictionary_initialized():
    """
    Domain concept: Variable storage mechanism must exist before assignments
    Expected: A dictionary named 'variables' should be created and used for storage
    
    This tests that the generated code includes the required variables dictionary
    as specified in the requirements, enabling dynamic variable creation and lookup.
    """
    namespace = {}
    exec(open('output.py').read(), namespace)
    
    # Requirements specify: "Must include a dictionary named 'variables'"
    assert 'variables' in namespace
    assert isinstance(namespace['variables'], dict)
    assert len(namespace['variables']) == 1  # Only 'result' is assigned
    assert 'result' in namespace['variables']