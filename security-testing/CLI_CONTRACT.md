# CLI Contract — Power BI Automated Security Testing

## 1. Overview

This document defines the command-line interface (CLI) contract for the Automated Security Testing module.

It specifies how the DevSecOps pipeline can execute security tests, select the adapter, interpret execution results, and retrieve generated reports.

## 2. Requirements

- Python 3.12+
- Project virtual environment activated
- Dependencies installed from `requirements.txt`

## 3. Execution

Run commands from the `security-testing` directory.

### Default execution (Mock adapter)

```powershell
python -m src.main
```

### Explicit Mock adapter

```powershell
$env:SECURITY_ADAPTER = "mock"
python -m src.main
```

### Power BI adapter

```powershell
$env:SECURITY_ADAPTER = "powerbi"
python -m src.main
```

**Important:** The Power BI adapter is prepared but requires a real Power BI query executor. Real Power BI RLS validation is not yet available.

## 4. Adapter configuration

| Environment variable | Accepted values | Default |
|---|---|---|
| `SECURITY_ADAPTER` | `mock`, `powerbi` | `mock` |

The Mock adapter uses simulated visible-region data.

The Power BI adapter is intended to execute queries against the actual semantic model under the tested user's identity.

## 5. Exit codes

| Exit code | Meaning |
|---|---|
| `0` | All security tests passed |
| `1` | At least one test failed or returned an error |
| `2` | Configuration, missing file, or execution setup error |

The pipeline must treat any non-zero exit code as a failed job.

## 6. Security test scenarios

| Test ID | Scenario | Purpose |
|---|---|---|
| TC001 | ALLOW | Verify authorized access |
| TC002 | DENY | Detect unauthorized regional access |
| TC003 | UNKNOWN_USER | Verify unknown users have no access |
| TC004 | INACTIVE_USER | Verify inactive users have no access |
| TC005 | MULTI_REGION | Verify access to all authorized regions |

## 7. Generated reports

Reports are generated automatically in:

```text
security-testing/reports/
```

### JSON report

`security_report.json`

Contains:

- `total_tests`
- `passed`
- `failed`
- `errors`
- `unauthorized_access_tests`
- `over_restriction_tests`
- `results`

### CSV report

`security_report.csv`

Contains:

- `test_id`
- `user`
- `scenario`
- `target_region`
- `description`
- `expected_regions`
- `actual_regions`
- `missing_regions`
- `unauthorized_regions`
- `status`
- `error`

## 8. Result interpretation

| Status | Meaning |
|---|---|
| PASS | Actual access matches expected authorization |
| FAIL | Unauthorized access or over-restriction detected |
| ERROR | Technical or execution error prevented the test from completing |

## 9. DevSecOps integration

The DevSecOps pipeline should:

1. Install Python dependencies.
2. Configure the required environment variables.
3. Execute the CLI command.
4. Check the process exit code.
5. Collect the JSON and CSV reports.
6. Publish reports as pipeline artifacts.

Example:

```powershell
$env:SECURITY_ADAPTER = "mock"
python -m src.main

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
```

## 10. Current limitations

- Mock mode validates the testing engine using simulated data.
- The Power BI adapter does not yet have a configured query executor.
- Actual RLS validation depends on access to the Power BI semantic model and a valid user-identity execution mechanism.
- The authorization matrix must be validated against the real project configuration before integration.

---

**Module:** Automated Security Testing  
**Responsible member:** Membre 2  
**Project:** Power BI Security Testing