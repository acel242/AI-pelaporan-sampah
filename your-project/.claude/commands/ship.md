# Ship command

`ship.md` is a meta‑command that builds, lints and deploys the project in one step.

```bash
# Run lint, tests, build, then push to production
./scripts/lint.sh && ./scripts/test.sh && ./scripts/build.sh && ./scripts/deploy.sh
```

Adjust the pipeline to match your CI/CD setup.
