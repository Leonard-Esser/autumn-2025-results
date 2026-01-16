from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Subject:
    full_name_of_repo: str
    commit_sha: str
    path: str


@dataclass(frozen=True, slots=True)
class Result:
    subject: Subject
    detected_channels: frozenset[str] = field(default_factory=frozenset)
    is_ccdc_event: bool = False
