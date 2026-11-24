"""Agent-side graph execution, loaded only for the treatment group."""
import json


class SkillFlow:
    def __init__(self, flow):
        self.nodes = {node["id"]: node for node in flow["nodes"]}
        self.next_node = {edge["from"]: edge["to"] for edge in flow["edges"]
                          if edge["on"] == "complete"}
        self.active = flow["entry"]
        self.retry_limit = flow["retry"]["limitPerNode"]
        self.retries = 0
        self.failed = False
        self.log("enter")

    def log(self, event):
        print(json.dumps({"type": "flow", "event": event, "node": self.active,
                          "retries": self.retries}), flush=True)

    def guidance(self):
        node = self.nodes[self.active]
        instruction = (
            f'Active stage: {self.active}. Original source: {node["skill"]}/SKILL.md.\n'
            'Use the task instruction and the active Skill excerpt. Preserve intermediate files '
            'for later stages. Call advance_skill when this stage is complete or inapplicable.'
        )
        if self.failed:
            instruction += "\nA shell command failed. Review its output and repair or recover before advancing."
        if self.retries >= self.retry_limit and self.failed:
            instruction += "\nThe recovery limit was reached. Advance only if recovery is unnecessary for this stage."
        if node.get("guidance"):
            instruction += "\n" + node["guidance"]
        return instruction + "\n\n" + node["text"]

    def advance(self):
        if self.failed:
            return {"advanced": False, "error": "Resolve the current failure or explain why the stage can be skipped."}
        self.log("complete")
        self.active = self.next_node.get(self.active)
        self.retries = 0
        if self.active:
            self.log("enter")
        return {"advanced": True, "next": self.active}

    def accept_shell_result(self, result):
        failed = result.get("exit_code") != 0
        if failed and not self.failed and self.retries < self.retry_limit:
            self.retries += 1
            self.log("retry")
        self.failed = failed


ADVANCE_TOOL = {
    "type": "function",
    "function": {
        "name": "advance_skill",
        "description": "Complete the active Skill stage or skip a stage that does not apply to the task.",
        "parameters": {"type": "object", "properties": {
            "skip_reason": {"type": "string", "description": "Reason if this stage does not apply"}
        }, "additionalProperties": False},
    },
}
