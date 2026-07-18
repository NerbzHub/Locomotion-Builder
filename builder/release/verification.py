"""Sprint B03-S078 — Final Verification."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job
from builder.review.engineering import ReviewFinding

from .preparation import RELEASE_VERSION, ReleasePreparation


@dataclass(frozen=True, slots=True)
class FinalVerification:
    """The final Version 1 readiness result before candidate production."""

    preparation: ReleasePreparation
    findings: tuple[ReviewFinding, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.preparation, ReleasePreparation):
            raise TypeError("Final verification requires ReleasePreparation")
        if any(not isinstance(finding, ReviewFinding) for finding in self.findings):
            raise TypeError("Final verification findings must be ReviewFinding values")

    @property
    def is_ready(self) -> bool:
        return not self.findings

    @property
    def status(self) -> str:
        if self.is_ready:
            return f"Version {RELEASE_VERSION} final verification passed"
        return (
            f"Version {RELEASE_VERSION} final verification found "
            f"{len(self.findings)} issue(s)"
        )


class VerifyVersionOneReadinessJob(Job):
    """Verify explicit release preparation before candidate production."""

    def __init__(self, preparation: ReleasePreparation):
        super().__init__("Verify Version 1 Readiness")
        self.preparation = preparation
        self.verification: FinalVerification | None = None

    def run(self) -> None:
        self.verification = _verify_version_one_readiness(self.preparation)


def verify_version_one_readiness(
    preparation: ReleasePreparation,
) -> FinalVerification:
    """Verify Version 1 readiness through the Job framework."""
    job = VerifyVersionOneReadinessJob(preparation)
    job.execute()
    if job.verification is None:
        raise RuntimeError("Final verification completed without a result")
    return job.verification


def _verify_version_one_readiness(
    preparation: ReleasePreparation,
) -> FinalVerification:
    if not isinstance(preparation, ReleasePreparation):
        raise TypeError("Final verification requires ReleasePreparation")

    findings = preparation.findings
    return FinalVerification(preparation=preparation, findings=findings)
