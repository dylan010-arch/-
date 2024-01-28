import tkinter as tk
from tkinter import ttk
import sqlite3

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Заметки")

        # Подключение к базе данных
        self.connection = sqlite3.connect("notes.db")
        self.create_table()

        # Интерфейс
        self.create_ui()

    def create_table(self):
        # Создание таблицы для заметок
        query = '''
            CREATE TABLE IF NOT EXISTS notes (
                № INTEGER PRIMARY KEY AUTOINCREMENT,
                Заголовок TEXT NOT NULL,
                Содержимое TEXT NOT NULL
            )
        '''
        self.connection.execute(query)
        self.connection.commit()

    def create_ui(self):
        # Основной контейнер для виджетов
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack()

        # Виджет для отображения списка заметок
        self.tree = ttk.Treeview(main_frame)
        self.tree["columns"] = ("№", "Заголовок", "Содержимое")
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("№", anchor=tk.W, width=40)
        self.tree.column("Заголовок", anchor=tk.W, width=150)
        self.tree.column("Содержимое", anchor=tk.W, width=300)

        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("№", text="№", anchor=tk.W)
        self.tree.heading("Заголовок", text="Заголовок", anchor=tk.W)
        self.tree.heading("Содержимое", text="Содержимое", anchor=tk.W)

        self.tree.grid(row=1, column=0, columnspan=3, pady=10)

        # Кнопки для управления заметками
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))

        add_btn = tk.Button(btn_frame, text="Добавить заметку", command=self.add_note)
        add_btn.grid(row=0, column=0, padx=10)

        edit_btn = tk.Button(btn_frame, text="Редактировать заметку", command=self.edit_note)
        edit_btn.grid(row=0, column=1, padx=10)

        delete_btn = tk.Button(btn_frame, text="Удалить заметку", command=self.delete_note)
        delete_btn.grid(row=0, column=2, padx=10)

        # Загрузка заметок из базы данных
        self.load_notes()

    def load_notes(self):
        # Очистка списка перед загрузкой
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Запрос к базе данных
        query = "SELECT * FROM notes"
        cursor = self.connection.execute(query)

        # Заполнение списка заметок
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def add_note(self):
        # Создание окна для добавления заметки
        add_window = tk.Toplevel(self.root)
        add_window.title("Добавить заметку")

        # Группировка элементов в LabelFrame
        label_frame = ttk.LabelFrame(add_window, text="Новая заметка", padding=(20, 10))
        label_frame.pack(padx=20, pady=20)

        # Создание элементов интерфейса для ввода данных
        title_label = tk.Label(label_frame, text="Заголовок:")
        title_label.grid(row=0, column=0, padx=10, pady=5)

        title_entry = tk.Entry(label_frame)
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        content_label = tk.Label(label_frame, text="Содержание:")
        content_label.grid(row=1, column=0, padx=10, pady=5)

        content_entry = tk.Entry(label_frame)
        content_entry.grid(row=1, column=1, padx=10, pady=5)

        # Кнопка для сохранения заметки
        save_btn = tk.Button(add_window, text="Сохранить", command=lambda: self.save_note(add_window, title_entry.get(), content_entry.get()))
        save_btn.pack(pady=10)

    def save_note(self, add_window, title, content):
        # Сохранение заметки в базе данных
        query = "INSERT INTO notes (Заголовок, Содержимое) VALUES (?, ?)"
        self.connection.execute(query, (title, content))
        self.connection.commit()

        # Обновление списка заметок
        self.load_notes()

        # Закрытие окна добавления заметки
        add_window.destroy()

    def edit_note(self):
        # Получение выбранной заметки
        selected_item = self.tree.selection()
        if not selected_item:
            return

        note_id = self.tree.item(selected_item, "values")[0]

        # Получение данных о заметке
        query = "SELECT * FROM notes WHERE № = ?"
        cursor = self.connection.execute(query, (note_id,))
        note_data = cursor.fetchone()

        # Создание окна для редактирования заметки
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактировать заметку")

        # Группировка элементов в LabelFrame
        label_frame = ttk.LabelFrame(edit_window, text="Редактировать заметку", padding=(20, 10))
        label_frame.pack(padx=20, pady=20)

        # Создание элементов интерфейса для редактирования данных
        title_label = tk.Label(label_frame, text="Заголовок:")
        title_label.grid(row=0, column=0, padx=10, pady=5)

        title_entry = tk.Entry(label_frame)
        title_entry.insert(0, note_data[1])  # Заполнение текущим заголовком
        title_entry.grid(row=0, column=1, padx=10, pady=5)

        content_label = tk.Label(label_frame, text="Содержание:")
        content_label.grid(row=1, column=0, padx=10, pady=5)

        content_entry = tk.Entry(label_frame)
        content_entry.insert(0, note_data[2])  # Заполнение текущим содержанием
        content_entry.grid(row=1, column=1, padx=10, pady=5)

        # Кнопка для сохранения изменений
        save_btn = tk.Button(edit_window, text="Сохранить", command=lambda: self.update_note(edit_window, note_id, title_entry.get(), content_entry.get()))
        save_btn.pack(pady=10)

    def update_note(self, edit_window, note_id, title, content):
        # Обновление данных о заметке в базе данных
        query = "UPDATE notes SET Заголовок = ?, Содержимое = ? WHERE №= ?"
        self.connection.execute(query, (title, content, note_id))
        self.connection.commit()

        # Обновление списка заметок
        self.load_notes()

        # Закрытие окна редактирования заметки
        edit_window.destroy()

    def delete_note(self):
        # Получение выбранной заметки
        selected_item = self.tree.selection()
        if not selected_item:
            return

        note_id = self.tree.item(selected_item, "values")[0]

        # Удаление заметки из базы данных
        query = "DELETE FROM notes WHERE № = ?"
        self.connection.execute(query, (note_id,))
        self.connection.commit()

        # Обновление списка заметок
        self.load_notes()

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
