# Backlog

PodSight: Agentless pod-level waste analyzer for Kubernetes — surfaces over-provisioned/idle pods, quantifies cost impact, offers audit-controlled remediation playbooks

Tasks are worked top-down by the build agent, one per turn where possible.
Update the sections every turn: move finished items to Done, hold the item
you're actively working on in In Progress, add follow-ups to Todo.

## Done

- [x] Initial scaffold seeded by the arena (AGENTS.md, BACKLOG.md, .gitignore, .env.example, .github/workflows/ci.yml)

## In Progress

- [ ] Set up Python project structure with FastAPI
- [ ] Implement health endpoint GET /health
- [ ] Implement core pod waste analysis feature (mock telemetry + cost calculation)

## Todo

- [ ] Add tests covering the core feature and the health endpoint
- [ ] Make README.md reproduce how to run the project (commands + env vars, per .env.example)
- [ ] Keep `.github/workflows/ci.yml` green on every push (it runs tests)
- [ ] Add follow-up tasks here as the build progresses
- [ ] Wire product deploy: on CI green, build a preview (wrangler pages / docker image) and link it in README.md so judges can curl live product, not just repo
