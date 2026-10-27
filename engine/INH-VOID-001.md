# Inheritance Rule INH-VOID-001

Every architectural layer SHALL inherit its view of a memory artefact from the database record when that artefact's pool_status is 'void'.

No layer may promote, cache, or re-identify a void artefact independently of the database.

Applies to: Identity Rail, Compile Engine, Governance Kernel, Descriptor, Skill, Hash Tree.

Status: project-defined, recorded in 6185-Code-Construct-Hash-Pool.db
