<!--
Sync Impact Report
==================
Version Change: [NONE] → 1.0.0
Type: MINOR (Initial constitution creation)
Date: 2025-11-13

Changes:
- Initial constitution ratified
- 8 core principles established
- Design philosophy and code quality standards defined
- Testing and maintainability requirements codified

Templates Status:
✅ .specify/templates/plan-template.md - No updates needed (constitution check already present)
✅ .specify/templates/spec-template.md - No updates needed (requirements structure compatible)
✅ .specify/templates/tasks-template.md - No updates needed (test-driven workflow compatible)
✅ .specify/templates/agent-file-template.md - Review recommended
✅ .specify/templates/checklist-template.md - Review recommended

Follow-up TODOs:
- None
-->

# Familiar Constitution

**Familiar** is an autonomous AI-driven end-to-end testing command line tool built on the foundation of clean object-oriented design and humane code principles.

## Core Principles

### I. Easy to Change

Code MUST be designed for change. We prioritize reducing dependencies between classes through:

- **Dependency injection**: Classes receive dependencies explicitly rather than creating them internally
- **Single responsibility**: Each class has one reason to change
- **Stable public APIs**: Public interfaces remain consistent while internals evolve
- **Loose coupling**: Classes interact through interfaces, not concrete implementations

**Rationale**: Testing tools must adapt quickly to changing requirements and technologies. Code that resists change becomes a liability, not an asset.

### II. Small, Single Purpose Classes

Classes and methods MUST be small and focused:

- Classes have one clear purpose that can be explained in a single sentence
- Methods do one thing and do it well
- Composition over inheritance: Build complex behavior by combining simple objects
- Message-oriented design: Objects send messages to collaborators rather than directly manipulating their state

**Rationale**: Small, focused units are easier to understand, test, modify, and reuse. They make the codebase navigable and reduce cognitive load.

### III. Stable, Minimal Public Interfaces

Public APIs MUST be:

- **Minimal**: Expose only what clients need
- **Stable**: Changes to public interfaces require explicit versioning
- **Clear**: Interface contracts are documented and predictable
- **Explicit dependencies**: All dependencies are visible in constructors or method signatures

**Rationale**: Public interfaces are contracts with users and other parts of the system. Stability reduces breaking changes; minimalism reduces surface area for bugs.

### IV. Polymorphism Over Conditionals

Use polymorphism instead of conditionals whenever behavior varies by type:

- Strategy pattern over case statements
- Command pattern over action switches
- Null objects over nil checks where appropriate

**Rationale**: Conditionals scatter related behavior across the codebase. Polymorphism centralizes behavior with the objects that own it, making code easier to extend and test.

### V. Behavior-Based Testing

Tests MUST validate behavior, not implementation:

- Test what the system does, not how it does it
- Tests remain valid when refactoring internals
- Focus on public interfaces and contracts
- Test outcomes and side effects, not private methods

**Rationale**: Implementation-focused tests are brittle and expensive to maintain. Behavior-based tests provide confidence that the system works while giving freedom to refactor.

### VI. Code as User Interface

Code is designed for humans to read and understand:

- Readability over cleverness
- Clarity over performance optimization (until performance becomes a problem)
- Native methods over regex when both suffice
- Clear implementations that 80% of developers understand over clever solutions

**Rationale**: Code is read far more often than it is written. The next developer (often you) needs to understand it quickly and correctly.

### VII. Humane Code

Code MUST be humane—keeping it clear, reducing unnecessary abstraction, and making it explicit:

- Use descriptive names that reveal intent
- Prefer explicit over implicit behavior
- Reduce abstraction layers unless they provide clear value
- Choose familiarity over novelty

**Rationale**: Humane code respects the reader's time and cognitive capacity. It reduces friction in understanding and modification.

### VIII. Test-Driven Development (when applicable)

For core functionality, prefer test-first development:

- Write tests that describe desired behavior
- Run tests to confirm they fail
- Implement the simplest solution that makes tests pass
- Refactor while keeping tests green

**Rationale**: As a testing tool, Familiar must be reliably testable. TDD ensures testability and provides living documentation of expected behavior.

## Code Quality Standards

Code contributions MUST meet these standards:

- **No long methods**: Methods exceeding 20 lines should be scrutinized for refactoring opportunities
- **No god classes**: Classes with more than 5-7 public methods likely have multiple responsibilities
- **No deep nesting**: More than 3 levels of nesting indicates complexity that should be extracted
- **Explicit over clever**: Simple, readable solutions trump clever optimizations
- **Dependency direction**: Dependencies flow toward stable abstractions, not volatile implementations

## Testing Requirements

Testing MUST ensure behavior correctness while remaining maintainable:

- **Unit tests**: Validate individual class behavior through public interfaces
- **Integration tests**: Verify collaborating objects work correctly together
- **Contract tests**: Ensure public APIs honor their contracts
- **Avoid mocking internals**: Mock external dependencies, not your own classes
- **Test behavior**: Focus on outcomes, not implementation details

## Maintainability Practices

Code MUST remain maintainable over time:

- **Clear naming**: Names reveal intent without needing comments
- **Minimal comments**: Code should be self-documenting; comments explain why, not what
- **Extract complexity**: Complex logic is extracted into well-named methods or classes
- **Consistent style**: Follow language idioms and project conventions
- **Progressive enhancement**: Start simple, add complexity only when needed

## Governance

This constitution represents the non-negotiable principles guiding Familiar development. All code contributions, design decisions, and architectural choices MUST align with these principles.

### Amendment Process

1. Proposed amendments must be documented with rationale and impact analysis
2. Version number is updated according to semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes or removals
   - **MINOR**: New principles added or material expansions
   - **PATCH**: Clarifications, wording improvements, non-semantic changes
3. Amendments require sync with dependent templates (plan, spec, tasks)
4. Impact report documents all changes and affected artifacts

### Compliance Review

- All pull requests MUST verify compliance with these principles
- Complexity must be justified when it violates simplicity principles
- Code review checklist validates constitutional adherence
- Refactoring efforts prioritize constitutional alignment

### Living Document

This constitution evolves with the project. When principles conflict with practical needs, we update the constitution thoughtfully rather than compromising quality.

**Version**: 1.0.0 | **Ratified**: 2025-11-13 | **Last Amended**: 2025-11-13
