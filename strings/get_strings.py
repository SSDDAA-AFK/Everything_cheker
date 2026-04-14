import re
import os
import sys

def extract_strings(file_path, min_len=4):
    """Витягує читабельні рядки з бінарного файлу (EXE/DLL/JAR)."""
    if not os.path.exists(file_path):
        print(f"\n[!] Помилка: Файл '{file_path}' не знайдено!")
        print("Покладіть лоадер в цю ж папку і перейменуйте в 'loader.exe' або вкажіть назву в коді.")
        return

    print(f"\n[*] Починаю аналіз файлу: {file_path}")
    print("[*] Це може зайняти кілька секунд для великих файлів...")
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"[!] Не вдалося прочитати файл: {e}")
        return

    # 1. Шукаємо ASCII рядки (стандартний текст)
    ascii_re = rb"[\x20-\x7E]{" + str(min_len).encode() + rb",}"
    ascii_strings = [s.decode('ascii', errors='ignore') for s in re.findall(ascii_re, data)]

    # 2. Шукаємо UTF-16 рядки (часто в Windows програмах)
    utf16_re = rb"(?:[\x20-\x7E]\x00){" + str(min_len).encode() + rb",}"
    utf16_matches = re.findall(utf16_re, data)
    utf16_strings = []
    for s in utf16_matches:
        try:
            utf16_strings.append(s.decode('utf-16le'))
        except:
            pass

    # Об'єднуємо та видаляємо дублікати
    all_strings = sorted(list(set(ascii_strings + utf16_strings)))

    # Зберігаємо результат
    output_file = "strings_report.txt"
    try:
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(f"--- STRINGS REPORT FOR: {file_path} ---\n")
            out.write(f"--- Found {len(all_strings)} unique strings ---\n\n")
            for s in all_strings:
                # Фільтруємо сміття (залишаємо рядки від 4 до 250 символів)
                if 4 <= len(s) <= 250:
                    out.write(s + "\n")
        
        print(f"\n[+] Готово! Знайдено {len(all_strings)} унікальних рядків.")
        print(f"[+] Результати збережено у файл: {output_file}")
    except Exception as e:
        print(f"[!] Помилка при записі звіту: {e}")

# Назва файлу для сканування
# Поклади лоадер поруч і вкажи його назву тут:
TARGET_FILE = "loader.exe" 

if __name__ == "__main__":
    # Якщо ти хочеш вказати назву через консоль: python get_strings.py MyCheat.exe
    if len(sys.argv) > 1:
        TARGET_FILE = sys.argv[1]
    
    extract_strings(TARGET_FILE)
