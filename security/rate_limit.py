"""
Token-bucket rate limiter for GUARDIAN-AGENT.
Prevents rapid-fire API calls that lead to 429 errors.
"""
import time
import threading

class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def acquire(self, amount: int = 1):
        with self.lock:
            self._refill()
            if self.tokens >= amount:
                self.tokens -= amount
                return True
            return False

    def wait_and_acquire(self, amount: int = 1):
        while not self.acquire(amount):
            time.sleep(1 / self.rate)

# Global rate limiters (example values)
groq_limiter = TokenBucket(rate=0.5, capacity=2) # 1 request every 2 sec
tavily_limiter = TokenBucket(rate=0.2, capacity=1) # 1 search every 5 sec
