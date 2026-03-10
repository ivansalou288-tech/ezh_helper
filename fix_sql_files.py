import os

def fix_sql_file(filename):
    """Add IF NOT EXISTS to CREATE TABLE statements"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace CREATE TABLE with CREATE TABLE IF NOT EXISTS
    content = content.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {filename}")

# Fix all SQL files
sql_files = [
    'e:\\ezh_helper\\{-chat_id}.sql',
    'e:\\ezh_helper\\all.sql', 
    'e:\\ezh_helper\\admin.sql'
]

for sql_file in sql_files:
    if os.path.exists(sql_file):
        fix_sql_file(sql_file)
    else:
        print(f"File {sql_file} not found")

print("All SQL files fixed!")
