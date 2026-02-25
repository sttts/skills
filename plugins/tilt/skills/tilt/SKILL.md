---
name: tilt
description: "Tilt local development and e2e testing. Triggers on tilt, kind cluster, e2e tests, test/tilt, local dev cluster."
version: 0.2.5
---

# Tilt Local Development

## Rules

- **NEVER run `tilt up` or `tilt down`** - Tilt is interactive, runs in the user's terminal
- Ask the user to start Tilt when needed
- Ask the user to verify Tilt shows all services ready before running tests

## Checking Tilt Status

```bash
# Check if Tilt is running
tilt get uiresources

# Check if all services are ready (non-zero exit = not ready)
tilt wait --timeout 5s --for=condition=Ready uiresource/<resource>
```

If Tilt is not running, ask the user:
> "Please start Tilt (`tilt up` or `tilt ci`) and wait for all services to be ready."

## Running test/tilt Tests

These are e2e tests that run against the Tilt-managed kind cluster.

```bash
# All tilt tests
cd test/tilt && go test -v ./...

# Specific test
cd test/tilt && go test -v -run TestSpecificFunction ./...

# With log file for easier reading
cd test/tilt && go test -v ./... 2>&1 | sed 's/\x1b\[[0-9;]*m//g' > test.log
```

## Running envtests (no Tilt needed)

Controller integration tests use envtest, independent of Tilt:

```bash
# Setup (one-time)
go install sigs.k8s.io/controller-runtime/tools/setup-envtest@latest

# Run envtests
KUBEBUILDER_ASSETS=$(setup-envtest use -p path 1.34.1) go test -v ./cmd/...

# Run specific controller tests
KUBEBUILDER_ASSETS=$(setup-envtest use -p path 1.34.1) go test -short -v ./cmd/<controller>/internal/reconcilers/...
```

## Prerequisites

If the user needs to set up Tilt from scratch:

**Install:**
```bash
brew install kind ko tilt tilt-dev/tap/ctlptl docker colima
```

**Start colima (Docker):**
```bash
colima start --cpu 4 --memory 6
export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock
```

**Symlink dependent repos into .cache/:**
```bash
mkdir -p .cache
ln -s <path-to-api-machinery-backend> .cache/backend
ln -s <path-to-dgxc-admission-controller> .cache/admission-controller
ln -s <path-to-platform-apis> .cache/apis
```

**Start cluster and Tilt:**
```bash
ctlptl apply -f ctlptl.yml
tilt up  # opens web UI on space bar
```

## Troubleshooting

- **Pod failures with taggedPointer errors**: Use colima, not Rancher Desktop
- **Tilt not finding repos**: Check .cache/ symlinks point to correct locations
- **Tests fail connecting to cluster**: Verify Tilt shows all services ready
- **Stale cluster**: `kind delete cluster && ctlptl apply -f ctlptl.yml`
