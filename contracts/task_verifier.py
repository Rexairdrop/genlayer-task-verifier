# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json

class TaskVerifier(gl.Contract):
    tasks: TreeMap[str, str]
    next_id: u256

    def __init__(self):
        self.tasks = TreeMap()
        self.next_id = u256(0)

    @gl.public.write
    def create_task(self, title: str, description: str, criteria: str) -> str:
        task_id = str(self.next_id)
        self.next_id = self.next_id + u256(1)

        task = {
            "title": title,
            "description": description,
            "criteria": criteria,
            "creator": str(gl.message.sender_address),
            "status": "open",
            "worker": "",
            "proof_url": "",
            "result": "",
            "reasoning": ""
        }

        self.tasks[task_id] = json.dumps(task)
        return task_id

    @gl.public.write
    def claim_task(self, task_id: str) -> bool:
        raw = self.tasks.get(task_id, "")
        if raw == "":
            return False

        task = json.loads(raw)
        if task["status"] != "open":
            return False

        task["status"] = "claimed"
        task["worker"] = str(gl.message.sender_address)
        self.tasks[task_id] = json.dumps(task)
        return True

    @gl.public.write
    def submit_proof(self, task_id: str, proof_url: str) -> bool:
        raw = self.tasks.get(task_id, "")
        if raw == "":
            return False

        task = json.loads(raw)
        if task["status"] != "claimed":
            return False
        if task["worker"] != str(gl.message.sender_address):
            return False

        task["status"] = "submitted"
        task["proof_url"] = proof_url
        self.tasks[task_id] = json.dumps(task)
        return True

    @gl.public.write
    def verify_task(self, task_id: str) -> str:
        raw = self.tasks.get(task_id, "")
        if raw == "":
            return "Task not found"

        task = json.loads(raw)
        if task["status"] != "submitted":
            return "Task is not submitted"

        proof_url = task["proof_url"]
        criteria = task["criteria"]
        title = task["title"]
        description = task["description"]

        def leader_fn():
            try:
                page = gl.nondet.web.render(proof_url, mode="text")
            except Exception as e:
                return {
                    "approved": False,
                    "reasoning": f"Could not fetch proof: {str(e)}"
                }

            prompt = f"""
You are a strict task verifier.

Task: {title}
Description: {description}
Criteria: {criteria}

Proof content:
{page[:3500]}

Decide if the proof meets the criteria.
Reply ONLY with this JSON:
{{"approved": true or false, "reasoning": "short explanation"}}
"""
            result = gl.nondet.exec_prompt(prompt, response_format="json")
            return result

        def validator_fn(leader_res) -> bool:
            if not isinstance(leader_res, gl.vm.Return):
                return False
            data = leader_res.calldata
            if not isinstance(data, dict):
                return False
            if "approved" not in data or not isinstance(data["approved"], bool):
                return False
            if "reasoning" not in data or not isinstance(data["reasoning"], str):
                return False
            return True

        decision_dict = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        is_approved = decision_dict.get("approved", False)
        task["status"] = "approved" if is_approved else "rejected"
        task["result"] = str(is_approved)
        task["reasoning"] = decision_dict.get("reasoning", "")

        self.tasks[task_id] = json.dumps(task, sort_keys=True)

        return json.dumps(decision_dict, sort_keys=True)

    @gl.public.view
    def get_task(self, task_id: str) -> str:
        return self.tasks.get(task_id, "{}")

    @gl.public.view
    def get_next_id(self) -> u256:
        return self.next_id
