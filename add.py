import csv


def add_qa_to_md(filename="qa.md"):
    """Добавляет вопросы и ответы в markdown файл в формате <details>"""
    
    print("Введите вопросы и ответы. Для завершения оставьте вопрос пустым.")
    
    with open(filename, "a", encoding="utf-8") as md_file:
        while True:
            question = input("\nВведите вопрос (или нажмите Enter для завершения): ").strip()
            if not question:
                break
                
            answer = input("Введите ответ: ").strip()
            
            md_entry = f"""
<details><summary>{question}</summary>
{answer}
</details>
"""
            md_file.write(md_entry)
            print(f"Добавлено в {filename}!")
    
    print(f"\nГотово! Результаты сохранены в {filename}")


def parse_without_regex(md_filename, csv_filename):
    with open(md_filename, 'r', encoding='utf-8') as md_file:
        lines = md_file.readlines()
    
    qa_pairs = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('<details><summary>'):
            question = lines[i].replace('<details><summary>', '').replace('</summary>', '').strip()
            answer_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('</details>'):
                answer_lines.append(lines[i].strip())
                i += 1
            answer = ' '.join(answer_lines)
            qa_pairs.append((question, answer))
        i += 1
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Question', 'Answer'])
        writer.writerows(qa_pairs)
    
    print(f"Спаршено {len(qa_pairs)} вопросов. Результат в {csv_filename}")



# def parse_without_regex(md_filename, csv_filename):
#     with open(md_filename, 'r', encoding='utf-8') as md_file:
#         lines = md_file.readlines()
    
#     qa_pairs = []
#     i = 0
#     while i < len(lines):
#         if lines[i].startswith('<details><summary>'):
#             # Извлекаем вопрос
#             question = lines[i].replace('<details><summary>', '').replace('</summary>', '').strip()
            
#             # Извлекаем ответ с сохранением переносов строк
#             answer_lines = []
#             i += 1
#             while i < len(lines) and not lines[i].strip().startswith('</details>'):
#                 answer_lines.append(lines[i].rstrip('\n'))  # Удаляем только символы новой строки в конце
#                 i += 1
            
#             # Объединяем строки ответа с сохранением переносов
#             answer = '\n'.join(answer_lines).strip()
#             qa_pairs.append((question, answer))
#         i += 1
    
#     # Записываем в CSV с экранированием переносов строк
#     with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
#         writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)  # QUOTE_ALL чтобы все значения были в кавычках
#         writer.writerow(['Question', 'Answer'])
#         for question, answer in qa_pairs:
#             # Заменяем переносы строк на специальный маркер, если нужно
#             # Или просто записываем как есть (CSV поддерживает переносы в кавычках)
#             writer.writerow([question, answer])
    
#     print(f"Спаршено {len(qa_pairs)} вопросов. Результат в {csv_filename}")

# Запуск функции
if __name__ == "__main__":
    # add_qa_to_md()
    parse_without_regex("PYTHON_BASE.md", "test.csv")