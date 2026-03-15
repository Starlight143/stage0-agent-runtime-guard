# Service Overview

This repo is a demo repository, not the full product. The purpose of this page is to clarify what is and is not represented here.

## What this repo does represent

- hosted SignalPulse Stage0 integration by default
- runtime `/check` authorization patterns
- customer-facing demo scenarios
- buyer-facing explanations for `ALLOW`, `DENY`, and `DEFER`
- practical examples of loop controls, publication controls, and deployment controls

## What this repo does not represent

- a real-time uptime monitor
- live incident reporting
- the full Next.js marketing site
- the full dashboard, billing, and API key lifecycle product

## Where production-facing behavior should be verified

When a buyer asks for the source of truth, point them to:

- the hosted Stage0 API responses
- the runtime contract fields such as `request_id`, `decision`, and `policy_version`
- the richer docs and dashboard flows in the main SignalPulse application

## Recommended positioning in a sales call

Use this repo to show:

- how the agent behaves without an external runtime authority
- how the same agent behaves when every step is checked
- how runtime context changes the decision

Do not use this repo to imply:

- live service uptime guarantees
- customer logos or unverifiable production claims
- full operational monitoring coverage
