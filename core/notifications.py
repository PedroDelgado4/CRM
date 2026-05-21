import sqlite3
from core.database import get_connection

def get_all_alerts(user_id):
    conn = get_connection()
    alerts = []
    if not conn: return alerts

    try:
        cursor = conn.cursor()

        # 🔴 ROJO: Tareas Atrasadas (Interacciones pendientes de hoy o antes)
        cursor.execute("""
            SELECT c.full_name, i.note, i.reminder_date
            FROM interactions i
            LEFT JOIN contacts c ON i.contact_id = c.id
            WHERE c.assigned_to = ? AND LOWER(i.status) = 'pending' AND i.reminder_date <= DATE('now')
        """, (user_id,))
        for row in cursor.fetchall():
            alerts.append({"title": "Overdue Task", "msg": f"{row[0]}: {row[1]}", "color": "#ff4d4d"})

        # 🔴 ROJO: Propuestas Caducadas
        cursor.execute("""
            SELECT name, proposal_deadline FROM opportunities
            WHERE assigned_to = ? AND LOWER(status) IN ('qualification', 'proposal') AND proposal_deadline < DATE('now')
        """, (user_id,))
        for row in cursor.fetchall():
            alerts.append({"title": "Expired Proposal", "msg": f"Opp: {row[0]} (Deadline: {row[1]})", "color": "#ff4d4d"})

        # 🟠 NARANJA: Propuestas a entregar hoy/mañana
        cursor.execute("""
            SELECT name, proposal_deadline FROM opportunities
            WHERE assigned_to = ? AND LOWER(status) IN ('qualification', 'proposal') AND proposal_deadline BETWEEN DATE('now') AND DATE('now', '+1 day')
        """, (user_id,))
        for row in cursor.fetchall():
            alerts.append({"title": "Proposal Due Soon", "msg": f"Opp: {row[0]} (Deadline: {row[1]})", "color": "#ff9f43"})

        # 🟠 NARANJA: Oportunidades enfriándose (> 7 días sin contacto)
        cursor.execute("""
            SELECT name, last_contact FROM opportunities
            WHERE assigned_to = ? AND LOWER(priority) IN ('very_high', 'high') AND LOWER(status) NOT IN ('closed_won', 'closed_lost')
            AND (last_contact < DATE('now', '-7 days') OR last_contact IS NULL)
        """, (user_id,))
        for row in cursor.fetchall():
            alerts.append({"title": "Neglected Opportunity", "msg": f"Opp: {row[0]} (Last contact: {row[1] or 'Never'})", "color": "#ff9f43"})

        # 🟡 AMARILLO: Cierres inminentes esta semana
        cursor.execute("""
            SELECT name, expected_close_date FROM opportunities
            WHERE assigned_to = ? AND LOWER(status) NOT IN ('closed_won', 'closed_lost')
            AND expected_close_date BETWEEN DATE('now') AND DATE('now', '+7 days')
        """, (user_id,))
        for row in cursor.fetchall():
            alerts.append({"title": "Closing This Week", "msg": f"Opp: {row[0]} (Expected: {row[1]})", "color": "#f1c40f"})

    except Exception as e:
        print(f"Error fetching alerts: {e}")
    finally:
        conn.close()

    return alerts