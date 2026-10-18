"""Process-local FIFO admission for bounded Codex subprocesses."""
from collections import deque
from contextlib import contextmanager
import threading
import uuid


class Scheduler:
    def __init__(self, capacity=2, max_waiting=10):
        if capacity < 1 or max_waiting < 1:
            raise ValueError('Invalid scheduler limits')
        self.capacity = capacity
        self.max_waiting = max_waiting
        self.condition = threading.Condition()
        self.waiting = deque()
        self.active = set()

    @contextmanager
    def slot(self, cancelled=lambda: False, changed=lambda state, position: None):
        token = uuid.uuid4().hex
        with self.condition:
            if len(self.waiting) >= self.max_waiting:
                raise ValueError('Codex 대기열이 가득 찼습니다. 진행 중 작업이 끝난 뒤 다시 시도하세요.')
            self.waiting.append(token)
        previous = None
        try:
            while True:
                if cancelled():
                    raise InterruptedError('사용자가 대기 작업을 중지했습니다.')
                with self.condition:
                    position = self.waiting.index(token) + 1
                    if position == 1 and len(self.active) < self.capacity:
                        self.waiting.popleft()
                        self.active.add(token)
                        self.condition.notify_all()
                        acquired = True
                    else:
                        acquired = False
                if acquired:
                    changed('running', 0)
                    break
                if previous != position:
                    changed('queued', position)
                    previous = position
                with self.condition:
                    self.condition.wait(timeout=.1)
            yield
        finally:
            with self.condition:
                if token in self.waiting:
                    self.waiting.remove(token)
                self.active.discard(token)
                self.condition.notify_all()
            changed('idle', 0)
