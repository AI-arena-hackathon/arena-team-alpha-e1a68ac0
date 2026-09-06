# PodSight: Unified Pod-Level Waste Analyzer

Team alpha — spec §3.2 hackathon build.

**One-liner:** PodSight: An opt‑in, agentless monitoring layer that surfaces pod‑level waste, quantifies its cost, and offers safe, audit‑controlled remediation playbooks – freeing CFOs and ops teams from weeks of manual scraping and hidden bill leaks.

**Problem:** Large enterprises with multi‑cluster, multi‑cloud deployments spend weeks manually correlating cluster metrics, cost APIs, and usage logs to surface pod‑level waste. Existing generic tools lack fine‑grained visibility, struggle with provider billing nuances, and their automatic remediation paths face resistance, governance gaps, and security concerns. This opacity leads to thousands of dollars in idle compute each month and costly manual investigations.

**Solution:** PodSight deploys an agentless sidecar that reads native cluster telemetry (Kubelet, Prometheus) and reconciles it with provider billing APIs through a pluggable adapter layer. It presents a unified, real‑time dashboard of over‑provisioned or idle pods, calculates exact cost impact using provider‑specific metering, and offers a staged remediation workflow: 1) observe‑only reporting; 2) manual‑approved playbooks (right‑size, scaling schedules, graceful termination); 3) optional automated declarative patches with full audit logs, role‑based approvals, and rollback hooks. The SaaS tier aggregates across accounts, delivers CFO‑ready reporting, and integrates with finance systems via secure APIs. Pilot clusters prove safety before scaling, mitigating ops risk and compliance friction.

**Build scope:** Phase 1 – Agentless telemetry collection and cost‑mapping adapters for AWS EKS, GKE, Azure AKS, and on‑prem OpenShift; Phase 2 – Unified dashboard and cost‑impact calculator; Phase 3 – Playbook engine with audit logs, RBAC, and rollback; Phase 4 – SaaS cross‑account aggregation, finance‑system integrations, and certification with major cloud vendors.

Built entirely by an AI coding agent across discrete GitHub Actions build turns (spec §8) — no human-written code.
