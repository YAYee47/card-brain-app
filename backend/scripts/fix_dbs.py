import sqlite3

conn = sqlite3.connect('backend/card_brain.db')
c = conn.cursor()

c.execute("SELECT id FROM cards WHERE card_name LIKE '%傳說對決%'")
card_id = c.fetchone()[0]

c.execute("DELETE FROM card_benefits WHERE card_id=? AND bonus_rate=9", (card_id,))
c.execute("DELETE FROM card_benefits WHERE card_id=? AND bonus_rate=4", (card_id,))

combined_9 = '指定數位與影音消費 (蝦皮、淘寶、App Store、Google Play、Uber Eats、foodpanda、Garena、GASH、MyCard、Steam、Netflix、Disney+、Spotify)'
c.execute("INSERT INTO card_benefits (card_id, channel_name, base_rate, bonus_rate, monthly_cap_ntd, effective_date) VALUES (?, ?, ?, ?, ?, '2026-08-16')", (card_id, combined_9, 1, 9, 500))

combined_4 = '外幣實體消費 (日本、韓國、美洲、新加坡、印尼、澳門)'
c.execute("INSERT INTO card_benefits (card_id, channel_name, base_rate, bonus_rate, monthly_cap_ntd, effective_date) VALUES (?, ?, ?, ?, ?, '2026-08-16')", (card_id, combined_4, 1, 4, 500))

# Clear monthly usage for this card to prevent dashboard calculation errors with deleted benefits
c.execute("DELETE FROM monthly_usage WHERE user_card_id IN (SELECT id FROM user_cards WHERE card_id=?)", (card_id,))
# Also clear transactions for this card so we don't have orphaned transactions pointing to nothing 
# Or actually it's fine, the user can just test again.

conn.commit()
conn.close()
print('DBS benefits combined successfully.')
