"""
Test file for: model_5_auth_broker.smarthome
Concepts tested: AMQP broker with authentication, Redis broker with authentication, entity with broker binding, plain authentication, API key authentication
Run with: pytest test_model_5_auth_broker.py
"""
import pytest
from textx import metamodel_from_str
from output import (
    AmqpbrokerBroker,
    RedisbrokerBroker,
    Doorsensor,
    SmartEnvironment,
    AuthPlain,
    AuthApiKey
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
    name: SecureBrokers
    version: "2.0"
    author: "Bob"
    email: "bob@example.com"
    description: "Demonstrates multiple brokers with authentication"
end

Broker<AMQP> amqpBroker
    host: "amqp.example.com"
    port: 5672
    vhost: "/production"
    topicExchange: "sensors"
    auth:
        username: "admin"
        password: "secret123"
end

Broker<Redis> redisBroker
    host: "redis.example.com"
    port: 6379
    db: 0
    ssl: true
    auth:
        key: "redis-api-key-abc"
end

Entity doorSensor
    type: sensor
    topic: "home/door"
    broker: amqpBroker
    attributes:
        - is_open : bool
        - last_opened : str
end
"""


def get_model(dsl_text: str):
    """Parse DSL text into a model object."""
    mm = metamodel_from_str(GRAMMAR)
    return mm.model_from_str(dsl_text)


def test_amqp_broker_configuration():
    """
    Domain concept: AMQP broker with connection parameters
    Expected: AmqpbrokerBroker class should be instantiated with host, port, vhost, 
    topicExchange values matching the DSL model. The broker should store these 
    configuration values for establishing AMQP connections.
    """
    broker = AmqpbrokerBroker()
    
    assert broker.name == "amqpBroker"
    assert broker.host == "amqp.example.com"
    assert broker.port == 5672
    assert broker.vhost == "/production"
    assert broker.topic_exchange == "sensors"
    assert broker.ssl is False  # Default value when not specified
    assert broker.rpc_exchange == ""  # Default value when not specified


def test_redis_broker_configuration():
    """
    Domain concept: Redis broker with SSL enabled
    Expected: RedisbrokerBroker class should be instantiated with host, port, db, 
    and ssl values matching the DSL model. SSL should be enabled as specified.
    """
    broker = RedisbrokerBroker()
    
    assert broker.name == "redisBroker"
    assert broker.host == "redis.example.com"
    assert broker.port == 6379
    assert broker.db == 0
    assert broker.ssl is True


def test_plain_authentication():
    """
    Domain concept: Plain username/password authentication for AMQP broker
    Expected: AuthPlain authentication object should store username and password 
    credentials and provide them via get_credentials() method as a dictionary.
    """
    broker = AmqpbrokerBroker()
    auth = broker.auth
    
    assert isinstance(auth, AuthPlain)
    assert auth.username == "admin"
    assert auth.password == "secret123"
    
    credentials = auth.get_credentials()
    assert credentials["username"] == "admin"
    assert credentials["password"] == "secret123"


def test_api_key_authentication():
    """
    Domain concept: API key authentication for Redis broker
    Expected: AuthApiKey authentication object should store the API key and 
    provide it via get_credentials() method as a dictionary with 'api_key' field.
    """
    broker = RedisbrokerBroker()
    auth = broker.auth
    
    assert isinstance(auth, AuthApiKey)
    assert auth.key == "redis-api-key-abc"
    
    credentials = auth.get_credentials()
    assert credentials["api_key"] == "redis-api-key-abc"


def test_entity_with_broker_binding():
    """
    Domain concept: Entity bound to a specific message broker
    Expected: Doorsensor entity should be configured with type 'sensor', topic 
    'home/door', and broker reference 'amqpBroker'. The broker_name should match 
    the AMQP broker defined in the model.
    """
    entity = Doorsensor()
    
    assert entity.name == "doorSensor"
    assert entity.entity_type == "sensor"
    assert entity.topic == "home/door"
    assert entity.broker_name == "amqpBroker"
    assert entity.freq == 0.0  # Default value when not specified


def test_entity_attributes():
    """
    Domain concept: Entity with typed attributes (bool and str)
    Expected: Doorsensor entity should have is_open (bool) and last_opened (str) 
    attributes initialized to None (no default values specified in DSL).
    """
    entity = Doorsensor()
    
    # Attributes should exist as instance variables
    assert hasattr(entity, 'is_open')
    assert hasattr(entity, 'last_opened')
    
    # No default values specified, so should be None
    assert entity.is_open is None
    assert entity.last_opened is None


def test_broker_connect_disconnect_interface():
    """
    Domain concept: Message broker connection lifecycle
    Expected: Both AMQP and Redis brokers should implement connect() and disconnect() 
    methods as defined by the MessageBroker abstract base class. These methods should 
    be callable without errors (actual connection logic is implementation-specific).
    """
    amqp_broker = AmqpbrokerBroker()
    redis_broker = RedisbrokerBroker()
    
    # Should have connect and disconnect methods
    assert hasattr(amqp_broker, 'connect')
    assert hasattr(amqp_broker, 'disconnect')
    assert hasattr(redis_broker, 'connect')
    assert hasattr(redis_broker, 'disconnect')
    
    # Should be callable without raising exceptions
    amqp_broker.connect()
    amqp_broker.disconnect()
    redis_broker.connect()
    redis_broker.disconnect()


def test_smart_environment_initialization():
    """
    Domain concept: Smart environment orchestrator with entity registry
    Expected: SmartEnvironment should initialize with an entity registry containing 
    the doorSensor entity. The entity should be accessible by name in the registry.
    """
    env = SmartEnvironment()
    
    # Entity registry should exist
    assert hasattr(env, 'entity_registry')
    assert isinstance(env.entity_registry, dict)
    
    # doorSensor should be registered
    assert "doorSensor" in env.entity_registry
    
    # Registered entity should be a Doorsensor instance
    entity = env.entity_registry["doorSensor"]
    assert isinstance(entity, Doorsensor)
    assert entity.name == "doorSensor"


def test_metadata_in_module():
    """
    Domain concept: Project metadata embedded in generated module
    Expected: The generated module should contain metadata constants (__version__, 
    __author__, __email__) matching the values from the Metadata block in the DSL.
    """
    import output
    
    assert output.__version__ == "2.0"
    assert output.__author__ == "Bob"
    assert output.__email__ == "bob@example.com"