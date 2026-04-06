"""
Test file for: example4.calc
Concepts tested: floating-point arithmetic, unary operators, variable assignment with floats, variable references in expressions
Run with: pytest test_example4.py

This test file verifies the semantic correctness of code generated from a calculator DSL
sample that exercises floating-point numbers, unary plus/minus operators, variable
assignments with float values, and multi-variable expressions.
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


def test_floating_point_multiplication():
    """
    Domain concept: Floating-point number multiplication
    Expected: The calculation 'calc 3.14 * 2' should multiply two floating-point
    numbers and print the result. According to requirements, numeric literals preserve
    their type and multiplication uses the * operator directly.
    """
    dsl_code = "calc 3.14 * 2"
    model = get_model(dsl_code)
    
    # The generated code should be: print(3.14 * 2.0)
    from output import variables
    
    # Execute the generated code by importing it
    import output
    
    # Capture what the generated code prints
    output_lines = capture_output(open('output.py').read())
    lines = output_lines.strip().split('\n')
    
    # First calculation should print 3.14 * 2 = 6.28
    assert len(lines) >= 1
    result = float(lines[0])
    assert result == pytest.approx(6.28, rel=1e-9)


def test_unary_minus_with_addition():
    """
    Domain concept: Unary minus operator applied to a number in an addition expression
    Expected: The calculation 'calc -5 + 10' should apply unary minus to 5, then add 10,
    resulting in 5. The unary operator is applied directly before the factor according
    to the UnaryOp mapping rule.
    """
    dsl_code = "calc -5 + 10"
    
    output_lines = capture_output(open('output.py').read())
    lines = output_lines.strip().split('\n')
    
    # Second calculation: -5 + 10 = 5
    assert len(lines) >= 2
    result = float(lines[1])
    assert result == pytest.approx(5.0, rel=1e-9)


def test_unary_plus_with_subtraction():
    """
    Domain concept: Unary plus operator (identity operation) in a subtraction expression
    Expected: The calculation 'calc +15 - 3' should apply unary plus to 15 (no change),
    then subtract 3, resulting in 12. Unary plus is a valid operator that preserves the value.
    """
    dsl_code = "calc +15 - 3"
    
    output_lines = capture_output(open('output.py').read())
    lines = output_lines.strip().split('\n')
    
    # Third calculation: +15 - 3 = 12
    assert len(lines) >= 3
    result = float(lines[2])
    assert result == pytest.approx(12.0, rel=1e-9)


def test_unary_minus_on_parenthesized_expression():
    """
    Domain concept: Unary minus applied to a parenthesized expression
    Expected: The calculation 'calc -(10 + 5)' should first evaluate the parenthesized
    expression (10 + 5 = 15), then apply unary minus to get -15. According to requirements,
    parenthesized expressions preserve precedence and unary operators apply to factors.
    """
    dsl_code = "calc -(10 + 5)"
    
    output_lines = capture_output(open('output.py').read())
    lines = output_lines.strip().split('\n')
    
    # Fourth calculation: -(10 + 5) = -15
    assert len(lines) >= 4
    result = float(lines[3])
    assert result == pytest.approx(-15.0, rel=1e-9)


def test_variable_assignment_with_float():
    """
    Domain concept: Variable assignment storing a floating-point value
    Expected: The assignment 'var pi = 3.14159' should store the float value in the
    variables dictionary under the key 'pi'. According to requirements, assignments
    evaluate the expression and store in variables['name'].
    """
    dsl_code = "var pi = 3.14159"
    model = get_model(dsl_code)
    
    # Import the generated output module to access its variables dictionary
    import output
    
    # The variable 'pi' should be stored in the variables dictionary
    assert 'pi' in output.variables
    assert output.variables['pi'] == pytest.approx(3.14159, rel=1e-9)


def test_multiple_variable_assignments():
    """
    Domain concept: Sequential variable assignments with different float values
    Expected: Multiple 'var' statements should each store their respective values in
    the variables dictionary. Variables should be accessible for later use.
    """
    dsl_code = """
    var pi = 3.14159
    var radius = 5.0
    """
    model = get_model(dsl_code)
    
    import output
    
    # Both variables should be stored
    assert 'pi' in output.variables
    assert 'radius' in output.variables
    assert output.variables['pi'] == pytest.approx(3.14159, rel=1e-9)
    assert output.variables['radius'] == pytest.approx(5.0, rel=1e-9)


def test_variable_reference_in_expression():
    """
    Domain concept: Using previously assigned variables in arithmetic expressions
    Expected: The calculation 'calc pi * radius * radius' should look up the values
    of 'pi' and 'radius' from the variables dictionary and compute the area of a circle.
    According to requirements, variable references use variables['name'] for lookup.
    """
    # The full sample includes variable assignments followed by a calculation using them
    output_lines = capture_output(open('output.py').read())
    lines = output_lines.strip().split('\n')
    
    # Last calculation: pi * radius * radius
    # pi = 3.14159, radius = 5.0
    # Expected: 3.14159 * 5.0 * 5.0 = 78.53975
    assert len(lines) >= 5
    result = float(lines[4])
    expected = 3.14159 * 5.0 * 5.0
    assert result == pytest.approx(expected, rel=1e-9)


def test_chained_multiplication():
    """
    Domain concept: Multiple multiplication operations in a single term
    Expected: The expression 'pi * radius * radius' demonstrates the paired-list pattern
    for Term, where multiple MulOp operators are chained left-to-right. The term has
    left=pi, op=['*', '*'], right=[radius, radius], which should evaluate as
    (pi * radius) * radius.
    """
    dsl_code = """
    var pi = 3.14159
    var radius = 5.0
    calc pi * radius * radius
    """
    model = get_model(dsl_code)
    
    # Verify the model structure matches the paired-list pattern
    calc_stmt = model.statements[2]
    term = calc_stmt.expression.left
    
    # Check that we have two multiplication operators
    assert len(term.op) == 2
    assert term.op[0] == '*'
    assert term.op[1] == '*'
    
    # Check that we have two right operands
    assert len(term.right) == 2


def test_complete_sample_output():
    """
    Domain concept: Complete execution of all statements in the sample model
    Expected: The generated code should execute all statements in order:
    1. Print 3.14 * 2 = 6.28
    2. Print -5 + 10 = 5.0
    3. Print +15 - 3 = 12.0
    4. Print -(10 + 5) = -15.0
    5. Assign pi = 3.14159
    6. Assign radius = 5.0
    7. Print pi * radius * radius = 78.53975
    
    This verifies that the sequential execution requirement is met.
    """
    output_lines = capture_output(open('output.py').read())
    lines = [line.strip() for line in output_lines.strip().split('\n') if line.strip()]
    
    # Should have exactly 5 print outputs (4 calcs + 1 calc with variables)
    assert len(lines) == 5
    
    # Verify each calculation result
    assert float(lines[0]) == pytest.approx(6.28, rel=1e-9)
    assert float(lines[1]) == pytest.approx(5.0, rel=1e-9)
    assert float(lines[2]) == pytest.approx(12.0, rel=1e-9)
    assert float(lines[3]) == pytest.approx(-15.0, rel=1e-9)
    assert float(lines[4]) == pytest.approx(78.53975, rel=1e-9)