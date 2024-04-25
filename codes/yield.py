# iterator
# __iter__, __next__

import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.DEBUG,
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

LOGGER = logging.getLogger(__name__)


class Counter:
    def __iter__(self):
        iter = Iterator()
        return iter


class Iterator:
    def __init__(self):
        self.index = 0

    def __next__(self):
        if self.index > 10:
            raise StopIteration

        n = self.index * 2
        self.index += 1
        return n


# generator makes things easier to make iterator.
# python supports coroutine as other languages with `yield`.
# and the function with yield is called `lightweight (simple) coroutine`.
# That means, yield based coroutine equals as generator.
# cf. async supports coroutine, which is called native coroutine.

# Later, send() is added to the coroutine.
# From this point, the concurrent runnable coroutine is enabled.
# Data can be transacted to and from caller and callee, which enables the concurrent asynchronous running.


def even_generator():
    for i in range(10):
        yield i * 2


def even_coroutine():
    print("callee 1")
    x = yield 1 * 2
    print("callee 2: %d" % x)
    x = yield x * 2
    print("callee 3: %d" % x)


####### yield from #######


# case when coroutine calls the sub-coroutine
# compared to the previous examples, here means:
# a <-> b <-> c, and not a <-> b (1:1 connection)
def subcoroutine():
    print("Subcoroutine")
    x = yield 1
    print("receive: " + str(x))
    x = yield 2
    print("receive: " + str(x))


def coroutine():
    sub_tasks = subcoroutine()
    sub_result = next(sub_tasks)  # At first, we have to run next one time.

    # run subcoroutine iteratively, while exchanging the data. (no close(), throw(); only send())
    # throw(type, value, traceback) -> it can transfer the exception to the coroutine from subcoroutine.
    while True:
        result = yield sub_result

        if result is None:
            sub_result = next(sub_tasks)
        else:
            sub_result = sub_tasks.send(result)


def yieldfrom_coroutine():
    # yield from = generator + send + throw + close
    yield from subcoroutine()  # yield from receives Iterator or Generator


# add return to generator
def sum(max):
    tot = 0
    for i in range(max):
        tot += i
        yield tot
    return tot  # finally let the subcoroutine to return the final result.


def sum_coroutine():
    x = yield from sum(5)
    print("Total: {}".format(x))


if __name__ == "__main__":
    c = Counter()
    i = iter(c)

    LOGGER.info(
        f"Iterator: {next(i)} -> {next(i)} -> ...",
    )

    even_gen = even_generator()
    LOGGER.info(f"Type of even_generator: {type(even_gen)}")
    LOGGER.info(f"Generator: {next(even_gen)} -> {next(even_gen)} -> ...")

    task = even_coroutine()
    LOGGER.info(f"Type of even_coroutine: {type(task)}")
    i = next(task)
    LOGGER.info(f"First i: {i}")
    i = task.send(10)
    LOGGER.info(f"Second i: {i}")
    try:
        task.send(i)
    except StopIteration:
        LOGGER.error("StopIteration raised")

    # ---- yield from ---- #
    main = coroutine()
    LOGGER.info(f"First call: {next(main)}")
    LOGGER.info(f"Second call: {main.send(10)}")  # send(None) == next()
    # main.send(20) -> StopIteration

    # ---- yield from ---- #
    main = yieldfrom_coroutine()
    LOGGER.info(f"First call: {next(main)}")
    LOGGER.info(f"Second call: {main.send(10)}")  # send(None) == next()
    # main.send(20) -> StopIteration

    main = sum_coroutine()
    LOGGER.info(f"First call: {next(main)}")
    LOGGER.info(f"Second call: {main.send(10)}")  # subcoroutine receives it, but sum() does not do anything.
    for _ in main:
        print(_)
