"""Observer classes for PlanGEN visualization."""

from abc import ABC, abstractmethod
from typing import Any
from typing_extensions import Self


class PlanObserver(ABC):
    """Observer interface for receiving plan update notifications."""

    @abstractmethod
    def update(self: Self, plan_data: dict[str, Any]) -> None:
        """Update the observer with new plan data.

        Args:
            plan_data: Dictionary containing updated plan information
        """


class Observable:
    """Base class for objects that can be observed.

    Implements the subject part of the observer pattern.
    """

    def __init__(self: Self) -> None:
        """Initialize the observer."""
        self._observers: list[PlanObserver] = []

    def add_observer(self: Self, observer: PlanObserver) -> None:
        """Add an observer to the notification list.

        Args:
            observer: The observer to add
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self: Self, observer: PlanObserver) -> None:
        """Remove an observer from the notification list.

        Args:
            observer: The observer to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self: Self, plan_data: dict[str, Any]) -> None:
        """Notify all observers with updated plan data.

        Args:
            plan_data: Dictionary containing updated plan information
        """
        for observer in self._observers:
            observer.update(plan_data)
