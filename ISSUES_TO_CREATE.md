# GitHub Issues to Create from PENDING_TASKS.md

This document lists the issues that should be created to track tasks from PENDING_TASKS.md.
These were automatically extracted from Priority 8: API Enhancement for Orchestration Framework Integration.

## Instructions

To create these issues, you can:

1. **Using the Python script** (requires GitHub CLI authentication):
   ```bash
   # Preview what would be created
   python create_issues_from_tasks.py --dry-run
   
   # Create only Priority 8 issues
   python create_issues_from_tasks.py --priority 8
   
   # Create all issues
   python create_issues_from_tasks.py
   ```

2. **Manually create them** using the details below

---

## Issue 1: [FEAT]: Async Support Implementation

**Priority**: High  
**Labels**: `priority:high`, `scope:api-design`, `milestone:v0.2`

**Description:**
Add async variants of public methods to support async orchestrators (LangChain, CrewAI, FastAPI).
This is critical for modern orchestration frameworks.

**Tasks:**
- [ ] Add `async def solve_async()` method to `PlanGen` class
- [ ] Add `async def solve_async()` to `Algorithm` factory
- [ ] Update `ModelProtocol` to support async generation
- [ ] Add concurrent execution support for solution generation
- [ ] Add tests for async functionality

**Files to Modify:**
- `plangen/api.py` - Add async methods
- `plangen/models/base_model.py` - Add async protocol
- `plangen/algorithms/base_algorithm.py` - Add async support
- `tests/test_api_async.py` - New test file

**Estimated Effort:** 3-5 days

---

## Issue 2: [FEAT]: Callback/Observer System

**Priority**: High  
**Labels**: `priority:high`, `scope:api-design`, `milestone:v0.2`

**Description:**
Add callback hooks to track workflow execution and inject custom logic. This enables monitoring and custom logic injection during the planning process.

**Tasks:**
- [ ] Implement callback registry in `PlanGen` class
- [ ] Add `on_constraint_extracted()` callback
- [ ] Add `on_solution_generated()` callback
- [ ] Add `on_verification_complete()` callback
- [ ] Add `on_solution_selected()` callback
- [ ] Add tests for callback system
- [ ] Update documentation with callback examples

**Files to Modify:**
- `plangen/api.py` - Add callback registry
- `plangen/plangen.py` - Trigger callbacks in workflow
- `tests/test_callbacks.py` - New test file
- `docs/user_guide/callbacks.md` - New documentation

**Estimated Effort:** 2-3 days

---

## Issue 3: [FEAT]: Type Safety Improvements

**Priority**: High  
**Labels**: `priority:high`, `scope:api-design`, `milestone:v0.2`

**Description:**
Replace generic `Dict[str, Any]` with proper TypedDict structures for better IDE support and type safety.

**Tasks:**
- [ ] Create `TypedDict` for `SolveResult`
- [ ] Create `TypedDict` for verification results
- [ ] Update all methods to return typed structures
- [ ] Add type stubs (.pyi files) if needed
- [ ] Update tests to use new types

**Files to Modify:**
- `plangen/api.py` - Add TypedDict definitions
- `plangen/models/base_model.py` - Update return types
- `plangen/algorithms/base_algorithm.py` - Update return types
- All integration tests

**Estimated Effort:** 2-3 days

---

## Issue 4: [FEAT]: Configuration Object Pattern

**Priority**: Medium  
**Labels**: `priority:medium`, `scope:api-design`, `milestone:v0.2`

**Description:**
Add `PlanGenConfig` dataclass for cleaner configuration management and dependency injection support.

**Tasks:**
- [ ] Create `PlanGenConfig` dataclass
- [ ] Add `from_config()` class method to `PlanGen`
- [ ] Add validation for config parameters
- [ ] Support environment variable overrides
- [ ] Add tests for configuration loading
- [ ] Document configuration patterns

**Files to Modify:**
- `plangen/api.py` - Add config class and loader
- `tests/test_config.py` - New test file
- `docs/user_guide/configuration.md` - Update documentation

**Estimated Effort:** 2-3 days

---

## Issue 5: [FEAT]: Workflow Customization/Exposure

**Priority**: Medium  
**Labels**: `priority:medium`, `scope:api-design`, `scope:architecture`, `milestone:v0.2`

**Description:**
Expose LangGraph workflow for inspection and customization by advanced users.

**Tasks:**
- [ ] Add `get_workflow_graph()` method
- [ ] Add `get_agents()` method to expose agent instances
- [ ] Document workflow structure
- [ ] Provide examples of workflow customization
- [ ] Add tests for workflow access

**Files to Modify:**
- `plangen/api.py` - Add accessor methods
- `tests/test_workflow_access.py` - New test file
- `docs/advanced_usage.md` - New documentation
- `examples/custom_workflow_example.py` - New example

**Estimated Effort:** 2-3 days

---

## Issue 6: [FEAT]: Streaming Support

**Priority**: Medium  
**Labels**: `priority:medium`, `scope:api-design`, `milestone:v0.2`

**Description:**
Add streaming API for real-time result generation and UI updates. Important for applications that need real-time feedback.

**Tasks:**
- [ ] Implement `solve_stream()` method
- [ ] Add solution generator streaming
- [ ] Add constraint extraction streaming
- [ ] Add verification result streaming
- [ ] Create tests for streaming
- [ ] Document streaming patterns
- [ ] Add streaming examples

**Files to Modify:**
- `plangen/api.py` - Add streaming methods
- `plangen/plangen.py` - Add stream support to workflow
- `tests/test_streaming.py` - New test file
- `examples/streaming_example.py` - New example
- `docs/streaming.md` - New documentation

**Estimated Effort:** 4-5 days

---

## Issue 7: [FEAT]: Verifier Composition

**Priority**: Low-Medium  
**Labels**: `priority:medium`, `scope:api-design`, `scope:verification`, `milestone:v0.2`

**Description:**
Support combining multiple verifiers with different strategies (average, weighted, first_fail) for advanced verification scenarios.

**Tasks:**
- [ ] Add `combine()` method to `Verifiers` class
- [ ] Implement `average` combining strategy
- [ ] Implement `weighted` combining strategy
- [ ] Implement `first_fail` combining strategy
- [ ] Create tests for verifier composition
- [ ] Document composition patterns
- [ ] Add composition examples

**Files to Modify:**
- `plangen/api.py` - Add combine method
- `plangen/verification/base_verifier.py` - Add composition support
- `tests/test_verifier_composition.py` - New test file
- `examples/verifier_composition_example.py` - New example
- `docs/user_guide/verification.md` - Update with composition

**Estimated Effort:** 2-3 days

---

## Summary

**Total Issues:** 7  
**Total Estimated Effort:** 18-25 days (approximately 4-5 weeks)

**Priority Breakdown:**
- High Priority: 3 issues (Async, Callbacks, Type Safety)
- Medium Priority: 4 issues (Config, Workflow, Streaming, Verifier Composition)

**Dependencies:**
- Issues 1-3 should be tackled first as they provide foundational improvements
- Issues 4-7 can be worked on in parallel or after the foundation is complete

**Note:** These issues are from the Priority 8 section of PENDING_TASKS.md which focuses on
API enhancements for orchestration framework integration. These features will make PlanGEN
more suitable for integration with modern async frameworks and provide better developer experience.
