---
name: lua-best-practices
description: >
  Apply, review against, and set up Lua coding standards for the project's pinned runtime (Lua
  5.1 to 5.5, LuaJIT, or a host such as Neovim). Invoke implicitly when a .lua file is created
  or edited and the project has no Lua standards of its own, or when the developer asks "is this
  idiomatic Lua", "review this Lua", "how do I do X in Lua", "set up luacheck/busted/StyLua".
  Establishes the runtime version first, defers to the project's own conventions, applies
  lua-code-standards.instructions.md with the guide for the deeper how, reports reviews in the
  Severity/Category format, and scaffolds .luacheckrc, stylua.toml, .luarc.json, and a busted
  spec/ folder.
tags: [code-standards, lua, skill]
---

# Lua Best Practices

Apply the Lua standards to real code: write, review, or set up a project. This skill is a procedure; the rules live in `lua-code-standards.instructions.md` and the rationale in `.github/docs/lua-code-standards-guide.md`.

## When to use

- A `.lua` file is created or edited and the project carries no Lua standards of its own.
- The developer asks for a Lua review, an idiom check, a how-to, or tooling setup.
- Skip it where the project's own Lua rules exist and answer the question: follow those.

## Procedure

1. **Establish the runtime and version.** Read, in order: `.luarc.json` (`runtime.version`), `.luacheckrc` (`std`), a `*.rockspec` (`lua >= x.y`), `stylua.toml` (`syntax`), then the host's docs (Neovim: Lua 5.1 on LuaJIT; Roblox: Luau). State the result in one line: "Target: LuaJIT 2.1 (5.1 language), from `.luarc.json`." Sources disagree, or none exist? Ask; don't guess. A new standalone project with no host defaults to Lua 5.4, said aloud.
2. **Check the project's own standards first** (`pattern-fidelity`). Existing StyLua or luacheck config, a host style guide, or the neighboring files' naming and module shape win over this skill's defaults. Note each place you follow the project over the defaults.
3. **Apply the rules.** Work from the instruction file: version traps, naming, `local M = {}` modules, `nil, err` versus `error()`, table and string hot-path rules, LuaCATS annotations. Open the guide only for the deeper how: version table, examples, performance notes, sandbox recipe. Unsure an API exists in the pinned version? Check that version's manual before writing it.
4. **Review.** Report each finding in the `pr-review.instructions.md` format, one severity and one category per finding, with file and line:
   - `**Blocker/Bug**: utils.lua:42 uses table.unpack, absent on the pinned LuaJIT build without 5.2 compat. Use unpack, or a local alias set once.`
   - `**Nitpick/Code Style**: parser.lua:10 assigns a global; declare it local.`
   - Priority: version-incompatible calls, accidental globals, swallowed `pcall` errors, and `#` on tables with holes before style. Run `luacheck` and `stylua --check` where installed and report their output, not a guess at it.
5. **Set up tooling** on request or when scaffolding a new Lua project. Write each file with a one-line reason; skip any the project already has (revise it instead, step 6):
   - `.luacheckrc`: `std` set to the pinned version, host globals in `read_globals`, `+busted` for `spec/`. Reason: luacheck is the lint gate and catches accidental globals.
   - `stylua.toml`: `syntax` for the pinned version, `indent_type = "Spaces"`, `indent_width = 4`. Reason: one formatter ends style debate; StyLua's own default is tabs.
   - `.luarc.json`: `$schema`, `runtime.version`, `diagnostics.globals`. Reason: LuaLS needs the version to flag missing APIs and check LuaCATS types.
   - `spec/<module>_spec.lua`: one busted example. Reason: proves the test runner and naming convention work.

   ```lua
   local greeter = require("greeter")

   describe("greeter.greet", function()
       it("returns a greeting that includes the name", function()
           assert.are.equal("hi Ada", greeter.greet("Ada"))
       end)
   end)
   ```

   Then run `luacheck .`, `stylua --check .`, and `busted` where installed, and report the result. A tool not installed is named as a skipped step, never reported green.
6. **Revise an existing artifact.** For a config file or spec that already exists: read it first, apply only the requested change, preserve every other setting and its conventions, confirm with the developer before overwriting, and save to the same path unless the developer renames it.

## Guardrails

- Changing a project's formatter settings, indent, or naming convention is the developer's call: present the options and a recommendation, then stop.
- A sandbox for untrusted scripts is a security boundary. Follow the guide's recipe, state its limits, and record the design in an ADR under `docs/adr/` if the project has none.
- Never commit. Suggest one conventional commit subject (for example `build(lua): add luacheck, StyLua, and busted config`) and stop.

## Done

- The runtime and version are stated with their source.
- Code follows the project's conventions, then the instruction file; every deviation is named.
- A review lists findings in Severity/Category form; a setup lists each file written with its reason and the tool runs, green or skipped.
