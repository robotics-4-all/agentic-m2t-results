"""
Test file for: model_8_full_system.smarthome
Concepts tested: 
  - Multiple broker types (MQTT and AMQP) with authentication
  - RTMonitor configuration with broker reference
  - Sensor entities with value generators and noise
  - Actuator entities with simple attributes
  - Complex automations with conditions and actions
  - Automation orchestration (starts, stops, after dependencies)
  - Automation execution modes (continuous, checkOnce, delay)
  - Entity registry and automation registry management

Run with: pytest test_model_8_full_system.py
"""
import pytest
from output import (
    SmartEnvironment,
    MqttmainBroker,
    AmqpanalyticsBroker,
    AuthPlain,
    RTMonitor,
    Outdoortemp,
    Indoorclimate,
    Powermeter,
    Securitycam,
    Hvacunit,
    Smartblinds,
    Alarmpanel,
    ClimatecontrolAutomation,
    VentilationAutomation,
    EnergysaverAutomation,
    SecurityarmAutomation,
    IntruderalertAutomation,
    MorningroutineAutomation,
    GaussianGenerator,
    SawtoothGenerator,
    ConstantGenerator,
    LinearGenerator,
    GaussianNoise,
    NoiseWrapper
)


def test_mqtt_broker_configuration():
    # Domain concept: MQTT broker with SSL and authentication
    # Expected: Broker should be configured with correct host, port, SSL enabled,
    # base path, and plain authentication credentials
    broker = MqttmainBroker()
    
    assert broker.name == "mqttMain"
    assert broker.host == "mqtt.local"
    assert broker.port == 8883
    assert broker.ssl is True
    assert broker.base_path == "home"
    
    # Authentication should be AuthPlain with correct credentials
    assert isinstance(broker.auth, AuthPlain)
    credentials = broker.auth.get_credentials()
    assert credentials["username"] == "homeuser"
    assert credentials["password"] == "h0m3p@ss"


def test_amqp_broker_configuration():
    # Domain concept: AMQP broker with virtual host and exchange configuration
    # Expected: Broker should be configured with host, port, vhost, exchanges,
    # and authentication for analytics data routing
    broker = AmqpanalyticsBroker()
    
    assert broker.name == "amqpAnalytics"
    assert broker.host == "analytics.local"
    assert broker.port == 5672
    assert broker.vhost == "/analytics"
    assert broker.topic_exchange == "sensor_data"
    assert broker.rpc_exchange == "commands"
    assert broker.ssl is False
    
    # Authentication should be AuthPlain
    assert isinstance(broker.auth, AuthPlain)
    credentials = broker.auth.get_credentials()
    assert credentials["username"] == "analytics"
    assert credentials["password"] == "analyticspw"


def test_rtmonitor_configuration():
    # Domain concept: Runtime monitoring system with broker binding and topic routing
    # Expected: RTMonitor should reference the MQTT broker and configure
    # namespace and topic paths for events and logs
    rtmonitor = RTMonitor()
    
    assert rtmonitor.broker_name == "mqttMain"
    assert rtmonitor.namespace == "monitoring"
    assert rtmonitor.event_topic == "home/events"
    assert rtmonitor.logs_topic == "home/logs"


def test_sensor_with_generator_and_noise():
    # Domain concept: Sensor entity with value generators and noise application
    # Expected: outdoorTemp sensor should have gaussian generator with noise for
    # temperature and sawtooth generator for humidity, producing values within ranges
    sensor = Outdoortemp()
    
    assert sensor.name == "outdoorTemp"
    assert sensor.entity_type == "sensor"
    assert sensor.topic == "home/outdoor/temperature"
    assert sensor.freq == 30
    assert sensor.broker_name == "mqttMain"
    
    # outdoor_temp should use NoiseWrapper with GaussianGenerator and GaussianNoise
    assert isinstance(sensor.outdoor_temp_generator, NoiseWrapper)
    assert isinstance(sensor.outdoor_temp_generator.generator, GaussianGenerator)
    assert isinstance(sensor.outdoor_temp_generator.noise, GaussianNoise)
    
    # outdoor_humidity should use SawtoothGenerator
    assert isinstance(sensor.outdoor_humidity_generator, SawtoothGenerator)
    
    # Generate multiple values to verify they're within expected ranges
    # VERIFY: Exact values are random, but should be within generator bounds
    for _ in range(10):
        temp = sensor.outdoor_temp_generator.generate()
        humidity = sensor.outdoor_humidity_generator.generate()
        # Temperature should be roughly in range (with noise it can exceed slightly)
        assert -10.0 <= temp <= 60.0  # Generous bounds accounting for noise
        # Humidity should be in sawtooth range
        assert 30.0 <= humidity <= 95.0


def test_sensor_with_multiple_generator_types():
    # Domain concept: Sensor entity with different generator types (gaussian, constant, linear)
    # Expected: indoorClimate sensor should have gaussian for temperature,
    # constant for humidity, and linear for CO2
    sensor = Indoorclimate()
    
    assert sensor.name == "indoorClimate"
    assert sensor.entity_type == "sensor"
    assert sensor.freq == 10
    
    # Verify generator types
    assert isinstance(sensor.indoor_temp_generator, GaussianGenerator)
    assert isinstance(sensor.indoor_humidity_generator, ConstantGenerator)
    assert isinstance(sensor.co2_generator, LinearGenerator)
    
    # Constant generator should always return same value
    humidity1 = sensor.indoor_humidity_generator.generate()
    humidity2 = sensor.indoor_humidity_generator.generate()
    assert humidity1 == 50.0
    assert humidity2 == 50.0
    
    # Linear generator should increment by step
    co2_initial = sensor.co2_generator.current
    co2_1 = sensor.co2_generator.generate()
    co2_2 = sensor.co2_generator.generate()
    assert co2_2 == co2_1 + 5  # step is 5


def test_actuator_entities():
    # Domain concept: Actuator entities with simple attributes (no generators)
    # Expected: Actuator entities should have None-initialized attributes
    # that can be set by automation actions
    hvac = Hvacunit()
    blinds = Smartblinds()
    alarm = Alarmpanel()
    
    # HVAC actuator
    assert hvac.name == "hvacUnit"
    assert hvac.entity_type == "actuator"
    assert hvac.hvac_power is None
    assert hvac.target_temp is None
    assert hvac.hvac_mode is None
    assert hvac.fan_speed is None
    
    # Smart blinds actuator
    assert blinds.name == "smartBlinds"
    assert blinds.entity_type == "actuator"
    assert blinds.blind_position is None
    
    # Alarm panel actuator
    assert alarm.name == "alarmPanel"
    assert alarm.entity_type == "actuator"
    assert alarm.armed is None
    assert alarm.siren is None


def test_automation_with_continuous_mode():
    # Domain concept: Continuous automation that re-evaluates after triggering
    # Expected: climateControl automation should have continuous=True,
    # allowing it to trigger repeatedly when conditions are met
    automation = ClimatecontrolAutomation()
    
    assert automation.name == "climateControl"
    assert automation.enabled is True
    assert automation.continuous is True
    assert automation.check_once is False
    assert automation.freq == 30
    assert automation.delay == 0.0
    
    # Verify actions are configured
    assert len(automation.actions) == 3
    # VERIFY: Action types and values match the DSL specification
    # First action should set hvac_power to True
    # Second action should set target_temp to 22
    # Third action should set fan_speed to 2


def test_automation_with_checkonce_and_delay():
    # Domain concept: One-shot automation with delay before execution
    # Expected: securityArm automation should trigger once, wait 300 seconds,
    # then execute action to arm the alarm
    automation = SecurityarmAutomation()
    
    assert automation.name == "securityArm"
    assert automation.enabled is True
    assert automation.continuous is False
    assert automation.check_once is True
    assert automation.delay == 300.0  # 5 minutes
    assert automation.has_triggered is False
    
    # Verify single action
    assert len(automation.actions) == 1


def test_automation_orchestration_dependencies():
    # Domain concept: Automation orchestration with starts, stops, and after dependencies
    # Expected: Automations should reference other automations by name for
    # execution flow control
    energy_saver = EnergysaverAutomation()
    intruder_alert = IntruderalertAutomation()
    morning_routine = MorningroutineAutomation()
    
    # energySaver should run after climateControl
    assert "climateControl" in energy_saver.after
    assert len(energy_saver.after) == 1
    
    # intruderAlert should run after securityArm
    assert "securityArm" in intruder_alert.after
    assert len(intruder_alert.after) == 1
    
    # morningRoutine should start climateControl
    assert "climateControl" in morning_routine.starts
    assert len(morning_routine.starts) == 1


def test_smart_environment_initialization():
    # Domain concept: Main orchestrator that initializes all entities and automations
    # Expected: SmartEnvironment should create entity registry and automation registry
    # with all entities and automations from the model, plus RTMonitor
    env = SmartEnvironment()
    
    # Verify entity registry contains all entities
    assert "outdoorTemp" in env.entity_registry
    assert "indoorClimate" in env.entity_registry
    assert "powerMeter" in env.entity_registry
    assert "securityCam" in env.entity_registry
    assert "hvacUnit" in env.entity_registry
    assert "smartBlinds" in env.entity_registry
    assert "alarmPanel" in env.entity_registry
    assert len(env.entity_registry) == 7
    
    # Verify automation registry contains all automations
    assert "climateControl" in env.automation_registry
    assert "ventilation" in env.automation_registry
    assert "energySaver" in env.automation_registry
    assert "securityArm" in env.automation_registry
    assert "intruderAlert" in env.automation_registry
    assert "morningRoutine" in env.automation_registry
    assert len(env.automation_registry) == 6
    
    # Verify RTMonitor is initialized
    assert env.rtmonitor is not None
    assert isinstance(env.rtmonitor, RTMonitor)
    
    # Verify initial time
    assert env.current_time == 0.0


def test_smart_environment_step_execution():
    # Domain concept: Simulation step that updates entity values and checks automations
    # Expected: Each step should advance time, regenerate sensor values,
    # and evaluate automation conditions
    env = SmartEnvironment()
    
    # Get initial values
    outdoor_temp_initial = env.entity_registry["outdoorTemp"].outdoor_temp
    indoor_co2_initial = env.entity_registry["indoorClimate"].co2
    
    # Execute one step
    env.step(delta_time=1.0)
    
    # Time should advance
    assert env.current_time == 1.0
    
    # Sensor values should be regenerated
    outdoor_temp_new = env.entity_registry["outdoorTemp"].outdoor_temp
    indoor_co2_new = env.entity_registry["indoorClimate"].co2
    
    # VERIFY: Values should change (except constant generator)
    # Gaussian generator produces random values, so they should differ
    # Linear generator increments, so CO2 should increase
    assert indoor_co2_new == indoor_co2_initial + 5  # Linear step is 5
    
    # Constant humidity should not change
    humidity = env.entity_registry["indoorClimate"].indoor_humidity
    env.step(delta_time=1.0)
    humidity_new = env.entity_registry["indoorClimate"].indoor_humidity
    assert humidity == humidity_new == 50.0