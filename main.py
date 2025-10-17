from datasets import load_dataset
from code_agent import CodeDebugAgent
from evaluation import evaluate
import time

def main():
    # t1 = time.time()
    ds_range = range(2)
    ds = load_dataset("bigcode/humanevalpack", "python")["test"].select(ds_range)
    prompts_ds = ds.select_columns(
        ['task_id', 'instruction', 'buggy_solution', 'bug_type', 'failure_symptoms', 'example_test']).select(ds_range)
    test_ds = ds.select_columns(['test'])

    agent = CodeDebugAgent()

    fixed_codes = []
    for i in range(len(prompts_ds)):
        print(f"{i + 1}-----" * 13 + f"{i + 1}")
        print(f"Start processing query...")
        result = agent.fix_code(prompts_ds[i])
        fixed_codes.append(result["last_code"])
        print(f"Result: {result['last_code']}")

    pass_1, score_list = evaluate(fixed_codes, test_ds)
    print(score_list)
    print(f"|-----" * 13 + f"|")
    print("All queries processed")
    print(f"Pass@1: {pass_1}")

    # t2 = time.time()
    # print(f"Time: {t2 - t1}")
if __name__ == "__main__":
    main()