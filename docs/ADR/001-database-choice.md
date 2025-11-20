# ADR 001: PostgreSQL as Primary Database

**Date**: 2025-11-20
**Status**: Accepted
**Context**: Need to select primary database for e-commerce analytics platform

## Decision

Use PostgreSQL 15 as the primary database for MarketPulse.

## Rationale

**Technical Requirements:**
- ACID compliance for financial transaction data integrity
- Complex analytical queries with aggregations and joins
- Support for stored procedures (SQL injection prevention)
- Database views for common analytics patterns
- Strong indexing capabilities for performance

**Production Readiness:**
- Industry standard in Israeli tech companies
- Mature ecosystem with excellent tooling (pgAdmin, psql)
- Proven scalability for analytics workloads
- Free and open-source (no licensing costs)

**Analytics Capabilities:**
- Native support for window functions and CTEs
- JSONB for flexible schema when needed
- Built-in analytics views (`v_daily_revenue`, `v_product_performance`, `v_customer_analytics`)
- Excellent aggregation performance

**Security:**
- Stored procedures for data modification operations
- Role-based access control (RBAC)
- Connection pooling support via SQLAlchemy
- Prepared statement support

## Alternatives Considered

### MySQL
- **Pros**: Widely used, good performance
- **Cons**: Less robust JSON support, weaker window functions, less suitable for complex analytics
- **Verdict**: Rejected - insufficient analytics capabilities

### MongoDB
- **Pros**: Flexible schema, horizontal scaling
- **Cons**: No ACID guarantees, harder to ensure data consistency for financial data, less mature analytics
- **Verdict**: Rejected - transaction data requires strong consistency

### SQLite
- **Pros**: Zero configuration, embedded
- **Cons**: Not suitable for production scale, no concurrent writes, limited connection pooling
- **Verdict**: Rejected - not production-ready

## Implementation Details

**Schema Design:**
- Primary table: `transactions` with BIGSERIAL primary key
- Unique constraint on `transaction_id` for deduplication
- Indexes on: `transaction_date`, `status`, `customer_name`, `product`, `amount`
- Auto-updating timestamps via triggers
- CHECK constraints for data validation

**Connection Management:**
- SQLAlchemy ORM with connection pooling
- Pool size: 5 connections + 10 overflow
- Pre-ping enabled for connection validation
- Connection recycling every 3600 seconds

**Security Implementation:**
- Stored procedures: `insert_transaction()`, `upsert_transaction()`
- All writes through prepared statements
- No raw SQL with user input
- Input validation via CHECK constraints

## Consequences

### Positive
- Strong data consistency and integrity
- Complex query capabilities for analytics
- Industry-standard tooling and knowledge base
- Excellent performance with proper indexing
- Security through stored procedures

### Negative
- Requires proper connection pooling configuration
- Vertical scaling limitations (addressed via indexing)
- Migration complexity if switching databases later
- Requires PostgreSQL expertise for optimization

### Neutral
- Must maintain database schema migrations
- Backup and recovery procedures needed
- Monitoring required for production deployment

## Performance Metrics

**Current Results:**
- ETL: 10,000 records in <5 seconds
- Index creation: Instantaneous on 10k records
- Query performance: All analytics views <50ms

**Expected at Scale:**
- Target: <200ms for all API queries
- Indexing strategy supports 100k+ records
- Connection pooling prevents exhaustion

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/)
- [SQLAlchemy Connection Pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- Knowledge Base: `Database Engineering/01_postgresql_guide.md`

## Review

This decision should be reviewed if:
- Dataset size exceeds 1M transactions (consider partitioning)
- Query performance degrades significantly
- Need for horizontal scaling emerges
- Real-time requirements change significantly

---

**Last Updated**: 2025-11-20
**Next Review**: After 100k transactions milestone
