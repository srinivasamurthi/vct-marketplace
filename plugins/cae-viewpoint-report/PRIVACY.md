# Privacy Policy: CAE Viewpoint Report plugin for Claude

Effective 2026-11-12. Applies to version 0.1.0 and later of the CAE Viewpoint Report plugin.

## Data collection

The plugin collects no personal data. It has no accounts, no analytics, and no telemetry.

When you ask Claude to use a tool, the plugin receives the arguments for that call (file paths and
options) and reads the files you name. It uses them only to run VCollab Pro on your computer.

## Use and storage

- Models are processed locally by VCollab Pro in batch mode. Outputs (the viewpoint Markdown file,
  the CAX, the WCAX, HTML panels, chart images, screenshots and a contact sheet) are written to the
  output folder you choose, by default `<model folder>\<model>_viewpoints\`.
- Each job keeps its script, progress log, VCollab console log and result summary in
  `<output folder>\_jobs\<job id>\` so a run can be diagnosed. These files can contain file paths
  and result values from your model. Delete the folder whenever you like.
- The MCP server uses only the Python standard library; uv may provide a Python runtime on first
  start.

## Third-party sharing

The plugin sends no data to VCollab or any third party. The review text that Claude writes is
produced in your Claude conversation and is subject to Anthropic's terms for that conversation.

## Contact

Open an issue at https://github.com/vcollab/vct-marketplace/issues or email
srinivasamurthi@vcollab.com.
