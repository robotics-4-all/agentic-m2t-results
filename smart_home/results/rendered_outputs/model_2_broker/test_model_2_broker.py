"""
Test file for: model_2_broker.smarthome
Concepts tested: Metadata extraction, MQTT broker configuration, broker instantiation
Run with: pytest test_model_2_broker.py

This test file verifies the semantic correctness of code generated from a minimal
SmartEnvironment DSL model that defines only metadata and a single MQTT broker.
The sample exercises:
- Metadata block with name, version, and author
- MQTT broker declaration with host and port configuration
- Default values for optional broker parameters (ssl, basePath, webPath, webPort, auth)
"""
import pytest
from textx import metamodel_from_str
from output import (
    SmartEnvironment,
    HomebrokerBroker,
    MessageBroker,
    __version__,
    __author__
)

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

DSL_SAMPLE = """
Metadata
    name: BrokerSetup
    version: "1.0"
    author: "Alice"
end

Broker<MQTT> homeBroker
    host: "localhost"
    port: 1883
end
"""


def get_model(dsl_text: str):
    """Parse DSL text and return the model object."""
    mm = metamodel_from_str(GRAMMAR)
    return mm.model_from_str(dsl_text)


def test_metadata_extraction():
    """
    Domain concept: Metadata block provides project information
    Expected: Module-level constants (__version__, __author__) should match metadata values
    
    The requirements specify that Metadata should be rendered as module-level docstring
    and metadata constants (__version__, __author__, __email__). This test verifies that
    the metadata from the DSL model is correctly extracted and exposed as module constants.
    """
    # The generated code should have module-level constants matching the metadata
    assert __version__ == "1.0", "Module version should match metadata.version"
    assert __author__ == "Alice", "Module author should match metadata.author"


def test_mqtt_broker_class_exists():
    """
    Domain concept: MQTT broker configuration
    Expected: A concrete broker class should be generated for the MQTT broker definition
    
    The requirements specify that each MessageBroker type should generate a Python class
    inheriting from MessageBroker base class. The broker name 'homeBroker' should be
    converted to PascalCase class name 'HomebrokerBroker'.
    """
    # Verify the broker class exists and is a MessageBroker subclass
    assert issubclass(HomebrokerBroker, MessageBroker), \
        "HomebrokerBroker should inherit from MessageBroker base class"


def test_mqtt_broker_configuration():
    """
    Domain concept: MQTT broker connection parameters
    Expected: Broker instance should store host, port, and default values for optional parameters
    
    The requirements specify that broker configuration should include host, port, ssl, basePath,
    webPath, webPort, and auth. When optional parameters are not specified in the DSL, they
    should have sensible defaults (ssl=False, empty strings for paths, 0 for webPort, None for auth).
    """
    broker = HomebrokerBroker()
    
    # Verify required parameters from DSL
    assert broker.name == "homeBroker", "Broker name should match DSL declaration"
    assert broker.host == "localhost", "Broker host should match DSL value"
    assert broker.port == 1883, "Broker port should match DSL value"
    
    # Verify default values for optional parameters not specified in DSL
    assert broker.ssl == False, "SSL should default to False when not specified"
    assert broker.base_path == "", "basePath should default to empty string"
    assert broker.web_path == "", "webPath should default to empty string"
    assert broker.web_port == 0, "webPort should default to 0"
    assert broker.auth is None, "auth should be None when not specified"


def test_mqtt_broker_abstract_methods():
    """
    Domain concept: Message broker interface contract
    Expected: MQTT broker should implement connect() and disconnect() methods
    
    The requirements specify that MessageBroker is an abstract base class with
    connect() and disconnect() methods. Concrete broker implementations should
    provide these methods (even if they're placeholder implementations in generated code).
    """
    broker = HomebrokerBroker()
    
    # Verify the broker has the required interface methods
    assert hasattr(broker, 'connect'), "Broker should have connect() method"
    assert hasattr(broker, 'disconnect'), "Broker should have disconnect() method"
    assert callable(broker.connect), "connect should be callable"
    assert callable(broker.disconnect), "disconnect should be callable"
    
    # Verify methods can be called without errors (even if they're no-ops)
    try:
        broker.connect()
        broker.disconnect()
    except NotImplementedError:
        pytest.fail("Concrete broker should implement connect/disconnect, not raise NotImplementedError")


def test_smart_environment_initialization():
    """
    Domain concept: Smart environment orchestrator
    Expected: SmartEnvironment class should initialize with empty registries
    
    The requirements specify that SmartEnvironment is the main orchestrator class
    that manages entity_registry, automation_registry, and optionally rtmonitor.
    For this minimal sample (no entities or automations), registries should be empty.
    """
    env = SmartEnvironment()
    
    # Verify the orchestrator has the required registries
    assert hasattr(env, 'entity_registry'), "Environment should have entity_registry"
    assert hasattr(env, 'automation_registry'), "Environment should have automation_registry"
    assert isinstance(env.entity_registry, dict), "entity_registry should be a dict"
    assert isinstance(env.automation_registry, dict), "automation_registry should be a dict"
    
    # For this sample with no entities or automations, registries should be empty
    assert len(env.entity_registry) == 0, "entity_registry should be empty (no entities in sample)"
    assert len(env.automation_registry) == 0, "automation_registry should be empty (no automations in sample)"


def test_smart_environment_rtmonitor():
    """
    Domain concept: Runtime monitoring configuration
    Expected: RTMonitor should be None when not specified in DSL
    
    The requirements specify that RTMonitor is optional. When not present in the DSL model,
    the SmartEnvironment should have rtmonitor set to None.
    """
    env = SmartEnvironment()
    
    assert hasattr(env, 'rtmonitor'), "Environment should have rtmonitor attribute"
    assert env.rtmonitor is None, "rtmonitor should be None when not specified in DSL"


def test_smart_environment_simulation_step():
    """
    Domain concept: Simulation time stepping
    Expected: SmartEnvironment should support step() method for time-based simulation
    
    The requirements specify that SmartEnvironment should have a step() method that
    advances simulation time, updates entity attributes with generators, and checks
    automation conditions. For this minimal sample (no entities/automations), step()
    should execute without errors and update current_time.
    """
    env = SmartEnvironment()
    
    assert hasattr(env, 'step'), "Environment should have step() method"
    assert hasattr(env, 'current_time'), "Environment should track current_time"
    
    initial_time = env.current_time
    env.step(delta_time=1.0)
    
    assert env.current_time == initial_time + 1.0, \
        "step() should advance current_time by delta_time"


def test_smart_environment_run():
    """
    Domain concept: Multi-step simulation execution
    Expected: SmartEnvironment should support run() method for batch simulation
    
    The requirements specify that SmartEnvironment should have a run() method that
    executes multiple simulation steps. This is the main entry point for running
    the smart environment simulation.
    """
    env = SmartEnvironment()
    
    assert hasattr(env, 'run'), "Environment should have run() method"
    assert callable(env.run), "run should be callable"
    
    initial_time = env.current_time
    steps = 10
    env.run(steps=steps)
    
    # VERIFY: Assuming default delta_time=1.0 per step, current_time should advance by steps
    # The requirements don't specify the exact delta_time behavior in run(), but the
    # generated code shows step() is called with default delta_time=1.0
    assert env.current_time == initial_time + steps, \
        "run(steps=10) should advance current_time by 10 (assuming delta_time=1.0)"