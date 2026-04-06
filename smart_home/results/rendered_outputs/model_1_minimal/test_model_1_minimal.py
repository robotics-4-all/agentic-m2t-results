"""
Test file for: model_1_minimal.smarthome
Concepts tested: ['Metadata', 'SmartEnvironment initialization', 'Empty model structure']
Run with: pytest test_model_1_minimal.py

This test file validates the minimal SmartEnvironment model that contains only
metadata. It verifies that the generated code can handle an empty model with
no brokers, entities, or automations, and that metadata is correctly extracted
and used in the module.
"""
import pytest
from textx import metamodel_from_str
from output import SmartEnvironment

GRAMMAR = """
/*
    Smart Environment DSL Grammar
*/

// Model definition
SmartEnvironmentModel:
    imports*=Import
    (metadata=Metadata)?
    (rtmonitor=RTMonitor)?
    (
        brokers*=MessageBroker
        entities*=Entity
        automations*=Automation
    )#
;

// Metadata
Metadata:
    'Metadata'
    (
        ('name:' name=ID)
        ('version:' version=STRING)
        ('author:' author=STRING)?
        ('email:' email=STRING)?
        ('description:' description=STRING)?
    )#
    'end'
;

// Broker configurations
MessageBroker: AMQPBroker | MQTTBroker | RedisBroker;

AMQPBroker:
    'Broker<AMQP>' name=ID
    (
        ('host:' host=STRING)
        ('port:' port=INT)
        ('vhost:' vhost=STRING)?
        ('topicExchange:' topicExchange=STRING)?
        ('rpcExchange:' rpcExchange=STRING)?
        ('ssl:' ssl=BOOL)?
        ('auth:' auth=Authentication)?
    )#
    'end'
;

MQTTBroker:
    'Broker<MQTT>' name=ID
    (
        ('host:' host=STRING)
        ('port:' port=INT)
        ('ssl:' ssl=BOOL)?
        ('basePath:' basePath=STRING)?
        ('webPath:' webPath=STRING)?
        ('webPort:' webPort=INT)?
        ('auth:' auth=Authentication)?
    )#
    'end'
;

RedisBroker:
    'Broker<Redis>' name=ID
    (
        ('host:' host=STRING)
        ('port:' port=INT)
        ('db:' db=INT)?
        ('ssl:' ssl=BOOL)?
        ('auth:' auth=Authentication)?
    )#
    'end'
;

// Authentication
Authentication: AuthPlain | AuthApiKey | AuthCert;

AuthPlain:
    'username:' username=STRING
    'password:' password=STRING
;

AuthApiKey:
    'key:' key=STRING
;

AuthCert:
    ('cert:' cert=STRING) | ('certPath:' certPath=STRING)
;

// RTMonitor configuration
RTMonitor:
    'RTMonitor'
    (
        ('broker:' broker=[MessageBroker])
        ('namespace:' namespace=STRING)?
        ('eventTopic:' eventTopic=STRING)?
        ('logsTopic:' logsTopic=STRING)?
    )#
    'end'
;

// Entity definition
Entity:
    'Entity' name=ID
    (
        ('type:' type=EntityType)
        ('topic:' topic=STRING)
        ('description:' description=STRING)?
        ('freq:' freq=NUMBER)?
        ('broker:' broker=[MessageBroker])
        ('attributes:' '-' attributes*=Attribute['-'])?
    )#
    'end'
;

EntityType: 'sensor' | 'actuator' | 'hybrid';

// Attribute definitions
Attribute:
    AttributeWithGenerator | SimpleAttribute
;

SimpleAttribute:
    name=ID ':' type=AttributeType ('=' default=AttributeValue)?
;

AttributeWithGenerator:
    name=ID ':' type=AttributeType '->' generator=ValueGenerator ('with' 'noise' noise=NoiseDefinition)?
;

AttributeType:
    'int' | 'float' | 'bool' | 'str' | 'list' | 'dict' | 'time'
;

AttributeValue:
    NUMBER | STRING | BOOL | TimeValue | List | Dict
;

TimeValue:
    hour=INT ':' minute=INT (':' second=INT)?
;

Date:
    month=INT ':' day=INT ':' year=INT
;

List:
    '[' items*=ListItem[','] ']'
;

ListItem:
    NUMBER | STRING | BOOL | List | Dict | TimeValue | Date
;

Dict:
    '{' items*=DictItem[','] '}'
;

DictItem:
    name=STRING ':' value=DictValue
;

DictValue:
    NUMBER | STRING | BOOL | List | Dict | TimeValue | Date
;

// Value generators
ValueGenerator:
    ConstantGenerator |
    LinearGenerator |
    GaussianGenerator |
    SinusGenerator |
    SawtoothGenerator |
    ReplayGenerator
;

ConstantGenerator:
    'constant' '(' value=NUMBER ')'
;

LinearGenerator:
    'linear' '(' start=NUMBER ',' step=NUMBER ')'
;

GaussianGenerator:
    'gaussian' '(' value=NUMBER ',' maxValue=NUMBER ',' sigma=NUMBER ')'
;

SinusGenerator:
    'sinus' '(' dc=NUMBER ',' amplitude=NUMBER ',' step=NUMBER ')'
;

SawtoothGenerator:
    'saw' '(' min=NUMBER ',' max=NUMBER ',' step=NUMBER ')'
;

ReplayGenerator:
    'replay' '(' (values=List | filepath=STRING) (',' times=INT)? ')'
;

// Noise definitions
NoiseDefinition:
    UniformNoise | GaussianNoise
;

UniformNoise:
    'uniform' '(' min=NUMBER ',' max=NUMBER ')'
;

GaussianNoise:
    'gaussian' '(' mu=NUMBER ',' sigma=NUMBER ')'
;

// Advanced numeric functions
NumericFunction:
    StandardDeviation |
    Variance |
    Mean |
    Minimum |
    Maximum |
    Multiplication
;

StandardDeviation:
    'std' '(' attribute=[Attribute] ',' size=INT ')'
;

Variance:
    'var' '(' attribute=[Attribute] ',' size=INT ')'
;

Mean:
    'mean' '(' attribute=[Attribute] ',' size=INT ')'
;

Minimum:
    'min' '(' attribute=[Attribute] ',' size=INT ')'
;

Maximum:
    'max' '(' attribute=[Attribute] ',' size=INT ')'
;

Multiplication:
    'mul' '(' attributes+=[Attribute][','] ')'
;

// Conditions
Condition:
    left=ConditionTerm (operator=LogicalOperator right=ConditionTerm)*
;

ConditionTerm:
    '(' condition=Condition ')' | PrimitiveCondition | MathExpression
;

PrimitiveCondition:
    NumericCondition |
    StringCondition |
    BooleanCondition |
    ListCondition |
    DictionaryCondition |
    TimeCondition |
    RangeCondition
;

NumericCondition:
    left=MathExpression operator=NumericOperator right=MathExpression
;

StringCondition:
    left=AttributeReference operator=StringOperator right=STRING
;

BooleanCondition:
    left=AttributeReference operator=BooleanOperator right=BOOL
;

ListCondition:
    left=AttributeReference operator=ListOperator right=List
;

DictionaryCondition:
    left=AttributeReference operator=DictOperator right=Dict
;

TimeCondition:
    left=AttributeReference operator=TimeOperator right=TimeValue
;

RangeCondition:
    value=AttributeReference 'in' 'range' '[' min=NUMBER ',' max=NUMBER ']'
;

// Math expressions
MathExpression:
    left=MathTerm (operator=AddOperator right=MathTerm)*
;

MathTerm:
    left=MathFactor (operator=MulOperator right=MathFactor)*
;

MathFactor:
    '(' expr=MathExpression ')' | NUMBER | AttributeReference | NumericFunction
;

AttributeReference:
    SimpleAttributeReference | ListAttributeReference | DictAttributeReference
;

SimpleAttributeReference:
    entity=[Entity] '.' attribute=[Attribute]
;

ListAttributeReference:
    entity=[Entity] '.' attribute=[Attribute] '[' index=INT ']'
;

DictAttributeReference:
    entity=[Entity] '.' attribute=[Attribute] '[' key=STRING ']'
;

// Operators
StringOperator: '~' | '!~' | '==' | '!=' | 'has' | 'in' | 'not in';
NumericOperator: '>=' | '>' | '<=' | '<' | '==' | '!=';
LogicalOperator: 'AND' | 'OR' | 'NOT' | 'XOR' | 'NOR' | 'XNOR' | 'NAND';
BooleanOperator: 'is not' | 'is' | '==' | '!=';
ListOperator: '==' | '!=' | 'is' | 'is not' | 'in' | 'not in';
DictOperator: '==' | '!=' | 'is' | 'is not';
TimeOperator: '>=' | '>' | '<=' | '<' | '==' | '!=' | 'is not' | 'is';
AddOperator: '+' | '-';
MulOperator: '*' | '/';

// Actions
Action:
    IntAction | FloatAction | BoolAction | StringAction | ListAction | DictAction
;

IntAction:
    entity=[Entity] '.' attribute=[Attribute] ':' value=INT
;

FloatAction:
    entity=[Entity] '.' attribute=[Attribute] ':' value=FLOAT
;

BoolAction:
    entity=[Entity] '.' attribute=[Attribute] ':' value=BOOL
;

StringAction:
    entity=[Entity] '.' attribute=[Attribute] ':' value=STRING
;

ListAction:
    entity=[Entity] '.' attribute=[Attribute] ':' value=List
;

DictAction:
    entity=[Entity] '.' attribute=[Attribute] ':' value=Dict
;

// Automation
Automation:
    'Automation' name=ID
    (
        ('condition:' condition=Condition)
        ('description:' description=STRING)?
        ('actions:' '-' actions*=Action['-'])?
        ('freq:' freq=NUMBER)?
        ('enabled:' enabled=BOOL)?
        ('continuous:' continuous=BOOL)?
        ('checkOnce:' checkOnce=BOOL)?
        ('delay:' delay=FLOAT)?
        ('starts:' '-' starts*=[Automation]['-'])?
        ('stops:' '-' stops*=[Automation]['-'])?
        ('after:' '-' after*=[Automation]['-'])?
    )#
    'end'
;

// Utility to handle fully qualified names
FQN: ID ('.' ID)*;

// Comments
Comment: CommentLine | CommentBlock;
CommentLine: /\/\/.*?$/;
CommentBlock: /\/\*(.|\n)*?\*\//;

// Imports
Import: 'import' importURI=STRING;
"""


def get_model(dsl_text: str):
    """Parse DSL text and return the model object."""
    mm = metamodel_from_str(GRAMMAR)
    return mm.model_from_str(dsl_text)


def test_metadata_extraction():
    """
    Domain concept: Metadata block provides project information
    Expected: The generated module should use metadata.name and metadata.version
    to set module-level constants and documentation. For this sample, name is
    'MyHome' and version is '1.0'.
    """
    # The generated code should have __version__ constant set from metadata
    from output import __version__
    
    assert __version__ == "1.0", "Module version should match metadata.version"
    
    # VERIFY: The module docstring should contain the metadata.name 'MyHome'
    # This is typically in the module's __doc__ attribute
    import output
    assert output.__doc__ is not None, "Module should have a docstring"
    assert "MyHome" in output.__doc__, "Module docstring should contain the system name from metadata"


def test_empty_smart_environment_initialization():
    """
    Domain concept: SmartEnvironment orchestrator initialization with no components
    Expected: A minimal model with only metadata should create a SmartEnvironment
    instance with empty registries for entities, automations, and brokers. The
    system should be able to initialize without errors even when no IoT components
    are defined.
    """
    env = SmartEnvironment()
    
    # Entity registry should be empty (no entities defined in this model)
    assert isinstance(env.entity_registry, dict), "Entity registry should be a dictionary"
    assert len(env.entity_registry) == 0, "Entity registry should be empty for minimal model"
    
    # Automation registry should be empty (no automations defined)
    assert isinstance(env.automation_registry, dict), "Automation registry should be a dictionary"
    assert len(env.automation_registry) == 0, "Automation registry should be empty for minimal model"
    
    # RTMonitor should be None (not defined in this model)
    assert env.rtmonitor is None, "RTMonitor should be None when not defined in model"
    
    # Current time should be initialized to 0
    assert env.current_time == 0.0, "Current time should start at 0.0"


def test_empty_model_step_execution():
    """
    Domain concept: Simulation step execution with no entities or automations
    Expected: The step() method should execute without errors even when there are
    no entities to update or automations to check. This validates that the
    orchestrator handles edge cases gracefully.
    """
    env = SmartEnvironment()
    initial_time = env.current_time
    
    # Execute one simulation step
    env.step(delta_time=1.0)
    
    # Time should advance by delta_time
    assert env.current_time == initial_time + 1.0, "Current time should advance by delta_time"
    
    # No errors should occur even with empty registries
    # VERIFY: This test passes if no exceptions are raised


def test_empty_model_run_simulation():
    """
    Domain concept: Multi-step simulation execution with minimal model
    Expected: The run() method should execute multiple steps without errors,
    advancing the simulation time appropriately even when no entities or
    automations are present. This validates the main simulation loop.
    """
    env = SmartEnvironment()
    
    # Run simulation for 10 steps
    env.run(steps=10)
    
    # Time should have advanced by 10 steps (default delta_time is 1.0)
    assert env.current_time == 10.0, "After 10 steps with delta_time=1.0, current_time should be 10.0"
    
    # VERIFY: No exceptions should be raised during execution


def test_module_structure_completeness():
    """
    Domain concept: Generated module structure and required classes
    Expected: Even for a minimal model, the generated code should include all
    base classes and infrastructure needed for a complete smart environment
    system. This includes abstract base classes for brokers, authentication,
    generators, conditions, actions, etc.
    """
    import output
    
    # Check for essential abstract base classes
    assert hasattr(output, 'MessageBroker'), "Module should define MessageBroker base class"
    assert hasattr(output, 'Authentication'), "Module should define Authentication base class"
    assert hasattr(output, 'ValueGenerator'), "Module should define ValueGenerator base class"
    assert hasattr(output, 'NoiseDefinition'), "Module should define NoiseDefinition base class"
    assert hasattr(output, 'NumericFunction'), "Module should define NumericFunction base class"
    assert hasattr(output, 'Condition'), "Module should define Condition base class"
    assert hasattr(output, 'Action'), "Module should define Action base class"
    
    # Check for main orchestrator
    assert hasattr(output, 'SmartEnvironment'), "Module should define SmartEnvironment orchestrator"
    
    # VERIFY: All infrastructure classes are present even when not used in this minimal model


def test_smart_environment_interface():
    """
    Domain concept: SmartEnvironment public interface
    Expected: The SmartEnvironment class should expose the required methods
    for simulation control (step, run) and maintain the required state
    (entity_registry, automation_registry, rtmonitor, current_time).
    """
    env = SmartEnvironment()
    
    # Check required attributes exist
    assert hasattr(env, 'entity_registry'), "SmartEnvironment should have entity_registry attribute"
    assert hasattr(env, 'automation_registry'), "SmartEnvironment should have automation_registry attribute"
    assert hasattr(env, 'rtmonitor'), "SmartEnvironment should have rtmonitor attribute"
    assert hasattr(env, 'current_time'), "SmartEnvironment should have current_time attribute"
    
    # Check required methods exist
    assert hasattr(env, 'step'), "SmartEnvironment should have step method"
    assert callable(env.step), "step should be callable"
    assert hasattr(env, 'run'), "SmartEnvironment should have run method"
    assert callable(env.run), "run should be callable"


def test_module_imports():
    """
    Domain concept: Required Python imports for smart environment functionality
    Expected: The generated module should import all necessary standard library
    modules and typing constructs as specified in the requirements (typing, abc,
    datetime, random, math, collections).
    """
    import output
    
    # Check that the module can access typing constructs
    # (This is implicit if the module loads without errors, but we verify key classes exist)
    assert hasattr(output, 'MessageBroker'), "Module should define classes using ABC"
    assert hasattr(output, 'SmartEnvironment'), "Module should define main orchestrator class"
    
    # VERIFY: The module imports are correct if it loads without ImportError
    # The presence of classes using List, Dict, Optional, ABC, datetime.time, etc.
    # confirms the imports are in place