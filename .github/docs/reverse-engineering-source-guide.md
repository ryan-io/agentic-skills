# Reverse Engineering Guide: Source in Hand

Companion to the `reverse-engineering` skill for targets that ship readable source: an addon, a vendored library, a legacy module, or a decompiled artifact handed on from the artifact guide. Carries the technique, the per-language lookups, and one host profile. Facts dated 2026-10-18 unless marked.

## What changes when you have source

Nothing is hidden, so the risk flips: reading everything is possible and wrong. Chikofsky and Cross call the work design recovery: the code gives the lowest rung, and domain knowledge plus deduction climb to components, responsibilities, and intent. The skill's loop runs unchanged; this guide says where to point it.

## First contact (OORP)

- **Read All the Code in One Hour.** One time-boxed pass over the tree. Note shape, not detail: entry points, the biggest files, naming conventions, anything duplicated.
- **Skim the Documentation.** README, changelog, issue tracker, forum threads. A changelog dates the design decisions; an issue tracker lists the known failure modes.
- **Interview During Demo.** Run it with a user, or play the user yourself. Each visible behavior becomes a hypothesis row before any code is read for it.
- **Chat with the Maintainers** where the project is alive. One answer can close a day of tracing.

## Initial understanding (OORP)

- **Analyze the Persistent Data.** Saved state, config files, schemas, serialized formats. The persisted shape is the domain model the code serves and changes slowest.
- **Speculate about Design.** Draw the component picture you expect, then read to confirm or refute it. Wrong guesses are the point: each refuted row is one less unknown.
- **Study the Exceptional Entities.** Sort units by size, fan-in, and fan-out. The outliers hold the logic worth the time.

## Detailed model capture (OORP)

- **Tie Code and Questions.** Keep the ledger beside the reading. A question with no code pointer goes back to first contact.
- **Refactor to Understand.** Rename, extract, and inline in a scratch copy to test a reading. Discard the edits; keep the understanding.
- **Step Through the Execution.** A debugger, trace prints, or the host's tooling (below). One traced run beats ten static readings of a callback chain.
- **Look for the Contracts.** How the code expects to be called: argument checks, invariants, event order. These become the Model's edges.
- **Learn from the Past.** Version history shows what kept changing. Volatile regions name the seams a port must keep.

## Pin behavior before trusting a reading

Feathers' characterization test: call the unit, assert whatever it returns today, keep the test. It pins behavior, correct or not, so a port or refactor can prove it preserved it. Write one per inferred row the work will rely on; the row moves to known when the test passes against the real target.

## Language lookups

### Lua

- **The API surface is the globals.** Grep for assignments to bare names and `_G`. Modules that return a table expose it; addons that write globals expose those. `rg -n "^\s*function [A-Za-z_]" --type lua` lists top-level functions.
- **Closures and upvalues carry state.** A `local` at file scope shared by several functions is a private field. Record it as one.
- **Metatables are the inheritance.** `setmetatable(x, {__index = Base})` is a class; `__call`, `__newindex`, and `__index` functions are the behavior to trace.
- **Events are the control flow.** In an event-driven host the call graph starts at registrations, not `main`. Grep the registration calls first (`RegisterEvent`, `hooksecurefunc`, a library's `:RegisterCallback`).
- **Pin the dialect** per `lua-code-standards.instructions.md` before reading: 5.1 versus 5.4 changes integer division, `unpack`, environments, and bit operations.
- **Bytecode in the tree.** `luac -l file.lua` lists the compiled instructions (`-l -l` for the full listing). A stripped chunk handed on from the artifact guide keeps no local names; treat every name in it as a guess.

### C# source

- The solution graph is the first map: `dotnet sln list`, then project references. Dependency direction is architecture.
- DI registrations (`AddSingleton`, `AddScoped`, a composition root) list the components and their contracts. Read those before any implementation.
- Entry points: `Program.Main`, hosted services, controllers, command handlers. One sequence diagram per entry point family.

## Host profile: World of Warcraft addon (2026-10-18)

Addons ship as plain Lua and XML, so this is the source case. Facts from https://warcraft.wiki.gg (TOC format, AddOn loading process, Lua functions, Secure Execution and Tainting); a project that depends on them records a dated note in `docs/research/` through `system-context`.

- **Runtime.** A modified Lua 5.1 with taint tracking. `io` and `os` are absent; `loadstring` is present. Blizzard adds string, table, and math helpers (`strsplit`, `wipe`, `tContains`, `Clamp`, `Lerp`) and aliases such as `tinsert` for `table.insert`.
- **Manifest.** `AddOnName.toc`, same name as the folder. `## Interface:` holds the client version as `major minor patch` digits (`12.1.5` is `120105`, comma-separated for several). `## SavedVariables:` and `## SavedVariablesPerCharacter:` name the globals persisted to `WTF\...\SavedVariables\`. `## Dependencies:` and `## OptionalDeps:` set load order. Per-flavor files (`_Mainline`, `_Classic`, `_Vanilla`) are tried before the plain name.
- **Load order.** Files run top to bottom as the TOC lists them; an XML `Include` or `Script` runs its file when reached. Saved variables load after the last file unless `## LoadSavedVariablesFirst` is set (Patch 11.1.5 and later). `ADDON_LOADED` (check the name argument) is the first point saved variables are readable; `PLAYER_LOGIN` fires once during the loading screen; `PLAYER_ENTERING_WORLD` fires on every loading screen.
- **Taint.** Execution starts secure and becomes tainted when it touches addon code or data; taint spreads through written values and persists until a reload. A protected function called from a tainted path fails, most visibly in combat. When tracing a failure, the question is where taint entered, not where it surfaced.
- **Libraries.** `LibStub` is the registry; `Ace3` (`AceAddon`, `AceDB`, `AceEvent`, `CallbackHandler`) is the common framework. An Ace addon's lifecycle is `OnInitialize` (after `ADDON_LOADED`), `OnEnable` (after `PLAYER_LOGIN`), `OnDisable`. `AceDB` saved variables fail silently when the TOC name and the `AceDB-3.0:New` name differ; check that first.
- **In-game tracing.** `/fstack` shows the frames under the cursor; `/tinspect` opens a table inspector; `/dump expr` prints a value; `/etrace` opens the event trace. Use them for the dynamic pass; they are Blizzard's own DebugTools.
- **Reading order that works.** TOC, then the saved-variables globals, then the event registrations, then the frames the registrations drive. Persistent data, control flow, UI: the OORP order.

## Sources

All accessed 2026-10-18.

- Chikofsky and Cross, "Reverse Engineering and Design Recovery: A Taxonomy," IEEE Software 7(1), 1990, pp. 13-17.
- Demeyer, Ducasse, Nierstrasz, Object-Oriented Reengineering Patterns, Morgan Kaufmann 2003; CC BY-SA edition: https://scg.unibe.ch/oorp/ and https://boris.unibe.ch/37172/1/OORP.pdf
- Feathers, Working Effectively with Legacy Code, Prentice Hall 2004.
- Lua 5.1 `luac` manual: https://www.lua.org/manual/5.1/luac.html
- Warcraft Wiki: https://warcraft.wiki.gg/wiki/TOC_format, https://warcraft.wiki.gg/wiki/AddOn_loading_process, https://warcraft.wiki.gg/wiki/Lua_functions, https://warcraft.wiki.gg/wiki/Secure_Execution_and_Tainting, https://warcraft.wiki.gg/wiki/MACRO_fstack, https://warcraft.wiki.gg/wiki/MACRO_dump, https://warcraft.wiki.gg/wiki/MACRO_eventtrace, https://warcraft.wiki.gg/wiki/WelcomeHome:_Your_first_Ace3_Addon
