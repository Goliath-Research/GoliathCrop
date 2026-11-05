-- GoliathCrop Phase 1 — RBAC notes
--
-- Semantic requests reference these permission names (register via GoliathApp RBAC admin
-- or a future crop permission seeder aligned with Meta ObjValues):
--   crop.field.read, crop.field.write
--   crop.planting.read
--   crop.operation.read, crop.operation.write
--   crop.trial.read
--
-- Planned crop roles (owner, agronomist, operator, viewer, researcher) and Role2Node
-- grants are applied per organization scope after roles exist — see docs/plan.md NavTree.

SELECT 1;
