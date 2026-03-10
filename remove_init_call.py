with open('e:\\ezh_helper\\main\\config3.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove the last line (init_chat_db call)
if lines and 'init_chat_db(-1003012971064)' in lines[-1]:
    lines = lines[:-1]
    
    with open('e:\\ezh_helper\\main\\config3.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Removed init_chat_db(-1003012971064) call from config3.py")
else:
    print("init_chat_db call not found at the end of file")
