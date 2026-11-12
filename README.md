# VCollab Claude Plugin Marketplace

A Claude Code plugin marketplace for the VCollab team. It holds two plugins: **VCollab**, which connects Claude to a local VCollab installation for working
with CAE and CAD simulation files, and **CAE Viewpoint Report**, which reviews a CAX or native CAE model and builds
a viewpoint report, a CAX with rich viewpoints and a WCAX.

## Plugins

| Plugin | Version | What it does |
|---|---|---|
| [`vcollab`](plugins/vcollab-plugin) | 0.2.0 | Inspect, convert, merge, and render CAE and CAD files with your local VCollab 26.1+ install on Windows: native results to CAX, CAX metadata, result images, and VCollab Pro XML batch jobs. Adds a VCollab workflow skill and a CAE result-review skill. |
| [`cae-viewpoint-report`](plugins/cae-viewpoint-report) | 0.2.0 | Senior CAE review of a `.cax` or native solver file (converted automatically with VMoveCAEBatch) delivered as three files: viewpoint Markdown report, CAX with rich PPT-style viewpoints (text, tables, charts, verified probes) and WCAX with the same viewpoints, built with your local VCollab Pro 26.1+. |

See each plugin's README ([vcollab](plugins/vcollab-plugin/README.md),
[cae-viewpoint-report](plugins/cae-viewpoint-report/README.md)) for requirements, settings, tools and
troubleshooting.

## Install

In Claude Code 2.1.275 or later, install in one step:

```
/plugin install vcollab --marketplace vcollab/vct-marketplace
```

Or add the marketplace first, then install from it:

```
/plugin marketplace add vcollab/vct-marketplace
/plugin install vcollab@vct-marketplace
/plugin install cae-viewpoint-report@vct-marketplace
```

To pick up new versions later, run `/plugin marketplace update vct-marketplace`.

## Repository layout

```
.claude-plugin/
  marketplace.json        Marketplace manifest: lists the plugins below
plugins/
  vcollab-plugin/
    .claude-plugin/
      plugin.json         Plugin manifest: name, version, settings
    .mcp.json             Starts the local MCP server with uv
    src/vcollab_mcp/      MCP server and tools (Python)
    skills/               vcollab-workflows and cae-expert skills
  cae-viewpoint-report/
    .claude-plugin/       plugin.json
    .mcp.json             Starts the stdlib MCP server (vp_server.py) with uv
    server/               MCP server + VCollab Pro batch job scripts
    skills/               cae-viewpoint-report skill (review method, MD format, examples)
    commands/             /viewpoint-report
```

## Adding or updating a plugin

1. Put the plugin in its own folder under `plugins/`, with a `.claude-plugin/plugin.json`.
2. Add an entry to `.claude-plugin/marketplace.json`. Its `name` must match the `name` in the
   plugin's `plugin.json`, and `source` is the relative path to the plugin folder.
3. For a new release, bump `version` in the plugin's `plugin.json`.
4. Validate both the marketplace and the plugin before pushing:

   ```
   claude plugin validate .
   claude plugin validate ./plugins/vcollab-plugin
   claude plugin validate ./plugins/cae-viewpoint-report
   ```

## Support

Open an issue at https://github.com/vcollab/vct-marketplace/issues or email
srinivasamurthi@vcollab.com.

## License

Both plugins are MIT licensed; see [vcollab](plugins/vcollab-plugin/LICENSE) and
[cae-viewpoint-report](plugins/cae-viewpoint-report/LICENSE). VCollab
itself is commercial software licensed separately.
