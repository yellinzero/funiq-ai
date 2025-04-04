import pytest

from utils.common.singleton import Singleton


class ExampleSingleton(metaclass=Singleton):
    def __init__(self, value=None):
        self.value = value


def test_singleton_instance():
    # Create first instance
    instance1 = ExampleSingleton(value="test1")
    
    # Create second instance
    instance2 = ExampleSingleton(value="test2")
    
    # Both instances should be the same object
    assert instance1 is instance2
    
    # The value should be from the first initialization
    assert instance1.value == "test1"
    assert instance2.value == "test1"


def test_singleton_multiple_classes():
    class AnotherSingleton(metaclass=Singleton):
        def __init__(self, value=None):
            self.value = value
    
    # Different singleton classes should have different instances
    instance1 = ExampleSingleton()
    instance2 = AnotherSingleton()
    
    assert instance1 is not instance2 