# Lab 5: Static Code Analysis

Shashank D | SRN: PES1UG24CS433

## Reflection answers

The repository requests four reflection answers, but the supplied three-page handout does not contain the questions. The four prompts below are relevant substitute prompts; they are not quoted from the handout. This is a prepared draft for the student to review and personalize.

### 1. What did the three tools contribute?

Pylint identified code quality problems such as the shared mutable default, bare exceptions, missing documentation and unsafe file handling. Flake8 identified spacing, line length and bare-except violations. Bandit identified the non-cryptographic random generator and the except/pass pattern. Their coverage overlaps, but each tool adds a different perspective.

### 2. Which issues were prioritized and why?

The original Bandit scan reported two Low-severity findings and no Medium or High findings. Both were fixed. Manual review also identified medium-impact behavior: malformed expiry dates were treated as valid, invalid registrations were accepted and load errors silently reset the database. These impact assessments are separate from tool severity. Correctness and data preservation were prioritized before documentation and formatting.

### 3. How were the fixes verified?

All three tools were run before and after the changes without disabling checks. Pylint improved from 6.32/10 to 10.00/10; Bandit fell from two findings to zero; Flake8 fell from 16 violations to zero. Eighteen regression tests passed, covering registration validation, revocation, date boundaries, zone scanning, JSON persistence, corrupt data and import behavior. A fresh demonstration run flags the expired vehicle that the original missed.

### 4. What are the benefits and limitations of static analysis?

Static analysis gives repeatable feedback early and makes code easier to review and maintain. It does not prove that business behavior is correct: the original date-format mismatch and unsupported zones needed manual inspection and behavioral tests. A clean scan should therefore be combined with tests and code review. A next improvement would be atomic file replacement and protection against simultaneous writers for production use.
