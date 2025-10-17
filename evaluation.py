import re
from code_intepretor import DockerCodeRunner
from typing import TypedDict, List, Any

def prepare_results(results):
    new_results = []
    for result in results:
        search = re.search(r"```python(.*?)```", result, re.S)
        code = search.group(1)
        new_results.append(code)
    return new_results


def run_code_with_test(code, test):
    code_with_test = code + "\n" + test
    code_runner = DockerCodeRunner()
    result = code_runner.run({
        "language": "python",
        "code": code_with_test,
        "timeout_sec": 15,
        "memory_mb": 512,
        "cpu_limit": 1,
    })
    return result


def evaluate(code, tests):
    scores = []
    code = prepare_results(code)
    assert len(code) == len(tests)
    for i in range(len(tests)):
        result = run_code_with_test(code[i], tests[i]["test"])
        if result["exit_code"] == 0:
            scores.append(1)
        else:
            print(result)
            scores.append(0)
    return sum(scores) / len(tests), scores


