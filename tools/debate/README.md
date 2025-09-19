Debate framework
================

Small, testable debate manager used to run short debates between agents. This is a lightweight scaffold intended for the Multi-Agent Debate Framework POC.

Usage
-----

1. Implement an Agent with a `name` and `propose()` method.
2. Register agents with `DebateManager` and call `run_rounds()`.
