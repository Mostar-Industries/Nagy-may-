import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL || "")

export async function logAuditEvent(
  userId: string | null,
  action: string,
  tableName: string,
  recordId: string | null,
  changes?: Record<string, unknown>,
) {
  try {
    await sql`
      INSERT INTO audit_logs (user_id, action, table_name, record_id, changes)
      VALUES (${userId}, ${action}, ${tableName}, ${recordId}, ${JSON.stringify(changes || {})})
    `
  } catch (error) {
    console.error("[v0] Audit logging error:", error)
  }
}

export async function getAuditLog(userId: string, limit = 50) {
  try {
    const logs = await sql`
      SELECT * FROM audit_logs
      WHERE user_id = ${userId}
      ORDER BY created_at DESC
      LIMIT ${limit}
    `
    return logs
  } catch (error) {
    console.error("[v0] Audit retrieval error:", error)
    return []
  }
}
