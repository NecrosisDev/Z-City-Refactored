# ZCity Mode Catalog

**Work package:** `WP-RESEARCH-001`  
**Branch:** `docs/architecture-baseline`  
**Runtime source baseline:** `429ec928203cec963176dfb6afd086dcdd01c181`  
**Status:** `partial / executable-source verified`  
**Reviewed:** 2026-07-12

This catalog records actual registration IDs, files, inheritance, lifecycle, network/data contracts, dependencies, verified defects, and validation. Directory names and client presentation entries are not treated as launchable modes until executable registration is verified.

## Verified dependency graph

```text
zb.modes
├─ tdm                                  standalone base
│  └─ cstrike                           MODE.base = "tdm"
├─ dm                                   standalone
└─ hmcd                                 standalone base registry entry
   ├─ standard                          server MODE.Types + SubModes
   ├─ wildwest                          server MODE.Types + SubModes
   ├─ gunfreezone                       server MODE.Types + SubModes
   ├─ soe                               server MODE.Types + SubModes
   ├─ suicidelunatic                    client presentation only in traced files
   ├─ supermario                        client presentation + server branch, no verified server type registration
   └─ fear                              MODE.base = "hmcd"
      ├─ standard2                      inherited former `standard`
      └─ soe2                           inherited former `soe`
```

`zb:GetMode(submode)` maps a registered `MODE.Types` key back to its owning registry key. `RoundInfo` sends the base registry key; Homicide-family modes separately send their active `MODE.Type`.

## Summary matrix

| ID | Directory | Base | Files verified | Effective launch contract | Primary dependencies |
|---|---|---|---|---|---|
| `tdm` | `tdm` | none | `sh_tdm.lua`, `sv_tdm.lua`, `cl_tdm.lua` | unconditional `true` | teams, inventory, classes, roles, attachments, armor, weapons, map points |
| `cstrike` | `tdm_cstrike` | `tdm` | `sh_cstrike.lua`, `sv_cstrike.lua`, `cl_cstrike.lua` | unconditional `true`; earlier point validator overwritten | TDM, bomb/hostage entities, organism, map points, harm tracking |
| `dm` | `dm` | none | `sh_dm.lua`, `sv_dm.lua`, `cl_dm.lua` | unconditional `true` | organism, appearance, armor, weapons, zone globals, entity iteration, harm tracking |
| `hmcd` | `homicide` | none | `sh_homicide.lua`, `sv_homicide.lua`, `cl_homicide.lua` | unconditional `true`; four verified server submodes | organism, fake ragdoll, appearance, inventory, classes, roles, loot, weapons, persistence |
| `fear` | `homicide_fear` | `hmcd` | `core/sh_fear.lua`, `core/sv_fear.lua`, `core/cl_fear.lua`, `sv_scary_black_guy.lua` | hard-disabled (`CanLaunch() == false`) | all Homicide contracts, light sampling, disappearance/afterlife state, props, sounds, scare entities/bots |

---

## `MODE-tdm` — Team Deathmatch

### Contract

- Files: `sh_tdm.lua` `1aa70fac...`; `sv_tdm.lua` `5dfaa969...`; `cl_tdm.lua` `c6e42546...`.
- `BuyTime=40`, `StartMoney=6500`, `start_time=20`, `ROUND_TIME=240`, `Chance=.04`, `ForBigMaps=true`, `buymenu=true`.
- `Intermission()` cleans map, resets teams/money and broadcasts `tdm_start` without fields. Client reads a string, starts music and removes fade.
- Equipment sets class/role/cosmetics/inventory; winner uses alive-team logic; end awards results and sends `tdm_roundend`.
- Buy request is `{category,itemName[,attachmentID]}`. Server checks mode/time/catalog/money/weapon ownership but not alive state, rate/size, `TeamBased`, or attachment membership.

### Verified defects

- Base `tdm_start` schema mismatch; CStrike happens to write the string expected by the inherited receiver.
- Dot-defined `GuiltCheck` receives dispatcher-injected mode table as its first argument.
- Arbitrary attachment IDs reach `hg.AddAttachmentForce`; `TeamBased` is ignored.
- Opening movement lock is duplicated; empty callbacks may suppress fallback behavior.

### Validation

Full cycle; missing points; team/disconnect/incapacitation; packet capture; malformed/oversized/rate-flooded purchases; attachment allowlist; wrong-team/dead-player purchase; latency/prediction.

---

## `MODE-cstrike` — Counter-Strike TDM derivative

### Contract

- Files: `sh_cstrike.lua` `66a341d1...`; `sv_cstrike.lua` `f194fe0a...`; `cl_cstrike.lua` `843e2b89...`.
- `base="tdm"`, `Rounds=5`, `ROUND_TIME=240`, multi-round bomb/hostage objectives and inherited buy/start/end surfaces.
- Intermission chooses objective, sends points, spawns objective after delay, writes round type via `tdm_start`, and sends `CS_Intermission`.
- `RoundStartPost()` queues another `cstrike`; end computes objective winner, pays teams, sends `CS_Roundover`, tracks series wins and clears state when leaving.

### Verified defects

- Point-validating `CanLaunch()` is overwritten by unconditional `true`.
- Empty team can cause `math.random(0)` during delayed objective assignment.
- Numeric winner `0|1|3` is written with `net.WriteBool`, collapsing identity because all Lua numbers are truthy.
- Unsorted directory order can register child before base.
- Multi-round state spans mode/global selection and is vulnerable to off-by-one/cleanup errors.
- `HarmDone` pays damage amount times `KillMoney`; objective/entity/organism/point validity is assumed.

### Validation

Reverse registration order; missing point combinations; zero/one team; bomb/hostage outcomes; packet matrix; exact series count; reconnect/team preservation; economy bounds; mode exit/re-entry cleanup.

---

## `MODE-dm` — Deathmatch with shrinking zone

### Contract

- Files: `sh_dm.lua` `04291057...`; `sv_dm.lua` `f645861d...`; `cl_dm.lua` `4e7cce0f...`.
- Intermission averages non-spectator positions to form a zone and sends vector+float. One loadout is selected for all alive players.
- Server scans all entities every .5 seconds while active, stunning players, blasting doors and dissolving props outside the zone.
- End condition is one-or-fewer alive; `dm_end` sends winner and most-violent entity.

### Verified defects

- No participants causes division by zero.
- Unscoped zone globals can remain stale; hooks fall through when `CurrentRound()` is nil.
- Full entity sweep has no partition/budget.
- Delayed player callback lacks validity; winner and most-violent may receive duplicate rewards.
- Missing zone state returns `0xFFFFFFFF`, masking initialization failure; remote-music/global remnants remain.

### Validation

Zero/one/many players; spectator-only/reconnect; zone on/off and full shrink; entity stress; stale state across mode changes; loadout failure; duplicate reward; audio cleanup.

---

## `MODE-hmcd` — Homicide base and submode family

### Contract

- Files: `sh_homicide.lua` `79d5b5e8...`; `sv_homicide.lua` `af101a8e...`; `cl_homicide.lua` `6e15a2b3...`.
- `start_time=1`, `end_time=7`, `ROUND_TIME=600`, chance `.2`, random/override spawn and loot enabled, unconditional launch.
- Verified server submodes: `soe`, `standard`, `wildwest`, `gunfreezone`. Client also presents `suicidelunatic`/`supermario`, but no verified server registrations exist.
- Owns traitor/gunner/police/subrole/profession state, reinforcement timing, role selection, words, persistence and broad organism/inventory/class/equipment mutations.

### `HMCD_RoundStart`

Ordered payload: traitor bool; gunner bool; type string; screen-default bool; subrole string; main-traitor bool; two word strings; uint traitor count; conditional color+name roster; profession string. The count includes all traitors, while roster entries require `CurAppearance`; a missing appearance underwrites the packet and shifts later reads. There is no version or independent roster count.

Other verified surfaces include role-selection start/end, subrole, traitor death/status, assistant updates and `hmcd_roundend` entity arrays.

### Verified defects

1. Role selection hard-returns false.
2. Requested-main-traitor consumer is commented out.
3. Reset listens for stale round state `2` rather than verified end state `3`.
4. Police attachment code uses undefined `gun` before declaration; `if math.random(0,1)` is always truthy.
5. `SpawnForce` compares possibly nil `afkTime2`.
6. `HMCD_RoundStart` can desynchronize on missing appearance.
7. Extra client submodes appear unreachable.
8. Helpers/dot-defined functions become hook candidates; registrations are duplicated; entities/equipment are assumed valid.
9. Start/end mutate many systems, so local testing cannot establish integration safety.

### Validation

Pair every packet branch; test missing appearances and assistant counts; verify all role/reinforcement paths and submodes across population/AFK/disconnect/incapacitation/equipment failures; classify every function; resolve stale client-only types.

---

## `MODE-fear` — Homicide2 / Fear derivative

### Files, inheritance and launch state

- `core/sh_fear.lua` blob `9797dd2cde5ffccdb4e231be80311a96630173f5`: `base="hmcd"`, `name="fear"`, event registry, per-player event hooks/timers and disappearance collision rule.
- `core/sv_fear.lua` blob `bbc02e7223f5e4fbcacae87c49471b1bf6254daa`: hard-disables launch, converts inherited `standard`/`soe` to `standard2`/`soe2`, removes other inherited types, runs horror lifecycle/victim selection.
- `core/cl_fear.lua` blob `e53fdb48d83e61555932931a68e488f47109edc3`: disappearance rendering, client light sampling, afterlife effects/audio and ambient fear timers.
- `sv_scary_black_guy.lua` blob `ea9c96fe21fc79cd067328eb11a635d7d54297e0`: registers event `scary_black_guy` that spawns an `ent_zc_anim` visible only to one victim.
- `CanLaunch()` returns false; mode is force/admin-only unless another system overrides eligibility.

### Lifecycle and state

- `AfterBaseInheritance()` aliases inherited Homicide types then removes originals; unsorted base registration remains a hard dependency.
- Intermission kills/resets players, selects only `standard2|soe2`, disables police, starts global random-environment timers and sends a Homicide-compatible round-start branch only if inherited role-selection logic says so.
- No traitors are selected (`traitors_needed=0`). Round ends only when no alive players remain.
- `RoundThink()` calls `self.BaseClass.RoundThink(self)`, periodically asks all clients to sample one target's light color, selects a victim, then kills, prop-attacks, breaks neck, starts scare event, disappears, creates `bot_fear`, or manipulates suicide behavior.
- Disappearance disables collision/visibility and may transition into a timed afterlife; return-to-life uses recurring visibility checks.
- Client suppresses shadows/sounds, samples render light, applies post-processing/ghost audio, ambient sounds and last-survivor effects.

### Network and public surfaces

- `check_lightness` is bidirectional: server broadcasts target entity; every client returns a vector. Server accepts one response per client while a global `checkedPlayer` is set and lerps all responses into that player's light color.
- Player network state: `disappearance`, local `afterlife` start, NWFloat `willsuicide`, collision rules, `lightcolor` and average velocity/harm heuristics.
- Dynamic hooks/timers: `Think/ScareThatGuy<UserID>`, `PlayerUse/dooruse<EntIndex>`, global timer names such as `WaitForRandomStuff`, `FearRandomStuff`, `Fear_End`, `FearSounds`, `fear*`, `disappearance <EntIndex>`, `Afterlife <EntIndex>`, `ReturnToLife <EntIndex>`.
- External surfaces: `ent_zc_anim`, `bot_fear`, `hg.BreakNeck`, fake ragdoll, visibility/light APIs, `SendLua`, sound files and global stations/notification flags.

### Verified defects and risks

1. **Inheritance/load-order hazard:** Fear cannot initialize correctly if `hmcd` is not already registered; mode-directory order is unsorted.
2. **Hard-disabled but globally active hooks:** direct hooks in loaded Fear files can exist even when the mode is not launchable; each must be verified as mode-gated.
3. **Nil event crash:** `StartEvent(name)` copies `MODE.Events[name]` and immediately calls it without validating existence.
4. **Ignored start failure:** `StartScare()` can return false, but caller keeps an event entry/hook.
5. **Event cleanup leak:** event `StopScare()` removes its entity but does not clear `MODE.StartedEvents` or its Think hook directly.
6. **Scare timer validity bug:** delayed callback returns when player is valid/alive, then calls `ply:SendLua` only when invalid/dead, risking method access on invalid player.
7. **Entity validity assumptions:** `ent_zc_anim`, `bot_fear`, door selection, physics objects, bone matrices and active weapon traces are used without complete validation. `RandomStuff()` can dereference `door` when none was found.
8. **Typo breaks victim selection:** calculation assigns `vicitm` (misspelled) and returns it; the initially chosen local `victim` is never returned. Selection can be nil or stale global.
9. **Client-authoritative light data:** any client can submit a bounded RGB vector for the global current target; server averages untrusted values without target identity, proximity, visibility, rate attribution or authoritative sampling.
10. **Global response race:** `checkedPlayer`/`checkPlayers` are shared across all clients and reset after .5 seconds; latency/order changes victim darkness assessment.
11. **Return-to-life logic flaw:** it captures the alive-player list once; within the loop, the first player who is not looking causes immediate return even if another player is looking.
12. **Unbounded expensive scans:** `RandomStuff()` traverses all entities, and prop-kill repeatedly scans nearby entities/physics; hooks/timers are global-name based.
13. **Global side effects:** scare event uses `SendLua("stopsound")` and fades every player for one victim; client uses global stations/flags and aggressive post-processing.
14. **Sound callback assumes channel validity:** `sound.PlayFile` callbacks call channel methods without validating channel in multiple paths.
15. **Last-player instant kill:** when one player remains, RoundThink kills them directly; core round winner/result semantics are bypassed.
16. **Base lifecycle coupling:** Fear calls inherited Homicide `RoundThink` despite replacing role setup/end semantics; all inherited side effects need explicit audit.
17. **Timer and UserID reuse:** event state keyed by UserID and names based on EntIndex/UserID can collide across reconnects/hotload.
18. **Rendering state ownership:** client shadow suppression toggles entity/player/weapon shadows but has no centralized restoration pass for disconnect/mode change/error.

### Required validation

- Force-load with Fear before/after HMCD and compare registry/types/callback sets.
- Confirm no Fear hooks/effects execute while another mode is active.
- Fuzz unknown/missing events and failed entity creation.
- Validate every dynamic timer/hook is removed on death, disconnect, end, cleanup and hotload.
- Replace/validate light sampling against malicious, delayed and missing clients; verify one authoritative target and schema.
- Test no-door maps, invalid physics/bones/weapons, one/many players, disappearance visibility groups, afterlife return, sound failures and rendering restoration.
- Trace inherited Homicide callbacks and packets to determine which are intentionally retained versus accidental.

## Next mode trace

1. Complete Counter-Strike bomb/hostage entity/client contracts and unresolved Homicide channel endpoints.
2. Build the complete mode-function classification/collision matrix.
3. Build a cross-mode packet matrix with writer, reader, ordered schema, validation, limits and legacy/duplicate status.
4. Continue remaining actual mode directories and resolve client-only/unreachable registrations.