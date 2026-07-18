<!-- Always created alongside .agent/skills/, from this template. Scaffolds with just the table
header — skills get added to this file over time as real .agent/skills/<name>/ folders are
created, never invented at setup. If step 3 of SKILL.md happened to turn up existing
tool-agnostic skill content worth seeding, add one real row per skill found; otherwise leave the
table with just the header, ready for the first skill. A row doesn't have to point at
.agent/skills/<name>/ — an existing .claude/skills/<name>/ (Claude Code's own skill format) gets a
row pointing at .claude/skills/<name>/SKILL.md instead, per step 6 of SKILL.md: cross-referenced,
not duplicated. See AGENTS.md's "Skills" section and "Creating a Feature / Reference / Task /
Skill" for the format each row corresponds to. Delete this comment when done. -->

# Skills Index

One line per skill: what it does, and when an agent should load it. Full instructions live in
each skill's own `.agent/skills/<skill-name>/SKILL.md` — this table exists so an agent doesn't
have to open every folder to find the right one.

| Skill | When to use it |
|---|---|
