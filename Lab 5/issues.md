# Lab 5: Static Code Analysis

Shashank D | SRN: PES1UG24CS433

## Known issue table

Line numbers refer to `original/parking_system.py`. Bandit reported no High or Medium findings. Medium labels below are manual impact assessments, not Bandit ratings.

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Invalid expiry accepted as valid | Manual review; Medium (assessment) | 25-30, 59 | A malformed date is caught and returns False, allowing an expired permit. | Parse canonical ISO dates; reject invalid updates and treat unreadable expiry as expired. |
| Invalid registration data | Manual review; Medium (assessment) | 9-15, 56-58 | Unsupported zones and blank or None plates are accepted. | Validate non-empty string plates and membership in zones A, B and C before mutation. |
| Silent database reset | Pylint W0702; Medium impact (assessment) | 39-44 | Any load failure resets state, so corrupt data could later be overwritten. | Catch only FileNotFoundError; validate the complete loaded object before updating state; propagate other failures. |
| Predictable permit identifier | Bandit B311; Low | 11 | random.randint uses a non-cryptographic generator and only 90,000 values. | Use secrets.token_hex(16) and check issued identifiers for collisions. |
| Exception silently ignored | Bandit B110; Low | 20-23 | A bare except/pass hides failures during revocation. | Use dictionary pop with a default for an unknown plate. |
| Shared mutable default | Pylint W0102; Warning | 9, 14 | zone_records=[] is shared across calls. | Use None as the default and initialize a fresh list inside the function. |
| Bare exception handlers | Pylint W0702; Flake8 E722 | 16, 22, 29, 43 | Unrestricted catches hide errors and can catch termination signals. | Remove unnecessary handlers; catch specific expected exceptions at the appropriate boundary. |
| Unmanaged file handles | Pylint R1732 | 42, 47-49 | The read handle is never explicitly closed; write closure is not exception-safe. | Use with open(...) for both reading and writing. |
| Implicit text encoding | Pylint W1514 | 42, 47 | Persistence depends on the platform default encoding. | Specify UTF-8 explicitly. |
| Missing documentation and poor naming | Pylint C0114, C0116, C0103 | 1, 9-54 | The module/functions lack docstrings; setExpiry is not snake_case. | Add docstrings and rename the function and its caller to set_expiry. |
| Global rebinding | Pylint W0603 | 40 | Loading rebinds global permits, replacing the dictionary object. | Use a named PERMITS store, validate a temporary database, then clear/update the existing object. |
| Spacing and excessive line lengths | Flake8 E302, E305, E501; Pylint C0301 | 9-68 | Top-level spacing is missing and several lines exceed limits. | Add two blank lines between top-level functions and wrap lines to at most 79 characters. |
| Import executes the demonstration | Manual review; Low (assessment) | 68 | Importing the module prompts for input and writes a database. | Protect the entry point with if __name__ == "__main__". |
