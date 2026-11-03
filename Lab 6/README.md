# Lab 6: Code and Branch Coverage Analysis

**Student:** Shashank D  
**SRN:** PES1UG24CS433  
**Module:** `bus_transit_fare.py`

---

## 1. Overview
This directory contains the completed deliverables for Lab 6 (Code and Branch Coverage Analysis).
Target application: Bus transit fare calculation and turnstile matrix failure detection (`bus_transit_fare.py`).

## 2. Deliverables Checklist
- [x] `bus_transit_fare.py`: The application under test.
- [x] `CodeCoverageTest_bus_transit_fare.py`: Test suite achieving **100% line coverage**.
- [x] `BranchCoverageTest_bus_transit_fare.py`: Targeted test suite achieving **100% branch coverage** (40/40 branches covered).
- [x] `test_bus_transit.py`: Comprehensive test file containing all line and branch test cases.
- [x] `code_coverage_report.png`: High-resolution terminal output screenshot of code coverage analysis.
- [x] `branch_coverage_report.png`: High-resolution terminal output screenshot of branch coverage analysis.
- [x] Two clean commits in git history as required by the rubric.

## 3. Results Summary

| Metric | Target Requirement | Achieved Result | Status |
| :--- | :---: | :---: | :---: |
| **Line / Code Coverage** | ≥ 90% | **100%** (57/57 statements) | PASSED |
| **Branch Coverage** | ≥ 90% | **100%** (40/40 branches) | PASSED |
| **Test Cases** | All passing | 16/16 Passed | PASSED |

## 4. How to Reproduce

### Run Code Coverage:
```bash
coverage run -m pytest CodeCoverageTest_bus_transit_fare.py
coverage report -m
```

### Run Branch Coverage:
```bash
coverage run --branch -m pytest BranchCoverageTest_bus_transit_fare.py
coverage report -m
```
