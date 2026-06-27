import socket
import os
import sys

# --- إعدادات الألوان والخلفيات النصية (هوية التطبيق) ---
CLEAR = "\033[H\033[2J"         # أمر مسح الشاشة لبدء التطبيق بشكل نظيف
RESET = "\033[0m"               # إعادة تعيين الألوان للوضع الافتراضي
BOLD = "\033[1m"                # خط عريض
TEXT_CYAN = "\033[1;36m"        # نص تركوازي أنيق
SUCCESS_GREEN = "\033[1;32m"    # نص أخضر للعمليات الناجحة
ERROR_RED = "\033[1;31m"        # نص أحمر للتنبيهات والأخطاء
BG_BANNER = "\033[1;30;46m"     # نص أسود عريض على خلفية تركوازية مذهلة

def get_local_ip():
    """دالة ذكية لمعرفة الـ IP الخاص بجهازك تلقائياً دون تعقيد"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def send_file():
    file_path = input(f"\n{TEXT_CYAN}[*] اسحب الملف هنا أو اكتب مساره الكامل: {RESET}").strip().strip("'\"")
    if not os.path.exists(file_path):
        print(f"{ERROR_RED}[-] الخطأ: الملف غير موجود! تأكد من المسار.{RESET}")
        return
    
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 9999))
    server.listen(1)
    
    print(f"\n{SUCCESS_GREEN}[+] عنوان الـ IP الخاص بك هو: {get_local_ip()}{RESET}")
    print(f"{TEXT_CYAN}[*] افتح التطبيق في الجهاز الآخر واكتب هذا الـ IP للاتصال...{RESET}")
    print(f"{TEXT_CYAN}[*] بانتظار الاتصال على منفذ 9999...{RESET}")
    
    conn, addr = server.accept()
    print(f"{SUCCESS_GREEN}[+] تم الاتصال بنجاح مع الجهاز: {addr}{RESET}")
    
    # إرسال البيانات الأساسية للملف
    conn.send(f"{file_name}|{file_size}".encode('utf-8'))
    
    print(f"{TEXT_CYAN}[*] جاري ضخ الملف بأقصى سرعة للشبكة...{RESET}")
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(65536) # التدفق الخارق بحجم 64 كيلوبايت
            if not chunk:
                break
            conn.sendall(chunk)
            
    print(f"\n{SUCCESS_GREEN}[+] تم إرسال الملف بنجاح تام!{RESET}")
    conn.close()
    server.close()

def receive_file():
    sender_ip = input(f"\n{TEXT_CYAN}[*] أدخل عنوان IP الخاص بجهاز المرسل: {RESET}").strip()
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((sender_ip, 9999))
    except Exception as e:
        print(f"{ERROR_RED}[-] فشل الاتصال بالمرسل: {e}{RESET}")
        return
        
    header = client.recv(1024).decode('utf-8')
    file_name, file_size = header.split('|')
    file_size = int(file_size)
    
    print(f"{SUCCESS_GREEN}[+] جاري استقبال: {file_name} | الحجم: ({file_size / (1024*1024):.2f} ميجابايت){RESET}")
    
    # مسار الحفظ المباشر في مجلد الـ Download بالهاتف
    save_path = f"/sdcard/Download/{file_name}"
    
    received_bytes = 0
    with open(save_path, 'wb') as f:
        while received_bytes < file_size:
            chunk = client.recv(65536)
            if not chunk:
                break
            f.write(chunk)
            received_bytes += len(chunk)
            
            # العداد الحي لنسبة تقدم النقل
            percent = (received_bytes / file_size) * 100
            print(f"\r{TEXT_CYAN}جاري الاستقبال: {percent:.2f}%{RESET}", end="")
            
    print(f"\n{SUCCESS_GREEN}[+] مبروك! اكتمل الاستقبال وحُفظ في الـ Downloads باسم: {file_name}{RESET}")
    client.close()

if __name__ == "__main__":
    # تنظيف الشاشة وعرض الواجهة الملونة المصممة لك
    print(CLEAR)
    print(f"{BG_BANNER}=================================================={RESET}")
    print(f"{BG_BANNER}        تطبيق ABU ALHASAN للنقل السريع الخارق       {RESET}")
    print(f"{BG_BANNER}=================================================={RESET}")
    print(f"\n{TEXT_CYAN}1. إرسال ملف (Send){RESET}")
    print(f"{TEXT_CYAN}2. استقبال ملف (Receive){RESET}")
    
    choice = input(f"\n{BOLD}اختر العملية (1 أو 2): {RESET}").strip()
    
    if choice == '1':
        send_file()
    elif choice == '2':
        receive_file()
    else:
        print(f"{ERROR_RED}[-] اختيار خاطئ، أعد تشغيل التطبيق.{RESET}")
