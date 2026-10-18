# Lua Code Standards Guide

Companion to `lua-code-standards.instructions.md` (mirror `.claude/rules/lua-code-standards.instructions.md`). Carries the rationale, examples, and sources too long for the rule file. Facts dated 2026-10-18 unless marked.

## Version Landscape

| Runtime | Status (2026-10-18) | Where it shows up |
|---|---|---|
| Lua 5.1 | frozen at 5.1.5 (2012) | the language LuaJIT, Neovim, and many engines expose |
| LuaJIT 2.1 | maintained, recommended for production; 2.0 is bugfix-only | Neovim, LÖVE, OpenResty, game engines |
| Lua 5.3 | frozen at 5.3.6 (2020) | older embedded hosts |
| Lua 5.4 | 5.4.9 (Aug 2026), no further releases planned | current standalone default |
| Lua 5.5 | 5.5.1 (Aug 2026), released Dec 2025 | new; lint and format tooling lagging |
| Luau | Roblox's 5.1 derivative, gradual types | Roblox only; its own style guide applies |

Why 5.4 is the default when nothing is declared: it is the newest line every tool targets. luacheck v1.2.0 offers `lua51` through `lua54` stds and no `lua55`; StyLua's `syntax` option lists `Lua51` to `Lua54`, `LuaJIT`, `Luau`, and `CfxLua`. LuaLS already accepts `"Lua 5.5"`. Revisit when luacheck and StyLua add 5.5.

Neovim states it outright: "Lua 5.1 is the permanent interface for Nvim Lua", built on LuaJIT where available. Plugins write 5.1 and gate LuaJIT-only code on `jit`.

## Version Differences in Full

| Area | 5.1 | LuaJIT 2.1 | 5.2 | 5.3 | 5.4 | 5.5 |
|---|---|---|---|---|---|---|
| Number type | double | double | double | integer + float subtypes | same | same |
| Integer division `//` | no | no | no | yes | yes | yes |
| Bitwise ops | none | `bit` module | `bit32` library | native operators, 64-bit; `bit32` deprecated | native | native |
| `goto` / labels | no | yes | yes | yes | yes | yes |
| Environments | `setfenv` | `setfenv`; `load` takes `env` | `_ENV`; `setfenv` removed | `_ENV` | `_ENV` | `_ENV`; `global` declarations, `global` is reserved |
| `unpack` | global | global; `table.unpack` with 5.2 compat build | `table.unpack` | `table.unpack` | `table.unpack` | `table.unpack` |
| `loadstring` | yes | yes | deprecated, use `load` | `load` | `load` | `load` |
| `module()` | yes | yes | deprecated | removed | removed | removed |
| `utf8` library | no | no | no | yes | yes, rejects surrogates by default | yes |
| `<const>` / `<close>` | no | no | no | no | yes | yes |
| String coercion in arithmetic | core | core | core | core | string metamethods only | same |
| `tostring(2.0)` | `"2"` | `"2"` | `"2"` | `"2.0"` | `"2.0"` | `"2.0"` |
| `%d` with a non-integral float | truncates | truncates | truncates | error | error | error |
| For-loop control variable | "should not change" (unenforced) | same | same | same | same | read-only |
| GC modes | incremental | incremental | incremental (+ generational, experimental) | incremental | incremental + generational | `collectgarbage("param", ...)` replaces mode tuning args |

Overflowing decimal integer literals read as floats from 5.4. `math.type(x)` and `math.tointeger(x)` (5.3+) separate the subtypes.

## Style Guides: Where They Disagree

| Point | lua-users wiki | Olivine Labs | LuaRocks | Roblox | Neovim repo | Chosen default |
|---|---|---|---|---|---|---|
| Indent | 2 spaces | 2 spaces | 3 spaces | tabs | 2 spaces | 4 spaces |
| Functions, locals | lowercase, underscores optional | snake_case | snake_case | camelCase | snake_case (its API) | snake_case |
| Classes | PascalCase or not | PascalCase factories | CamelCase | PascalCase | n/a | PascalCase |
| Constants | ALL_CAPS | unstated | UPPER_CASE, sparingly | LOUD_SNAKE_CASE | n/a | UPPER_SNAKE_CASE |
| Quotes | unstated | single | double | n/a | prefer single | double |
| Line length | unstated | 80 | no limit | 100 | 100 | 120 |
| Function form | `local function` | `local function` | `local function` | `local function` | n/a | `local function` |

Reasons for each default:

- **4 spaces.** The formatter enforces whatever is picked, so the deciding factor is consistency with the project's other stacks (C# at 4). StyLua's `indent_width` defaults to 4; set `indent_type = "Spaces"` because its type default is tabs. The Lua community's majority is 2 spaces (PiL, the manual, Neovim); a project that prefers it changes one config line.
- **snake_case.** Matches the standard library's lowercase names and three of five guides. Roblox camelCase is a host convention: follow it on Roblox.
- **Double quotes, 120 columns, call parentheses always.** These are StyLua's and luacheck's defaults, so a fresh project needs no overrides. LuaRocks also wants `require("x")` with parentheses because it "is a regular Lua function call".

## Modules and Classes

```lua
-- Before: 5.1 module() leaks a global and exposes _G through the module table.
module(..., package.seeall)
function greet(name) return "hi " .. name end

-- After:
local M = {}

---Return a greeting for the given name.
---@param name string
---@return string
function M.greet(name)
    return "hi " .. name
end

return M
```

A class is a metatable prototype:

```lua
---@class BankAccount
---@field balance number
local BankAccount = {}
BankAccount.__index = BankAccount

---Create an account with a zero balance.
---@return BankAccount
function BankAccount.new()
    return setmetatable({ balance = 0 }, BankAccount)
end

function BankAccount:deposit(amount) -- called as account:deposit(10)
    self.balance = self.balance + amount
end

return BankAccount
```

## Error Handling

```lua
local function read_file(path) -- expected failure: return nil, err
    local f, err = io.open(path, "r")
    if not f then return nil, err end
    local data = f:read("a") -- 5.1 / LuaJIT: "*a"
    f:close()
    return data
end

local function set_volume(level) -- misuse: raise, blaming the caller
    if type(level) ~= "number" or level < 0 or level > 1 then
        error("set_volume: level must be a number in [0, 1]", 2)
    end
end

local ok, err = pcall(plugin.run, context) -- one owned boundary
if not ok then log.error("plugin failed", { plugin = plugin.name, error = err }) end
```

## Tables, Strings, and Performance

Ierusalimschy's measurements ("Lua Performance Tips", Lua Programming Gems, 2008, Lua 5.1.1 on a Pentium IV) are old; the ratios guide, the numbers do not. His two rules come first: "Don't do it" and "Don't do it yet", and measure before and after.

| Tip | Measured effect (2008) |
|---|---|
| Cache `math.sin` in a local outside the loop | about 30% faster |
| Build closures instead of compiling with `loadstring` | 1.4 s to 0.14 s for 100,000 functions |
| Size small tables with a constructor (`{ true, true, true }`) | 2.0 s to 0.7 s for 1,000,000 tables |
| Buffer pieces and `table.concat` instead of `s = s .. x` | reads a 5 MB file in 0.28 s; the `..` loop is quadratic |
| Hoist constant tables and closures out of loops | avoids one allocation per iteration |
| Memoize with a weak table (`__mode = "kv"`) | cache entries collectable when unused |

Other facts from the same paper: a table never shrinks when fields are set to `nil`, only on a later rehash, so drop the table rather than clear a huge one; `{ [1] = true }` builds a hash part, not an array part. Holes: `#{ 10, 20, 30, nil, 50 }` may return 3 or 5 (the 5.4 manual's non-sequence example), so store `n` explicitly, as `table.pack` does. LuaJIT changes the cost model (traces, FFI); profile there separately.

```lua
-- Before: quadratic.
local s = ""
for _, line in ipairs(lines) do s = s .. line .. "\n" end

-- After: linear.
local buf = {}
for i, line in ipairs(lines) do buf[i] = line end
local s = table.concat(buf, "\n")
```

## Doc Comments

LuaCATS (Lua Comment And Type System) is LuaLS's annotation dialect, derived from EmmyLua; as of LuaLS v3 the two are no longer cross-compatible. Syntax: `---@param name[?] type [description]`, `---@return type [name] [# comment]`, `---@class Name[: Parent]`, `---@field name type`. One `---` summary sentence above the annotations.

## Tooling Configuration

Only non-default values are set; 120 columns, Unix endings, double quotes, and call parentheses are already the tool defaults.

```lua
-- .luacheckrc
std = "lua54"                 -- the pinned runtime (lua51, luajit, ...)
read_globals = { "host_api" } -- injected by the embedding host
files["spec/**/*_spec.lua"] = { std = "+busted" }
```

```toml
# stylua.toml
syntax = "Lua54"
indent_type = "Spaces"
indent_width = 4
```

```json
{ "$schema": "https://raw.githubusercontent.com/LuaLS/vscode-lua/master/setting/schema.json",
  "runtime.version": "Lua 5.4", "diagnostics.globals": ["host_api"] }
```

## Sandboxing Untrusted Scripts

Recipe (5.2+; hooks are per coroutine, so run the chunk in its own):

```lua
local SAFE = { "assert", "error", "ipairs", "next", "pairs", "pcall", "select",
    "tonumber", "tostring", "type", "xpcall" }

local function copy(t) local c = {} for k, v in pairs(t) do c[k] = v end return c end

local function run_untrusted(src, api, budget)
    local env = { string = copy(string), table = copy(table), math = copy(math), api = api }
    for _, name in ipairs(SAFE) do env[name] = _G[name] end
    local chunk, err = load(src, "=untrusted", "t", env) -- "t": refuse bytecode
    if not chunk then return nil, err end
    local co = coroutine.create(chunk)
    debug.sethook(co, function() error("instruction budget exceeded", 0) end, "", budget)
    local ok, result = coroutine.resume(co)
    if not ok then return nil, result end
    return true, result
end
```

Limits to state, not hide:

- 5.1: use `loadstring` plus `setfenv(chunk, env)`, and reject binary chunks (first byte `\27`) yourself; 5.1 `loadstring` accepts bytecode, which can crash the VM.
- The count hook does not interrupt a long-running C function (`string.rep` of a huge size, a pathological pattern match). Memory is not capped from Lua; the host sets a limiting allocator (`lua_setallocf`).
- Strings share one metatable whose `__index` is the real `string` table, so `("x"):rep(n)` stays reachable. Never expose `getmetatable`, `setmetatable` on shared tables, `rawset`, `debug`, `io`, `os`, `load`, `dofile`, `require`, or `collectgarbage`.
- Expose host verbs through a narrow `api` table, never the host's internals.
- LuaJIT: confirm count hooks fire for JIT-compiled code before relying on them (not verified for this guide).

## Sources

All accessed 2026-10-18.

- Lua releases and manuals (5.3 for `string.format`; 5.4 for borders, attributes, `load`, `debug.sethook`; section 8 of each for incompatibilities): https://www.lua.org/versions.html, https://www.lua.org/manual/5.1/manual.html, https://www.lua.org/manual/5.2/manual.html, https://www.lua.org/manual/5.3/manual.html, https://www.lua.org/manual/5.4/manual.html, https://www.lua.org/manual/5.5/manual.html
- Programming in Lua, fourth edition (Lua 5.3): https://www.lua.org/pil/
- Lua Programming Gems and "Lua Performance Tips": https://www.lua.org/gems/, https://www.lua.org/gems/sample.pdf
- LuaJIT and Luau: https://luajit.org/extensions.html, https://luajit.org/status.html, https://luau.org/syntax
- Style guides: http://lua-users.org/wiki/LuaStyleGuide, https://github.com/Olivine-Labs/lua-style-guide, https://github.com/luarocks/lua-style-guide, https://roblox.github.io/lua-style-guide/
- Neovim (Lua 5.1 interface; repo StyLua config): https://neovim.io/doc/user/lua.html, https://raw.githubusercontent.com/neovim/neovim/master/.stylua.toml
- Sandboxing: http://lua-users.org/wiki/SandBoxes
- Tooling: https://github.com/JohnnyMorganz/StyLua, https://github.com/lunarmodules/luacheck, https://luacheck.readthedocs.io/en/stable/config.html, https://luacheck.readthedocs.io/en/stable/cli.html
- LuaLS and LuaCATS: https://github.com/LuaLS/lua-language-server, https://luals.github.io/wiki/annotations/, https://luals.github.io/wiki/configuration/, https://raw.githubusercontent.com/LuaLS/vscode-lua/master/setting/schema.json
- Tests and packages: https://lunarmodules.github.io/busted/, https://github.com/bluebird75/luaunit, https://luarocks.org/, https://github.com/luarocks/luarocks/blob/main/docs/rockspec_format.md
