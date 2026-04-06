"""
Test file for: model_3_sensor.smarthome
Concepts tested: Metadata extraction, MQTT broker configuration, sensor entity creation, 
                 entity attributes, broker-entity binding, entity type classification
Run with: pytest test_model_3_sensor.py
"""
import pytest
from textx import metamodel_from_str
from output import (
    SmartEnvironment,
    MqttbrokerBroker,
    Tempsensor,
    __version__
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
    name: SensorHome
    version: "1.0"
end

Broker<MQTT> mqttBroker
    host: "192.168.1.10"
    port: 1883
end

Entity tempSensor
    type: sensor
    topic: "home/bedroom/temperature"
    broker: mqttBroker
    freq: 10
    attributes:
        - temperature : float
        - humidity : float
end
"""


def get_model(dsl_text: str):
    """Parse DSL text and return the model object."""
    mm = metamodel_from_str(GRAMMAR)
    return mm.model_from_str(dsl_text)


def test_metadata_extraction():
    """
    Domain concept: Metadata block provides project information
    Expected: Module should expose metadata as constants (__version__) and docstring should contain system name
    """
    # The metadata name "SensorHome" and version "1.0" should be reflected in the generated module
    assert __version__ == "1.0", "Module version should match metadata version"
    
    # VERIFY: Check if module docstring contains the system name "SensorHome"
    # The requirements specify module-level docstring should include metadata.name


def test_mqtt_broker_configuration():
    """
    Domain concept: MQTT broker configuration with host and port
    Expected: MqttbrokerBroker class should be instantiated with correct host, port, and default values
    """
    broker = MqttbrokerBroker()
    
    # Broker name should match the DSL identifier
    assert broker.name == "mqttBroker", "Broker name should be 'mqttBroker'"
    
    # Host and port should match the DSL specification
    assert broker.host == "192.168.1.10", "Broker host should be '192.168.1.10'"
    assert broker.port == 1883, "Broker port should be 1883"
    
    # Default values for optional fields
    assert broker.ssl == False, "SSL should default to False when not specified"
    assert broker.base_path == "", "basePath should default to empty string"
    assert broker.web_path == "", "webPath should default to empty string"
    assert broker.web_port == 0, "webPort should default to 0"
    assert broker.auth is None, "auth should be None when not specified"


def test_broker_connection_interface():
    """
    Domain concept: Message brokers must implement connect/disconnect interface
    Expected: Broker instances should have connect() and disconnect() methods as per MessageBroker abstract class
    """
    broker = MqttbrokerBroker()
    
    # Verify broker has required interface methods
    assert hasattr(broker, 'connect'), "Broker should have connect() method"
    assert hasattr(broker, 'disconnect'), "Broker should have disconnect() method"
    assert callable(broker.connect), "connect should be callable"
    assert callable(broker.disconnect), "disconnect should be callable"
    
    # Methods should execute without error (even if they're stubs)
    broker.connect()
    broker.disconnect()


def test_sensor_entity_creation():
    """
    Domain concept: Sensor entity with type classification
    Expected: Entity class should be created with entity_type='sensor' and proper initialization
    """
    sensor = Tempsensor()
    
    # Entity name should match DSL identifier
    assert sensor.name == "tempSensor", "Entity name should be 'tempSensor'"
    
    # Entity type should be 'sensor' as specified in DSL
    assert sensor.entity_type == "sensor", "Entity type should be 'sensor'"
    
    # Topic should match DSL specification
    assert sensor.topic == "home/bedroom/temperature", "Topic should be 'home/bedroom/temperature'"
    
    # Frequency should match DSL specification
    assert sensor.freq == 10, "Frequency should be 10"


def test_entity_broker_binding():
    """
    Domain concept: Entity-to-broker binding via cross-reference
    Expected: Entity should store broker reference as broker name string for runtime resolution
    """
    sensor = Tempsensor()
    
    # Broker reference should be stored as the broker name string
    assert sensor.broker_name == "mqttBroker", "Entity should reference broker by name 'mqttBroker'"
    
    # VERIFY: In a full system, this name would be resolved to actual broker instance at runtime


def test_entity_float_attributes():
    """
    Domain concept: Simple attributes with float type on sensor entities
    Expected: Entity should have temperature and humidity attributes initialized to None (no default values specified)
    """
    sensor = Tempsensor()
    
    # Attributes should exist as instance variables
    assert hasattr(sensor, 'temperature'), "Sensor should have temperature attribute"
    assert hasattr(sensor, 'humidity'), "Sensor should have humidity attribute"
    
    # Type hints should indicate float type
    # VERIFY: Check type annotations if available
    
    # Initial values should be None (no default or generator specified in DSL)
    assert sensor.temperature is None, "temperature should initialize to None when no default specified"
    assert sensor.humidity is None, "humidity should initialize to None when no default specified"


def test_smart_environment_orchestrator():
    """
    Domain concept: SmartEnvironment orchestrator manages entity registry
    Expected: SmartEnvironment class should initialize with entity registry containing all defined entities
    """
    env = SmartEnvironment()
    
    # Entity registry should exist
    assert hasattr(env, 'entity_registry'), "SmartEnvironment should have entity_registry"
    assert isinstance(env.entity_registry, dict), "entity_registry should be a dictionary"
    
    # Entity registry should contain the tempSensor entity
    assert "tempSensor" in env.entity_registry, "entity_registry should contain 'tempSensor'"
    
    # The registered entity should be an instance of Tempsensor
    registered_sensor = env.entity_registry["tempSensor"]
    assert isinstance(registered_sensor, Tempsensor), "Registered entity should be Tempsensor instance"
    assert registered_sensor.name == "tempSensor", "Registered entity should have correct name"


def test_smart_environment_step_execution():
    """
    Domain concept: Simulation step execution for time-based progression
    Expected: SmartEnvironment.step() should advance simulation time and update entity states
    """
    env = SmartEnvironment()
    
    # Initial time should be 0
    assert env.current_time == 0.0, "Initial simulation time should be 0.0"
    
    # Step should advance time by delta_time
    env.step(delta_time=1.0)
    assert env.current_time == 1.0, "Time should advance by delta_time after step()"
    
    # Multiple steps should accumulate time
    env.step(delta_time=2.5)
    assert env.current_time == 3.5, "Time should accumulate across multiple steps"
    
    # VERIFY: In models with generators, step() would update entity attribute values


def test_automation_registry_initialization():
    """
    Domain concept: Automation registry for event-driven rules
    Expected: SmartEnvironment should have automation_registry (empty in this sample as no automations defined)
    """
    env = SmartEnvironment()
    
    # Automation registry should exist
    assert hasattr(env, 'automation_registry'), "SmartEnvironment should have automation_registry"
    assert isinstance(env.automation_registry, dict), "automation_registry should be a dictionary"
    
    # This sample has no automations, so registry should be empty
    assert len(env.automation_registry) == 0, "automation_registry should be empty when no automations defined"