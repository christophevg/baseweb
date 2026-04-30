# Coordination Plan: Baseweb ↔ Hosted-Quarts

**Created:** 2026-04-30
**Task:** task-2.2

## Relationship Summary

| Aspect | Description |
|--------|-------------|
| Type | Hosting platform |
| hosted-quarts role | Serves multiple Quart applications |
| baseweb role | One Quart application served by hosted-quarts |
| Code dependency | None - external service relationship |

## Dependency Matrix

| Project | Dependency | Version | Notes |
|---------|------------|---------|-------|
| baseweb | None on hosted-quarts | N/A | Independent package |
| hosted-quarts | None on baseweb code | N/A | Hosts as external service |

## Integration Points

| Integration | Type | Impact of Baseweb Migration |
|-------------|------|----------------------------|
| Application hosting | Runtime | Baseweb must be async-compatible Quart app |
| Deployment | Infrastructure | No changes required |
| Configuration | Environment | May need async-compatible ASGI server |

## Migration Timeline

### Parallel Development (Recommended)

Both projects can migrate independently:
- **Baseweb:** Flask → Quart migration (Phase 3)
- **Hosted-Quarts:** Prepare to serve async Quart apps
- **Existing apps:** Update code to async patterns

### Coordinated Production Upgrade

Production upgrade requires:
1. Baseweb 1.0.0 released
2. Hosted-quarts ready to serve Quart apps
3. All existing baseweb applications migrated and tested

**Recommendation:** Stage changes in development environment, then upgrade all production systems together.

## Shared Considerations

### Testing Strategy

1. **Unit tests:** Each project tests independently
2. **Integration tests:** Test baseweb apps served by hosted-quarts in staging
3. **Production validation:** Smoke tests after coordinated upgrade

### Communication Points

- Baseweb 1.0.0 release candidate availability
- Hosted-quarts async support readiness
- Existing application migration status
- Production upgrade window scheduling

## Recommendations

1. **No tight coupling:** Projects can be developed independently
2. **Staged rollout:** Development → Staging → Production
3. **Migration guide:** Use docs/migration-guide.md for existing applications
4. **Coordinated upgrade:** Schedule production upgrade when all components ready

## Acceptance Criteria Status

| Criteria | Status | Evidence |
|----------|--------|----------|
| Dependency matrix documented | ✓ | This document |
| Migration timeline aligned | ✓ | Parallel development, coordinated upgrade |
| Shared code/dependencies | ✓ | None identified |