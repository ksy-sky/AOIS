"""
Главный модуль с интерактивным меню для работы с хеш-таблицей.
Вариант 4: квадратичное пробирование.
Тематика: Биология.
"""

from src.hash_table import HashTable
from src.constants import DEFAULT_TABLE_SIZE


def print_header(title: str) -> None:
    """Печать красивого заголовка."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_menu() -> None:
    """Вывод меню."""
    print("\n" + "-" * 50)
    print(" МЕНЮ:")
    print("  1. Показать всю таблицу")
    print("  2. Показать V и h для всех записей")
    print("  3. Добавить новый термин")
    print("  4. Найти термин по ключу")
    print("  5. Обновить описание термина")
    print("  6. Удалить термин")
    print("  7. Показать статистику")
    print("  8. Показать коллизии (отладка)")
    print("  0. Выход")
    print("-" * 50)


def display_table(table: HashTable) -> None:
    """Вывод таблицы."""
    print_header("ТЕКУЩЕЕ СОСТОЯНИЕ ХЕШ-ТАБЛИЦЫ")
    print(table.display())


def display_hash_info(table: HashTable) -> None:
    """Вывод V и h для всех записей."""
    print_header("V и h для всех записей")
    records = table.get_all_records()
    
    if not records:
        print("  Таблица пуста. Добавьте несколько записей.")
        return
    
    print(f"\n{'Ключ':<20} {'V':<8} {'h':<4}")
    print("-" * 35)
    for record in records:
        key = record["id"]
        v_value, hash_address = table.get_hash_info(key)
        print(f"{key:<20} {v_value:<8} {hash_address:<4}")


def add_term(table: HashTable) -> None:
    """Добавление нового термина."""
    print_header("ДОБАВЛЕНИЕ НОВОГО ТЕРМИНА")
    
    key = input("  Введите ключевое слово (например, 'Лизосома'): ").strip()
    if not key:
        print("   Ключ не может быть пустым!")
        return
    
    data = input("  Введите описание: ").strip()
    if not data:
        print("   Описание не может быть пустым!")
        return
    
    # Проверяем, есть ли уже такой ключ
    existing = table.search(key)
    if existing:
        print(f"  Ключ '{key}' уже существует!")
        print(f"     Текущее описание: {existing}")
        return
    
    v_value, hash_address = table.get_hash_info(key)
    success = table.insert(key, data)
    
    if success:
        print(f"  Термин '{key}' успешно добавлен!")
        print(f"     V={v_value}, h={hash_address}")
    else:
        print(f"  Ошибка: таблица заполнена или другой сбой!")


def search_term(table: HashTable) -> None:
    """Поиск термина по ключу."""
    print_header("ПОИСК ТЕРМИНА")
    
    key = input("  Введите ключевое слово для поиска: ").strip()
    if not key:
        print("   Ключ не может быть пустым!")
        return
    
    result = table.search(key)
    
    if result:
        v_value, hash_address = table.get_hash_info(key)
        print(f"  Найдено!")
        print(f"     Ключ: {key}")
        print(f"     Описание: {result}")
        print(f"     V={v_value}, h={hash_address}")
    else:
        print(f"  Термин '{key}' не найден в таблице.")


def update_term(table: HashTable) -> None:
    """Обновление описания термина."""
    print_header("ОБНОВЛЕНИЕ ТЕРМИНА")
    
    key = input("  Введите ключевое слово для обновления: ").strip()
    if not key:
        print("   Ключ не может быть пустым!")
        return
    
    # Проверяем, существует ли ключ
    existing = table.search(key)
    if not existing:
        print(f"  Термин '{key}' не найден в таблице.")
        return
    
    print(f"  Текущее описание: {existing}")
    new_data = input("  Введите новое описание: ").strip()
    
    if not new_data:
        print("   Описание не может быть пустым!")
        return
    
    success = table.update(key, new_data)
    
    if success:
        print(f"   Описание термина '{key}' успешно обновлено!")
    else:
        print(f"   Ошибка при обновлении!")


def delete_term(table: HashTable) -> None:
    """Удаление термина."""
    print_header("УДАЛЕНИЕ ТЕРМИНА")
    
    key = input("  Введите ключевое слово для удаления: ").strip()
    if not key:
        print("   Ключ не может быть пустым!")
        return
    
    # Проверяем, существует ли ключ
    existing = table.search(key)
    if not existing:
        print(f"   Термин '{key}' не найден в таблице.")
        return
    
    print(f"  Найден термин: {key} -> {existing}")
    confirm = input("  Вы уверены? (да/нет): ").strip().lower()
    
    if confirm in ['да', 'yes', 'д', 'y']:
        success = table.delete(key)
        if success:
            print(f" Термин '{key}' успешно удалён (мягкое удаление D=1).")
        else:
            print(f" Ошибка при удалении!")
    else:
        print("  Удаление отменено.")


def show_statistics(table: HashTable) -> None:
    """Показать статистику."""
    print_header("СТАТИСТИКА ХЕШ-ТАБЛИЦЫ")
    
    records = table.get_all_records()
    active_count = len(records)
    deleted_count = 0
    free_count = 0
    
    for idx in range(table._size):
        row = table.get_row_at_index(idx)
        if row:
            if row["d"]:
                deleted_count += 1
            elif not row["u"]:
                free_count += 1
    
    print(f"\n  Общая информация:")
    print(f"     Размер таблицы: {table._size}")
    print(f"     Активных записей: {active_count}")
    print(f"     Удалённых записей: {deleted_count}")
    print(f"     Свободных ячеек: {free_count}")
    print(f"     Коэффициент заполнения: {table.get_fill_factor():.4f}")
    
    # Оценка качества
    fill = table.get_fill_factor()
    if fill < 0.5:
        quality = "🟢 Отлично (много свободного места)"
    elif fill < 0.7:
        quality = "🟡 Хорошо (оптимальный уровень)"
    elif fill < 0.85:
        quality = "🟠 Нормально (увеличена вероятность коллизий)"
    else:
        quality = "🔴 Плохо (требуется расширение таблицы)"
    
    print(f"     Оценка: {quality}")


def show_collisions(table: HashTable) -> None:
    """Показать информацию о коллизиях (для отладки)."""
    print_header("ИНФОРМАЦИЯ О КОЛЛИЗИЯХ")
    
    records = table.get_all_records()
    
    if not records:
        print("  Таблица пуста.")
        return
    
    print("\n  Записи, у которых был коллизия (C=1):")
    print(f"  {'Ключ':<20} {'C':<3} {'Индекс':<8} {'h':<4} {'V':<6}")
    print("  " + "-" * 50)
    
    collision_count = 0
    for record in records:
        if record["c"]:
            key = record["id"]
            v, h = table.get_hash_info(key)
            # Найдём индекс, где лежит запись
            idx = None
            for i in range(table._size):
                row = table.get_row_at_index(i)
                if row and row["id"] == key:
                    idx = i
                    break
            print(f"  {key:<20} {record['c']:<3} {idx:<8} {h:<4} {v:<6}")
            collision_count += 1
    
    if collision_count == 0:
        print("  Нет записей с коллизиями.")
    else:
        print(f"\n  Всего записей с коллизиями: {collision_count}")
        print("  (C=1 означает, что при вставке этой записи произошла коллизия)")


def create_demo_table() -> HashTable:
    """Создание и заполнение хеш-таблицы демонстрационными данными."""
    table = HashTable(DEFAULT_TABLE_SIZE)
    
    demo_terms = [
        ("Амеба", "Простейшее одноклеточное животное"),
        ("Бактерия", "Одноклеточный микроорганизм без ядра"),
        ("Вирус", "Неклеточная форма жизни"),
        ("ДНК", "Дезоксирибонуклеиновая кислота"),
        ("Эукариот", "Клетка с оформленным ядром"),
        ("Прокариот", "Клетка без ядра"),
        ("Митохондрия", "Органоид клетки для выработки энергии"),
        ("Хлоропласт", "Органоид фотосинтеза у растений"),
        ("Фотосинтез", "Процесс образования органических веществ на свету"),
        ("Митоз", "Деление соматических клеток"),
        ("Мейоз", "Деление половых клеток"),
        ("Рибосома", "Органоид синтеза белка"),
        ("Цитоплазма", "Внутреннее содержимое клетки"),
        ("Ядро", "Органоид, содержащий генетический материал"),
    ]
    
    print("Создание демонстрационной таблицы...")
    for key, data in demo_terms:
        table.insert(key, data)
    
    print(f"Добавлено {len(demo_terms)} биологических терминов.")
    return table


def main() -> None:
    """Главная функция с меню."""
    print_header("ХЕШ-ТАБЛИЦА С КВАДРАТИЧНЫМ ПРОБИРОВАНИЕМ")
    print("  Вариант 4: разрешение коллизий - квадратичный поиск")
    print("  Тематика: Биология")
    print(f"  Размер таблицы: {DEFAULT_TABLE_SIZE} (≥20)")
    print("  Хеш-функция: V = код1×33 + код2, h = V mod H")
    
    # Создаём таблицу с демо-данными
    table = create_demo_table()
    
    print("\nДемонстрационная таблица готова!")
    print("   Теперь вы можете работать с ней через меню.")
    
    while True:
        print_menu()
        choice = input("\n  Ваш выбор: ").strip()
        
        if choice == '1':
            display_table(table)
        elif choice == '2':
            display_hash_info(table)
        elif choice == '3':
            add_term(table)
        elif choice == '4':
            search_term(table)
        elif choice == '5':
            update_term(table)
        elif choice == '6':
            delete_term(table)
        elif choice == '7':
            show_statistics(table)
        elif choice == '8':
            show_collisions(table)
        elif choice == '0':
            print_header("ДО СВИДАНИЯ!")
            break
        else:
            print("  Неверный выбор. Пожалуйста, введите число от 0 до 8.")
        
        input("\n  Нажмите Enter, чтобы продолжить...")
    print()


if __name__ == '__main__':
    main()