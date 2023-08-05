
from parsl import *
import argparse

workers = IPyParallelExecutor()
dfk = DataFlowKernel(executors=[workers])


@App('python', dfk)
def get_num(first, second):
    return first + second


def test_fibonacci(num=5):
    x1 = 0
    x2 = 1
    counter = 0
    results = []
    results.append(0)
    results.append(1)
    while counter < num - 2:
        counter += 1
        results.append(get_num(x1, x2))
        temp = x2
        x2 = get_num(x1, x2)
        x1 = temp
    for i in range(len(results)):
        if isinstance(results[i], int):
            print(results[i])
        else:
            print(results[i].result())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--num", default="5",
                        action="store", dest="a", type=int)
    args = parser.parse_args()
    test_fibonacci(args.a)
