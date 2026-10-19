# Reverse Engineering Guide: Compiled Artifact in Hand

Companion to the `reverse-engineering` skill for targets that arrive compiled: a .NET assembly, Lua bytecode, a native binary. The job here is to get back to readable source, then hand on to `reverse-engineering-source-guide.md`. Facts dated 2026-10-18 unless marked.

## What changes when you have an artifact

Names, comments, and structure are partly or wholly gone. Every identifier in a decompiled listing is a hypothesis, and the hypothesis ledger starts at the naming level. Eilam's rule for the whole discipline applies: form a theory of what a routine does, then look for the evidence that would break it.

## Permission first

An artifact is the form most licenses and terms of use speak about. Before the first decompile, record in the dossier's `license` field what allows the study and the intended use. Interoperability, porting your own data out, security audit under authorization, and study of a library you are licensed to use are the ordinary cases. A protection, a license check, or an anti-tamper measure in the way is a stop, not a puzzle.

## Decompile by format

| Format | Tell | Tool (status 2026-10-18) | Output |
|---|---|---|---|
| .NET assembly | PE with a CLI header; `dotnet` metadata | ILSpy 11.1 (Sep 2026); `ilspycmd` as a dotnet tool for batch output | a C# project tree, readable; names survive unless obfuscated |
| .NET assembly, to debug | same | dnSpyEx (unofficial continuation of dnSpy; .NET 8 and Framework 4.8 builds) | step through IL and decompiled C# live |
| Lua 5.1 bytecode | chunk begins with `\27Lua` | `luac -l -l` for the listing; unluac (Java, Lua 5.0 to 5.4, updated Jan 2026) for source when debug info is present | source with local names if not stripped; positional names otherwise |
| Native binary | ELF, PE, or Mach-O with no managed header | Ghidra (The Ghidra Book); a debugger for the dynamic pass | pseudo-C per function; structure recovery is manual |

Confirm a tool's current release before relying on a version here; decompilers move. A tool not installed is a named gap in the dossier, never a guessed result.

## .NET specifics

- Decompile to a project with `ilspycmd` so symbol search works on the result. Search the output, not the binary.
- Obfuscation shows as unreadable names, string encryption, control-flow flattening, or a packer stub. Record which; a deobfuscation step is its own hypothesis and often out of scope.
- Metadata survives obfuscation better than code: attributes, resource names, public contracts, and DI registration strings are the first map.
- Dang et al. cover the Windows kernel and native side; for managed code the metadata tables and IL opcode reference are the primary sources.

## Lua bytecode specifics

- `luac -l` prints constants, upvalues, and one line per instruction with the source line when debug info is kept. A stripped chunk (`luac -s`) keeps instructions only.
- unluac needs the debug info; without it, expect positional names (`L0`, `L1`) and rename as the ledger moves rows to known.
- LuaJIT bytecode is a different format (`\27LJ`) and needs LuaJIT-aware tooling; do not point 5.1 tools at it.
- Once decompiled, the host profile in the source guide applies (for an addon, the TOC, load order, and taint model).

## Native specifics

- Static first in Ghidra: imports, strings, and cross-references give the inventory. Rename as you learn; the rename is the ledger row.
- Dynamic second: a debugger or tracer on the real input. Eilam's method is theory, then breakpoint, then confirm.
- Structure recovery (types, vtables, state machines) is the Model step; expect it to be the slowest and keep it bounded by the question.

## Handing on

The decompiled tree is now source. Record in the dossier's Inventory what was recovered, what was stripped, and which names are guesses, then continue with the source guide's first contact. The ledger keeps its artifact-level rows; the source pass adds design-level ones above them.

## Sources

All accessed 2026-10-18.

- Eilam, Reversing: Secrets of Reverse Engineering, Wiley 2005, ISBN 978-0-7645-7481-8.
- Dang, Gazet, Bachaalany, Practical Reverse Engineering, Wiley Feb 2014, ISBN 978-1-118-78731-1.
- Eagle and Nance, The Ghidra Book, No Starch 2020.
- ILSpy releases: https://github.com/icsharpcode/ILSpy/releases
- dnSpyEx: https://github.com/dnSpyEx/dnSpy
- Lua 5.1 `luac`: https://www.lua.org/manual/5.1/luac.html
- unluac: https://sourceforge.net/projects/unluac/ (README mirrored at https://gitee.com/TieScript/unluac)
- Ghidra: https://ghidra-sre.org/
