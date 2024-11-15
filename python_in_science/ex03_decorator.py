import json
import random
import statistics
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable

import tqdm


@dataclass
class Stats:
    func_name: str
    count: float
    sum: float
    mean: float
    std: float
    min: float
    max: float


class TimeIt:
    times: list[float] = []
    stats = Stats(
        func_name="",
        count=0,
        sum=0,
        mean=0,
        std=0,
        min=0,
        max=0,
    )

    def __call__(self, func: Callable) -> Callable:
        self.stats.func_name = func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()

            duration = end - start
            self.times.append(duration)
            self.stats.count += 1

            return result

        wrapper.print_stats = self.print_stats  # type: ignore
        return wrapper

    def calc_stats(self):
        self.stats.sum = sum(self.times)
        self.stats.mean = statistics.mean(self.times)
        self.stats.std = statistics.stdev(self.times)
        self.stats.max = max(self.times)
        self.stats.min = min(self.times)

    def print_stats(self):
        self.calc_stats()
        print(json.dumps(self.stats.__dict__, indent=2))


@TimeIt()
def do_something(n: int) -> int:
    x = 0
    for i in range(n):
        x += 1
        x *= random.randint(i, n)
    return x


if __name__ == "__main__":
    for _ in tqdm.tqdm(range(10), ascii=True):
        do_something(40000)

    do_something.print_stats()  # type: ignore
