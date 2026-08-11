# Copilot Capstone Prompt Pack

Use these prompts in order with GitHub Copilot Chat Agent mode.

## Step 1: Requirements Prompt
"Read this user story: Automated Documentation Sync. Ask me clarifying questions one by one about scope, triggers, error behavior, security constraints, and acceptance criteria. Then draft requirements.md with FR/NFR/AC and open questions."

## Step 2: Architecture Prompt
"Using requirements.md, propose architecture with components, data flow, failure handling, and technology choices suitable for this Django/Python repo. Generate architecture.md with a component responsibility table and Mermaid data flow."

## Step 3: Design Review Prompt
"Review architecture.md like a senior engineer. Identify risks/gaps in correctness, security, error handling, testability, and CI reliability. Produce design-review.md with findings and design decisions, then suggest architecture.md updates."

## Step 4: Implementation Plan Prompt
"Break architecture.md into dependency-ordered tasks with blockers. Generate impl-plan.md including priorities, dependencies, and Definition of Done."

## Step 5: Implementation Prompt
"Implement the first P0 task from impl-plan.md. Make small commits per task, add/update tests for each change, and explain each commit message before applying it."

## Step 6: Self Review Prompt
"Perform a structured review against requirements.md covering correctness, security, error handling, test coverage, code clarity, DRY, and dependency safety. Return findings ordered by severity with file/line references and concrete fixes."

## Step 7: Verify Prompt
"Generate and run verification: unit + integration tests, then quality check of generated docs content. Provide pass/fail summary and raw command output."

## Step 8: PR Prompt
"Create a PR description with sections: Summary, Changes Made, Test Evidence, Known Limitations, Reviewer Checklist. Include changelog entry notes and links to artifacts."

## Optional: Human-in-the-loop Questions
- "Do you approve this design decision? If no, provide preferred alternative."
- "Should Not Found entries fail CI or only warn?"
- "What is the mapping ownership model for ongoing maintenance?"
