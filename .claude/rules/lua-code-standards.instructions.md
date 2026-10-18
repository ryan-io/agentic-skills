---
applyTo: "**/*.lua"
paths:
  - "**/*.lua"
---

# Lua Code Standards

> **Full guidance:** `.github/docs/lua-code-standards-guide.md`

Extends `code-standards.instructions.md`. Sources: the Lua reference manuals, the LuaRocks and Olivine Labs style guides, the lua-users wiki style guide, "Lua Performance Tips" (Ierusalimschy). Review and setup procedure: the `lua-best-practices` skill.

## Language Version

Pin the target runtime and version per project; do not use a feature above it.

- Declare it twice: `runtime.version` in `.luarc.json` (LuaLS) and `std` in `.luacheckrc`. A rockspec also states `lua >= x.y`.
- Embedded hosts decide the version: Neovim is Lua 5.1 on LuaJIT, Roblox is Luau. Follow the host, not this file's defaults.
- No declared version and no host? Target Lua 5.4 and say so. Lua 5.5 (Dec 2025) waits until luacheck and StyLua ship a 5.5 target (2026-10-18: neither does).
- A portable library targets the 5.1 intersection (`std = "min"`).

| Trap | 5.1 / LuaJIT | 5.3 / 5.4 |
|---|---|---|
| Numbers | doubles only | integer and float subtypes; `3 // 2` is `1`, `3 / 2` is `1.5` |
| `tostring(2.0)` | `"2"` | `"2.0"` |
| `string.format("%d", 3.5)` | truncates | errors (no integer representation) |
| Unpack | `unpack` | `table.unpack` |
| Environments | `setfenv` / `getfenv` | `_ENV`, `load(src, name, "t", env)` |
| Bit ops | `bit` library (LuaJIT) | native `& \| ~ << >>` (5.3+) |
| `goto`, `utf8` | LuaJIT has `goto`; no `utf8` | both built in (`goto` 5.2+, `utf8` 5.3+) |
| `<const>` / `<close>` | absent | 5.4+ |
| String to number in arithmetic | core coercion | 5.4: string library metamethods, not core |

## Verify, Don't Recall

- Not 100% sure a function, operator, or library exists in the pinned version, or behaves as remembered? Check that version's reference manual first, then write it.
- A "faster" idiom claimed without a measurement is a guess; profile on the shipping runtime (PUC Lua and LuaJIT differ sharply).

## Naming

| Identifier | Convention | Example |
|---|---|---|
| Local, function, parameter, field | snake_case | `item_count`, `load_config` |
| Class (metatable prototype) | PascalCase | `BankAccount` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Private field or module-private helper | leading `_` on fields; `local function` for helpers | `self._cache` |
| Predicate | `is_` / `has_` prefix | `is_empty` |
| Ignored value | `_` | `for _, v in ipairs(t)` |
| Module file | lowercase, matches the `require` path | `net/http_client.lua` |

Never start a name with `_` plus uppercase (`_VERSION`): Lua reserves it. A host with its own convention (Roblox camelCase) wins.

## Scope and Modules

- Every variable is `local`. No globals; luacheck enforces it.
- Module shape: `local M = {}`, public functions as `function M.name()`, explicit `return M` at the end. Never `module()` (deprecated in 5.2).
- `require` into a local named after the module's last path component; requiring a module has no side effects beyond loading.
- Prefer `local function f()` over `local f = function()`.
- Narrow scope with `do ... end` where a temporary lives only a few lines.

## Error Handling

- Expected failure (I/O, parse, lookup miss): return `nil, err`. API misuse or broken invariant: raise with `error()` or `assert()`.
- `error(msg, 2)` blames the caller at a validation boundary. Structured errors are tables (`{ code = "E_PARSE", message = "..." }`), never `nil` (5.5 replaces a `nil` error object with a string).
- `pcall` / `xpcall` only at an owned boundary (a plugin call, a request handler, a script host); log or rethrow, never discard the second return value.

## Tables and Strings

- Arrays are 1-based. `#t` is defined only on a sequence; with holes it may return any border. Track an explicit count when holes are possible.
- `ipairs` stops at the first `nil`; `pairs` has no order guarantee. Sort keys when order matters.
- Only `nil` and `false` are falsy; `0` and `""` are true.
- Hot paths: build strings with a buffer and `table.concat`, never `..` in a loop; append with `t[#t + 1] = v` or a counter; cache globals and library functions in locals; reuse tables and closures instead of creating them per iteration.
- Varargs: count with `select("#", ...)`, which keeps trailing `nil`s; `#{...}` does not.

## Doc Comments

LuaCATS annotations (LuaLS): a one-sentence `---` summary, then `---@param`, `---@return`, `---@class`, `---@field`. Annotate every public module function and class. The summary-cap rule in `code-standards` applies.

## Formatting

StyLua is the formatter; commit a `stylua.toml`. Defaults here: 4-space indent (set `indent_type = "Spaces"`; StyLua's own default is tabs), 120 columns, Unix line endings, double quotes, call parentheses always (`require("x")`, not `require "x"`). A project's existing config wins.

## Linting

luacheck is the gate: zero warnings in CI. `.luacheckrc` sets `std` to the pinned version, declares host globals in `read_globals` (writable ones in `globals` only with a reason), and adds `+busted` for `spec/`. Inline `-- luacheck: ignore` carries a reason.

## Testing

busted by default: `spec/` folder, files named `*_spec.lua`, `describe` per unit, `it` per behavior, names reading as sentences (`it("returns nil and an error when the file is missing")`). `assert.are.same` for deep equality. Stub only at owned boundaries (I/O, clock, host API), revert after. LuaUnit is the fallback where LuaRocks is unavailable.

## Sandboxing

For untrusted scripts (mods, plugins, user config): load text only into an allowlisted environment (`load(src, name, "t", env)`; 5.1: `setfenv`), never expose `debug`, `io`, `os`, `load`, `require`, `rawset`, or `collectgarbage`, and cap runaway code with an instruction-count hook. Recipe and limits: the guide.
