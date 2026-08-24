import json

from .core import run_acceptance_test

print(json.dumps(run_acceptance_test(), indent=2))
