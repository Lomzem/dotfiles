# Stretch goal: inline preview

Attempt this only after the verified HTML file is ready. The file is the deliverable; preview failures do not block delivery or require changes to the report.

Transfer `<report directory>/<report directory name>.html` through code orchestration, keeping compiled HTML in tool variables. In Codex `functions.exec`, read it as JSON through `exec_command`, parse the output into a variable, and pass that variable directly to the HTML tools. For example (substitute the absolute path):

```js
const file = await tools.exec_command({
  cmd: `python3 -c 'import json,pathlib; print(json.dumps(pathlib.Path("/absolute/report.html").read_text()))'`,
  max_output_tokens: 100000,
});
if (file.exit_code !== 0) throw new Error("Cannot read report");
const html = JSON.parse(file.output); // Truncated output fails here.
const preview = await tools.mcp__t3_code__html_preview({ html, width: 728 });
// Inspect only the preview image and metadata; keep html out of tool output.
```

Preview the final export at 728 pixels wide, then call `html_render` from code with the same `html` variable and `height` set to the preview's `contentHeight`, clamped to 80–2000. Print only metadata and images from these calls. If code transfer is unavailable, report the inline-preview limitation and finish with the file delivery in the main workflow.

Renderer payload and frame bounds apply only to this optional preview. Deliver the full exported file at its natural size and length; if it exceeds the renderer’s supported bounds, finish with file delivery.
