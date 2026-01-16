# section: diffing options
ASSUMES_MAXIMUM_OF_ONE_DELTA_PER_FILE = True
CONTEXT_LINES = 0
FINDS_SIMILAR = False
# end of section

# section: RE the Zero-shot classifier via NLI
# The model id of a predefined tokenizer hosted inside a model repo on huggingface.co.
MODEL_ID = "facebook/bart-large-mnli"
# Maximum allowed number of tokens for a single (premise, hypothesis) pair.
TOKEN_LIMIT = 256
TASK_MODE: TaskMode = TaskMode.TOPIC
TRIES_TO_CLASSIFY_FLATTENED_HUNK = False
RETURNS_ASAP = True
# end of section

# section: RE the subjects sample
RANDOM_STATE = 42

NUMBER_OF_REPOS_TO_INVESTIGATE: int | None = 385
EXCLUDES_RETIRED_REPOS = True

_README = "README"
_CONTRIBUTING = "CONTRIBUTING"
FILES_TO_INVESTIGATE = [
    _README + ".md",
    _README.lower() + ".md",
    _README + ".txt",
    _README.lower() + ".txt",
    _CONTRIBUTING + ".md",
    _CONTRIBUTING.lower() + ".md",
    _CONTRIBUTING + ".txt",
    _CONTRIBUTING.lower() + ".txt",
]

COMMITS_SINCE: datetime | None = None

# The time of cloning a repo should be after COMMITS_UNTIL
COMMITS_UNTIL: datetime | None = datetime(2025, 12, 31, 23, 59, 59)

ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO: int | None = None
# end of section