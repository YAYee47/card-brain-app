import sqlite3

conn = sqlite3.connect('backend/card_brain.db')
c = conn.cursor()

c.execute("SELECT id FROM cards WHERE card_name LIKE '%JCB%'")
card_id = c.fetchone()[0]

c.execute("DELETE FROM card_benefits WHERE card_id=? AND bonus_rate=3 AND monthly_cap_ntd=300", (card_id,))

combined_jcb = '特選網購與百貨 (蝦皮、momo、PChome、淘寶、東森、YAHOO、friDay、台灣樂天、生活市集、Amazon、酷澎、漢神巨蛋、漢神百貨、遠東SOGO、遠東百貨、日本實體)'
c.execute("INSERT INTO card_benefits (card_id, channel_name, base_rate, bonus_rate, monthly_cap_ntd, effective_date) VALUES (?, ?, ?, ?, ?, '2026-08-16')", (card_id, combined_jcb, 1, 3, 300))

# Clear monthly usage
c.execute("DELETE FROM monthly_usage")
# Clear transactions
c.execute("DELETE FROM transactions")

conn.commit()
conn.close()
print('JCB benefits combined successfully, and all DB data cleared as requested.')
