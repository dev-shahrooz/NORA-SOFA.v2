# nora/core/event_bus.py
from collections import defaultdict
from typing import Callable, Dict, List

class EventBus:
    def __init__(self):
        self._subs: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable):
        self._subs[topic].append(handler)

    def publish(self, topic: str, payload):
        for h in self._subs.get(topic, []):
            try:
                h(payload)
            except Exception as e:
                print(f"[EventBus] handler error on {topic}: {e}")