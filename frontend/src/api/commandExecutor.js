import {
  createWorkflow,
  runWorkflow,
} from "./automation";

import {
  parseCreatorCommand,
} from "./commandParser";

export async function executeCreatorCommand(
  rawCommand
) {
  const parsed =
    parseCreatorCommand(rawCommand);

  if (!parsed.valid) {
    throw new Error(
      "Tell me what you want to create."
    );
  }

  const created =
    await createWorkflow({
      command: parsed.command,
      platform: parsed.platform,
      topic: parsed.topic,
    });

  const workflow =
    created?.workflow || created;

  if (!workflow?.id) {
    throw new Error(
      "N1MOX created the workflow but did not receive a workflow ID."
    );
  }

  const executed =
    await runWorkflow(workflow.id);

  return {
    parsed,
    workflow:
      executed?.workflow ||
      executed ||
      workflow,
  };
}
