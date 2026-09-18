# Genome-web TF Reference Integration

This directory is a reference translation layer between BioHarness public contracts and the externally checked-out Genome-web TF workflow.

## Dependency boundary

- Genome-web owns all biological data, schema, validation, launcher, and workflow logic.
- This directory contains only reference configuration and adapter code.
- The reference layer may depend on BioHarness public contracts.
- BioHarness Core never depends on this directory.
- Deleting this directory must not break the `bioharness` package or Core tests.
- Audited capability claims apply only to Genome-web revision `05072cbbcd533ca59afa13996d8d0edd8f939c6e`.
- The configured revision is not trusted by itself: operations that execute audited Genome-web code must also observe and verify the checkout revision.
