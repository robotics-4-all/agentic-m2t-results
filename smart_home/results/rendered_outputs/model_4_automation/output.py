



"""
SimpleAutomation - Smart Home Automation System

Version: 1.0

Generated from SmartEnvironment DSL model.
"""


__version__ = "1.0"

from typing import List, Dict, Optional, Union, Any, Tuple
from abc import ABC, abstractmethod
from datetime import time, datetime
import random
import math
from collections import deque


class MessageBroker(ABC):
    """Abstract base class for message brokers."""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the broker."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the broker."""
        pass


class Authentication(ABC):
    """Abstract base class for authentication strategies."""
    
    @abstractmethod
    def get_credentials(self) -> Dict[str, Any]:
        """Return authentication credentials."""
        pass


class ValueGenerator(ABC):
    """Abstract base class for value generators."""
    
    @abstractmethod
    def generate(self) -> Any:
        """Generate and return the next value."""
        pass


class NoiseDefinition(ABC):
    """Abstract base class for noise generators."""
    
    @abstractmethod
    def apply(self, value: float) -> float:
        """Apply noise to the given value."""
        pass


class NoiseWrapper(ValueGenerator):
    """Wrapper that applies noise to a generator's output."""
    
    def __init__(self, generator: ValueGenerator, noise: NoiseDefinition) -> None:
        self.generator = generator
        self.noise = noise
    
    def generate(self) -> Any:
        """Generate value and apply noise."""
        value = self.generator.generate()
        return self.noise.apply(value)


class NumericFunction(ABC):
    """Abstract base class for numeric functions."""
    
    @abstractmethod
    def calculate(self, entity_registry: Dict[str, Any]) -> float:
        """Calculate and return the function result."""
        pass


class Condition(ABC):
    """Abstract base class for conditions."""
    
    @abstractmethod
    def evaluate(self, entity_registry: Dict[str, Any]) -> bool:
        """Evaluate the condition and return True or False."""
        pass


class Action(ABC):
    """Abstract base class for actions."""
    
    @abstractmethod
    def execute(self, entity_registry: Dict[str, Any]) -> None:
        """Execute the action."""
        pass


# Attribute reference classes
class SimpleAttributeReference:
    """Reference to a simple entity attribute."""
    
    def __init__(self, entity_name: str, attribute_name: str) -> None:
        self.entity_name = entity_name
        self.attribute_name = attribute_name
    
    def get_value(self, entity_registry: Dict[str, Any]) -> Any:
        """Retrieve the current attribute value."""
        entity = entity_registry.get(self.entity_name)
        if entity:
            return getattr(entity, self.attribute_name, None)
        return None


class ListAttributeReference:
    """Reference to a list element in an entity attribute."""
    
    def __init__(self, entity_name: str, attribute_name: str, index: int) -> None:
        self.entity_name = entity_name
        self.attribute_name = attribute_name
        self.index = index
    
    def get_value(self, entity_registry: Dict[str, Any]) -> Any:
        """Retrieve the list element value."""
        entity = entity_registry.get(self.entity_name)
        if entity:
            attr_value = getattr(entity, self.attribute_name, None)
            if isinstance(attr_value, list) and 0 <= self.index < len(attr_value):
                return attr_value[self.index]
        return None


class DictAttributeReference:
    """Reference to a dictionary value in an entity attribute."""
    
    def __init__(self, entity_name: str, attribute_name: str, key: str) -> None:
        self.entity_name = entity_name
        self.attribute_name = attribute_name
        self.key = key
    
    def get_value(self, entity_registry: Dict[str, Any]) -> Any:
        """Retrieve the dictionary value."""
        entity = entity_registry.get(self.entity_name)
        if entity:
            attr_value = getattr(entity, self.attribute_name, None)
            if isinstance(attr_value, dict):
                return attr_value.get(self.key)
        return None


# Numeric function classes
class StandardDeviation(NumericFunction):
    """Calculate standard deviation over attribute history."""
    
    def __init__(self, attribute_name: str, size: int) -> None:
        self.attribute_name = attribute_name
        self.size = size
        self.history: deque = deque(maxlen=size)
    
    def calculate(self, entity_registry: Dict[str, Any]) -> float:
        """Calculate standard deviation."""
        if len(self.history) < 2:
            return 0.0
        mean_val = sum(self.history) / len(self.history)
        variance = sum((x - mean_val) ** 2 for x in self.history) / len(self.history)
        return math.sqrt(variance)


class Variance(NumericFunction):
    """Calculate variance over attribute history."""
    
    def __init__(self, attribute_name: str, size: int) -> None:
        self.attribute_name = attribute_name
        self.size = size
        self.history: deque = deque(maxlen=size)
    
    def calculate(self, entity_registry: Dict[str, Any]) -> float:
        """Calculate variance."""
        if len(self.history) < 2:
            return 0.0
        mean_val = sum(self.history) / len(self.history)
        return sum((x - mean_val) ** 2 for x in self.history) / len(self.history)


class Mean(NumericFunction):
    """Calculate mean over attribute history."""
    
    def __init__(self, attribute_name: str, size: int) -> None:
        self.attribute_name = attribute_name
        self.size = size
        self.history: deque = deque(maxlen=size)
    
    def calculate(self, entity_registry: Dict[str, Any]) -> float:
        """Calculate mean."""
        if not self.history:
            return 0.0
        return sum(self.history) / len(self.history)


class Minimum(NumericFunction):
    """Calculate minimum over attribute history."""
    
    def __init__(self, attribute_name: str, size: int) -> None:
        self.attribute_name = attribute_name
        self.size = size
        self.history: deque = deque(maxlen=size)
    
    def calculate(self, entity_registry: Dict[str, Any]) -> float:
        """Calculate minimum."""
        if not self.history:
            return 0.0
        return min(self.history)


class Maximum(NumericFunction):
    """Calculate maximum over attribute history."""
    
    def __init__(self, attribute_name: str, size: int) -> None:
        self.attribute_name = attribute_name
        self.size = size
        self.history: deque = deque(maxlen=size)
    
    def calculate(self, entity_registry: Dict[str, Any]) -> float:
        """Calculate maximum."""
        if not self.history:
            return 0.0
        return max(self.history)


class Multiplication(NumericFunction):
    """Multiply multiple attribute values."""
    
    def __init__(self, attribute_names: List[str]) -> None:
        self.attribute_names = attribute_names
    
    def calculate(self, entity_registry: Dict[str, Any]) -> float:
        """Calculate product of attributes."""
        result = 1.0
        for attr_name in self.attribute_names:
            # Attribute names need entity resolution in real implementation
            result *= 1.0  # Placeholder
        return result


# Math expression classes
class MathExpression:
    """Mathematical expression with addition/subtraction operators."""
    
    def __init__(self, *args) -> None:
        """Initialize with left term and optional (operator, right term) pairs."""
        self.left = args[0]
        self.operations: List[Tuple[str, Any]] = []
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                self.operations.append((args[i], args[i + 1]))
    
    def evaluate(self, entity_registry: Dict[str, Any]) -> float:
        """Evaluate the expression."""
        result = self._evaluate_term(self.left, entity_registry)
        for operator, right_term in self.operations:
            right_value = self._evaluate_term(right_term, entity_registry)
            if operator == '+':
                result += right_value
            elif operator == '-':
                result -= right_value
        return result
    
    def _evaluate_term(self, term: Any, entity_registry: Dict[str, Any]) -> float:
        """Evaluate a term (could be MathTerm or number)."""
        if isinstance(term, (int, float)):
            return float(term)
        elif hasattr(term, 'evaluate'):
            return term.evaluate(entity_registry)
        return 0.0


class MathTerm:
    """Mathematical term with multiplication/division operators."""
    
    def __init__(self, *args) -> None:
        """Initialize with left factor and optional (operator, right factor) pairs."""
        self.left = args[0]
        self.operations: List[Tuple[str, Any]] = []
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                self.operations.append((args[i], args[i + 1]))
    
    def evaluate(self, entity_registry: Dict[str, Any]) -> float:
        """Evaluate the term."""
        result = self._evaluate_factor(self.left, entity_registry)
        for operator, right_factor in self.operations:
            right_value = self._evaluate_factor(right_factor, entity_registry)
            if operator == '*':
                result *= right_value
            elif operator == '/' and right_value != 0:
                result /= right_value
        return result
    
    def _evaluate_factor(self, factor: Any, entity_registry: Dict[str, Any]) -> float:
        """Evaluate a factor (could be number, reference, function, or expression)."""
        if isinstance(factor, (int, float)):
            return float(factor)
        elif isinstance(factor, (SimpleAttributeReference, ListAttributeReference, DictAttributeReference)):
            value = factor.get_value(entity_registry)
            return float(value) if value is not None else 0.0
        elif isinstance(factor, NumericFunction):
            return factor.calculate(entity_registry)
        elif hasattr(factor, 'evaluate'):
            return factor.evaluate(entity_registry)
        return 0.0


# Condition classes
class ConditionExpression(Condition):
    """Compound condition with logical operators."""
    
    def __init__(self, *args) -> None:
        """Initialize with left term and optional (operator, right term) pairs."""
        self.left = args[0]
        self.operations: List[Tuple[str, Any]] = []
        for i in range(1, len(args), 2):
            if i + 1 < len(args):
                self.operations.append((args[i], args[i + 1]))
    
    def evaluate(self, entity_registry: Dict[str, Any]) -> bool:
        """Evaluate the condition."""
        result = self._evaluate_term(self.left, entity_registry)
        for operator, right_term in self.operations:
            right_value = self._evaluate_term(right_term, entity_registry)
            if operator == 'and':
                result = result and right_value
            elif operator == 'or':
                result = result or right_value
        return result
    
    def _evaluate_term(self, term: Any, entity_registry: Dict[str, Any]) -> bool:
        """Evaluate a condition term."""
        if hasattr(term, 'evaluate'):
            return term.evaluate(entity_registry)
        return False


class NumericCondition(Condition):
    """Numeric comparison condition."""
    
    def __init__(self, left: Any, operator: str, right: Any) -> None:
        self.left = left
        self.operator = operator
        self.right = right
    
    def evaluate(self, entity_registry: Dict[str, Any]) -> bool:
        """Evaluate numeric comparison."""
        left_val = self.left.evaluate(entity_registry) if hasattr(self.left, 'evaluate') else float(self.left)
        right_val = self.right.evaluate(entity_registry) if hasattr(self.right, 'evaluate') else float(self.right)
        
        if self.operator == '==':
            return left_val == right_val
        elif self.operator == '!=':
            return left_val != right_val
        elif self.operator == '<':
            return left_val < right_val
        elif self.operator == '>':
            return left_val > right_val
        elif self.operator == '<=':
            return left_val <= right_val
        elif self.operator == '>=':
            return left_val >= right_val
        return False


class StringCondition(Condition):
    """String comparison condition."""
    
    def __init__(self, left: Any, operator: str, right: str) -> None:
        self.left = left
        self.operator = operator
        self.right = right
    
    def evaluate(self, entity_registry: Dict[str, Any]) -> bool:
        """Evaluate string comparison."""
        left_val = str(self.left.get_value(entity_registry) if hasattr(self.left, 'get_value') else self.left)
        
        if self.operator == '==':
            return left_val == self.right
        elif self.operator == '!=':
            return left_val != self.right
        elif self.operator == 'contains':
            return self.right in left_val
        elif self.operator == 'startswith':
            return left_val.startswith(self.right)
        elif self.operator == 'endswith':
            return left_val.endswith(self.right)
        return False


class BooleanCondition(Condition):
    """Boolean comparison condition."""
    
    def __init__(self, left: Any, operator: str, right: bool) -> None:
        self.left = left
        self.operator = operator
        self.right = right
    
    def evaluate(self, entity_registry: Dict[str, Any]) -> bool:
        """Evaluate boolean comparison."""
        left_val = self.left.get_value(entity_registry) if hasattr(self.left, 'get_value') else self.left
        
        if self.operator == '==':
            return left_val == self.right
        elif self.operator == '!=':
            return left_val != self.right
        return False


class ListCondition(Condition):
    """List comparison condition."""
    
    def __init__(self, left: Any, operator: str, right: List[Any]) -> None:
        self.left = left
        self.operator = operator
        self.right = right
    
    def evaluate(self, entity_registry: Dict[str, Any]) -> bool:
        """Evaluate list comparison."""
        left_val = self.left.get_value(entity_registry) if hasattr(self.left, 'get_value') else self.left
        
        if self.operator == '==':
            return left_val == self.right
        elif self.operator == '!=':
            return left_val != self.right
        elif self.operator == 'in':
            return left_val in self.right
        return False


class DictionaryCondition(Condition):
    """Dictionary comparison condition."""
    
    def __init__(self, left: Any, operator: str, right: Dict[str, Any]) -> None:
        self.left = left
        self.operator = operator
        self.right = right
    
    def evaluate(self, entity_registry: Dict[str, Any]) -> bool:
        """Evaluate dictionary comparison."""
        left_val = self.left.get_value(entity_registry) if hasattr(self.left, 'get_value') else self.left
        
        if self.operator == '==':
            return left_val == self.right
        elif self.operator == '!=':
            return left_val != self.right
        elif self.operator == 'hasKey':
            return isinstance(left_val, dict) and any(k in left_val for k in self.right.keys())
        return False


class TimeCondition(Condition):
    """Time comparison condition."""
    
    def __init__(self, left: Any, operator: str, right: time) -> None:
        self.left = left
        self.operator = operator
        self.right = right
    
    def evaluate(self, entity_registry: Dict[str, Any]) -> bool:
        """Evaluate time comparison."""
        left_val = self.left.get_value(entity_registry) if hasattr(self.left, 'get_value') else self.left
        
        if not isinstance(left_val, time):
            return False
        
        if self.operator == '==' or self.operator == 'at':
            return left_val == self.right
        elif self.operator == '!=':
            return left_val != self.right
        elif self.operator == '<' or self.operator == 'before':
            return left_val < self.right
        elif self.operator == '>' or self.operator == 'after':
            return left_val > self.right
        return False


class RangeCondition(Condition):
    """Range condition (value between min and max)."""
    
    def __init__(self, value: Any, min_val: float, max_val: float) -> None:
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
    
    def evaluate(self, entity_registry: Dict[str, Any]) -> bool:
        """Evaluate range condition."""
        val = self.value.get_value(entity_registry) if hasattr(self.value, 'get_value') else self.value
        try:
            val = float(val)
            return self.min_val <= val <= self.max_val
        except (TypeError, ValueError):
            return False


# Action classes
class IntAction(Action):
    """Action that sets an integer attribute value."""
    
    def __init__(self, entity_name: str, attribute_name: str, value: int) -> None:
        self.entity_name = entity_name
        self.attribute_name = attribute_name
        self.value = value
    
    def execute(self, entity_registry: Dict[str, Any]) -> None:
        """Execute the action by setting the attribute value."""
        entity = entity_registry.get(self.entity_name)
        if entity:
            setattr(entity, self.attribute_name, self.value)


class FloatAction(Action):
    """Action that sets a float attribute value."""
    
    def __init__(self, entity_name: str, attribute_name: str, value: float) -> None:
        self.entity_name = entity_name
        self.attribute_name = attribute_name
        self.value = value
    
    def execute(self, entity_registry: Dict[str, Any]) -> None:
        """Execute the action by setting the attribute value."""
        entity = entity_registry.get(self.entity_name)
        if entity:
            setattr(entity, self.attribute_name, self.value)


class BoolAction(Action):
    """Action that sets a boolean attribute value."""
    
    def __init__(self, entity_name: str, attribute_name: str, value: bool) -> None:
        self.entity_name = entity_name
        self.attribute_name = attribute_name
        self.value = value
    
    def execute(self, entity_registry: Dict[str, Any]) -> None:
        """Execute the action by setting the attribute value."""
        entity = entity_registry.get(self.entity_name)
        if entity:
            setattr(entity, self.attribute_name, self.value)


class StringAction(Action):
    """Action that sets a string attribute value."""
    
    def __init__(self, entity_name: str, attribute_name: str, value: str) -> None:
        self.entity_name = entity_name
        self.attribute_name = attribute_name
        self.value = value
    
    def execute(self, entity_registry: Dict[str, Any]) -> None:
        """Execute the action by setting the attribute value."""
        entity = entity_registry.get(self.entity_name)
        if entity:
            setattr(entity, self.attribute_name, self.value)


class ListAction(Action):
    """Action that sets a list attribute value."""
    
    def __init__(self, entity_name: str, attribute_name: str, value: List[Any]) -> None:
        self.entity_name = entity_name
        self.attribute_name = attribute_name
        self.value = value
    
    def execute(self, entity_registry: Dict[str, Any]) -> None:
        """Execute the action by setting the attribute value."""
        entity = entity_registry.get(self.entity_name)
        if entity:
            setattr(entity, self.attribute_name, self.value)


class DictAction(Action):
    """Action that sets a dictionary attribute value."""
    
    def __init__(self, entity_name: str, attribute_name: str, value: Dict[str, Any]) -> None:
        self.entity_name = entity_name
        self.attribute_name = attribute_name
        self.value = value
    
    def execute(self, entity_registry: Dict[str, Any]) -> None:
        """Execute the action by setting the attribute value."""
        entity = entity_registry.get(self.entity_name)
        if entity:
            setattr(entity, self.attribute_name, self.value)


# Authentication classes


# Broker classes
class MqttbrokerBroker(MessageBroker):
    """MQTT broker implementation."""
    
    def __init__(self) -> None:
        self.name = "mqttBroker"
        self.host = "localhost"
        self.port = 1883
        self.ssl = False
        self.base_path = ""
        self.web_path = ""
        self.web_port = 0
        self.auth = None
    
    def connect(self) -> None:
        """Establish MQTT connection."""
        # Connection logic would go here
        pass
    
    def disconnect(self) -> None:
        """Close MQTT connection."""
        # Disconnection logic would go here
        pass


# Generator classes




# Noise classes




# Entity classes

class Thermostat:
    """Sensor entity: thermostat"""
    
    def __init__(self) -> None:
        self.name = "thermostat"
        self.entity_type = "sensor"
        self.topic = "home/thermostat"
        self.freq = 0.0
        self.broker_name = "mqttBroker"
        
        # Initialize attributes
        self.temperature: float = None
        



class Heater:
    """Actuator entity: heater"""
    
    def __init__(self) -> None:
        self.name = "heater"
        self.entity_type = "actuator"
        self.topic = "home/heater"
        self.freq = 0.0
        self.broker_name = "mqttBroker"
        
        # Initialize attributes
        self.power: bool = None
        



# Automation classes

class TurnonheaterAutomation:
    """Automation: turnOnHeater"""
    
    def __init__(self) -> None:
        self.name = "turnOnHeater"
        self.freq = 0.0
        self.enabled = True
        self.continuous = False
        self.check_once = False
        self.delay = 0.0
        self.has_triggered = False
        self.last_check_time = 0.0
        
        # Condition
        self.condition = NumericCondition(MathExpression(MathTerm(1)), "==", MathExpression(MathTerm(1)))
        
        # Actions
        self.actions = [
            BoolAction("heater", "power", True)
        ]
        
        # Orchestration references (automation names)
        self.starts = []
        self.stops = []
        self.after = []
    
    def check_and_execute(self, entity_registry: Dict[str, Any], automation_registry: Dict[str, Any], current_time: float) -> bool:
        """Check condition and execute actions if triggered."""
        # Check if automation is enabled
        if not self.enabled:
            return False
        
        # Check if already triggered and checkOnce is set
        if self.check_once and self.has_triggered:
            return False
        
        # Check frequency constraint
        if self.freq > 0 and (current_time - self.last_check_time) < (1.0 / self.freq):
            return False
        
        self.last_check_time = current_time
        
        # Check after dependencies
        for after_name in self.after:
            after_auto = automation_registry.get(after_name)
            if after_auto and not after_auto.has_triggered:
                return False
        
        # Evaluate condition
        try:
            condition_met = self.condition.evaluate(entity_registry)
        except Exception:
            condition_met = False
        
        if condition_met:
            # Apply delay if specified
            if self.delay > 0:
                import time
                time.sleep(self.delay)
            
            # Execute actions
            for action in self.actions:
                try:
                    action.execute(entity_registry)
                except Exception:
                    pass
            
            # Mark as triggered
            self.has_triggered = True
            
            # Handle starts orchestration
            for start_name in self.starts:
                start_auto = automation_registry.get(start_name)
                if start_auto:
                    start_auto.enabled = True
            
            # Handle stops orchestration
            for stop_name in self.stops:
                stop_auto = automation_registry.get(stop_name)
                if stop_auto:
                    stop_auto.enabled = False
            
            # Reset has_triggered if continuous
            if self.continuous:
                self.has_triggered = False
            
            return True
        
        return False



# RTMonitor class

# Smart Environment orchestrator
class SmartEnvironment:
    """Main orchestrator for the smart home environment."""
    
    def __init__(self) -> None:
        # Initialize entity registry
        self.entity_registry: Dict[str, Any] = {}
        
        self.entity_registry["thermostat"] = Thermostat()
        
        self.entity_registry["heater"] = Heater()
        
        
        # Initialize automation registry
        self.automation_registry: Dict[str, Any] = {}
        
        self.automation_registry["turnOnHeater"] = TurnonheaterAutomation()
        
        
        # Initialize RTMonitor if present
        self.rtmonitor = None
        
        
        self.current_time = 0.0
    
    def step(self, delta_time: float = 1.0) -> None:
        """Execute one simulation step."""
        self.current_time += delta_time
        
        # Update entity attributes with generators
        for entity_name, entity in self.entity_registry.items():
            for attr_name in dir(entity):
                if attr_name.endswith('_generator'):
                    base_name = attr_name[:-10]  # Remove '_generator' suffix
                    generator = getattr(entity, attr_name)
                    new_value = generator.generate()
                    setattr(entity, base_name, new_value)
        
        # Check and execute automations
        for automation_name, automation in self.automation_registry.items():
            automation.check_and_execute(self.entity_registry, self.automation_registry, self.current_time)
    
    def run(self, steps: int = 100) -> None:
        """Run the simulation for a specified number of steps."""
        for _ in range(steps):
            self.step()


if __name__ == "__main__":
    # Create and run the smart environment
    env = SmartEnvironment()
    env.run(steps=100)