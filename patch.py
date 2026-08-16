import os

files_to_patch = {
    r'backend\app\models\cards.py': [
        ('icon_emoji: Mapped[str] = mapped_column(String(10), nullable=True, default="💳")', '')
    ],
    r'backend\app\schemas\cards.py': [
        ('icon_emoji: Optional[str] = "💳"', '')
    ],
    r'backend\app\schemas\dashboard.py': [
        ('icon_emoji: str', '')
    ],
    r'backend\app\schemas\recommend.py': [
        ('icon_emoji: str', '')
    ],
    r'backend\app\services\dashboard.py': [
        ('icon_emoji=card.icon_emoji or "💳",', '')
    ],
    r'backend\app\services\recommend.py': [
        ('icon_emoji: str', ''),
        ('icon_emoji=card.icon_emoji or "💳",', '')
    ],
    r'backend\app\api\v1\endpoints\recommend.py': [
        ('icon_emoji=r.icon_emoji,', '')
    ],
    r'mobile\app\(tabs)\index.tsx': [
        ('<Text style={styles.cardIcon}>{card.icon_emoji}</Text>', '')
    ],
    r'mobile\app\(tabs)\scan.tsx': [
        ("<Text style={styles.cardPickerIcon}>{selectedUserCard?.card.icon_emoji ?? '💳'}</Text>", ''),
        ('<Text style={styles.modalCardIcon}>{uc.card.icon_emoji}</Text>', '')
    ],
    r'mobile\src\api\cards.ts': [
        ('icon_emoji: string;', '')
    ],
    r'mobile\src\api\dashboard.ts': [
        ('icon_emoji: string;', '')
    ],
    r'mobile\src\api\recommend.ts': [
        ('icon_emoji: string;', '')
    ]
}

for fp, replacements in files_to_patch.items():
    if not os.path.exists(fp): continue
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
