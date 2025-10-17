import re
from code_intepretor import DockerCodeRunner

header = \
"""from __future__ import annotations
from typing import Any, Optional, List, Dict, Set, Tuple"""

# extract the code
def prepare_results(ds_fixed):
    new_fixed = []
    for fixed in ds_fixed:
        search = re.search(r"```python(.*?)```", fixed, re.S)
        code = search.group(1)
        new_fixed.append(code)
    return new_fixed

# run single test
def run_code_with_test(code, test):
    code_with_test = header + "\n" + code + "\n" + test
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
            scores.append(0)
    return sum(scores) / len(tests), scores


