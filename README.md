# AI Task Verifier – GenLayer Intelligent Contract

## Purpose
A reusable Intelligent Contract that lets users create tasks with natural-language criteria. Workers submit a proof URL, and the contract uses GenLayer’s web access + LLM + non-deterministic consensus to decide if the task was completed correctly.

## Key Features
- Create tasks with custom criteria
- Claim and submit proof links
- AI-powered verification using `gl.vm.run_nondet_unsafe`
- Clear and deterministic state design using `TreeMap`

## How Consensus Works
The `verify_task` method uses:
1. `gl.nondet.web.render` to fetch the proof page
2. An LLM to judge the content against the criteria
3. A custom validator function that checks the structure of the LLM response

This allows realistic consensus on subjective decisions.

## Studio Deployment
Contract Address: `PASTE_YOUR_CONTRACT_ADDRESS_HERE`

## How to Use
1. `create_task(title, description, criteria)`
2. `claim_task(task_id)`
3. `submit_proof(task_id, proof_url)`
4. `verify_task(task_id)`
5. `get_task(task_id)` to check the result
