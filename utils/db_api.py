import aiosqlite
import datetime

DB_PATH = "data/bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS homework (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                grade TEXT,
                hw_date DATE NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS homework_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                homework_id INTEGER,
                file_id TEXT,
                file_type TEXT,
                FOREIGN KEY(homework_id) REFERENCES homework(id) ON DELETE CASCADE
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                day_name TEXT PRIMARY KEY,
                lessons TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY
            )
        """)
        await db.commit()

async def add_chat(chat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO chats (chat_id) VALUES (?)", (chat_id,))
        await db.commit()

async def get_all_chats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_id FROM chats") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def add_homework(subject, grade, hw_date, description, attachments=None):
    """
    attachments: list of dicts [{'file_id': '...', 'file_type': 'photo/document'}]
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO homework (subject, grade, hw_date, description)
            VALUES (?, ?, ?, ?)
        """, (subject, grade, hw_date, description))
        hw_id = cursor.lastrowid
        
        if attachments:
            for att in attachments:
                await db.execute("""
                    INSERT INTO homework_attachments (homework_id, file_id, file_type)
                    VALUES (?, ?, ?)
                """, (hw_id, att['file_id'], att['file_type']))
        
        await db.commit()
        return hw_id

async def get_homework_subjects(hw_date: datetime.date):
    """Get list of subjects that have homework for a specific date"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT DISTINCT subject FROM homework WHERE hw_date = ?
        """, (hw_date,)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def get_homework_by_subject(hw_date: datetime.date, subject: str):
    """Get homework and attachments for a specific subject and date"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT id, description, grade FROM homework 
            WHERE hw_date = ? AND subject = ?
        """, (hw_date, subject)) as cursor:
            hw_rows = await cursor.fetchall()
            
        results = []
        for row in hw_rows:
            hw_id, desc, grade = row
            # Get attachments
            async with db.execute("""
                SELECT file_id, file_type FROM homework_attachments WHERE homework_id = ?
            """, (hw_id,)) as att_cursor:
                att_rows = await att_cursor.fetchall()
                attachments = [{'file_id': r[0], 'file_type': r[1]} for r in att_rows]
            
            results.append({
                'id': hw_id,
                'description': desc,
                'grade': grade,
                'attachments': attachments
            })
        return results

async def get_homework(hw_date: datetime.date):
    # Backward compatibility wrapper or unused now?
    # We'll adapt it to return all HW for the date to support legacy/reminder logic if needed.
    # But for the new requirement, we primarily use subject filtering.
    pass 


async def update_schedule(day_name, lessons):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO schedule (day_name, lessons) VALUES (?, ?)
        """, (day_name, lessons))
        await db.commit()

async def get_schedule(day_name):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT lessons FROM schedule WHERE day_name = ?", (day_name,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def delete_homework(hw_date: datetime.date):
    """Delete all homework for a specific date (simplified for this example)"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM homework WHERE hw_date = ?", (hw_date,))
        await db.commit()

async def delete_homework_subject(hw_date: datetime.date, subject: str):
    """Delete homework for a specific subject and date"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM homework WHERE hw_date = ? AND subject = ?", (hw_date, subject))
        await db.commit()
async def get_schedule_subjects(date_obj: datetime.date) -> list:
    """Get list of subjects from the schedule for a specific date."""
    days_reverse = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    day_name = days_reverse[date_obj.weekday()]
    
    schedule_text = await get_schedule(day_name)
    subjects = []
    
    if schedule_text:
        import re
        for line in schedule_text.split('\n'):
            line = line.strip()
            if not line: continue
            # Try to match Number. Subject or just Subject
            match = re.match(r'^\d+[\.\)]\s*(.*)', line)
            if match:
                subjects.append(match.group(1).strip())
            else:
                subjects.append(line)
    return subjects
