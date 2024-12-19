import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import pandas as pd
import openpyxl
from matplotlib import pyplot as plt
class NoVaOrderManagementApp(tk.Tk):
    """
        Класс для управления заказами в приложении NoVa. Включает авторизацию,
        работу с товарами, заказами, отзывами и отчетами, а также функции настройки
        """
    def show_role_selection(self):
        """Отображает окно выбора роли (администратор или пользователь)."""
        self.clear_screen()
        role_selection_frame = tk.Frame(self, bg=self.bg_color, padx=20, pady=20)
        role_selection_frame.pack(expand=True, fill="both")

        welcome_label = tk.Label(role_selection_frame, text="Добро пожаловать, в Nova!", font=("Arial", 24, "bold"),
                                 bg=self.bg_color, fg="#336699")
        welcome_label.pack(pady=20)

        role_label = tk.Label(role_selection_frame, text="Выберите роль:", font=("Arial", 16, "bold"), bg=self.bg_color)
        role_label.pack(pady=20)

        def select_admin():
            self.show_login_screen()

        def select_user():
            import user_window
            user_window.UserWindow(self).mainloop()

        def exit_app():
            self.quit()
        admin_button = tk.Button(role_selection_frame, text="Администратор", command=select_admin,
                                 font=self.default_font, width=20)
        admin_button.pack(pady=10)

        user_button = tk.Button(role_selection_frame, text="Пользователь", command=select_user, font=self.default_font,
                                width=20)
        user_button.pack(pady=10)


    def __init__(self):
        """Инициализация главного окна приложения."""
        super().__init__()
        self.title("NoVa Order Management System")
        self.geometry("1000x600")  # Начальный размер
        self.bg_color = "#DCE4E4"
        self.configure(bg=self.bg_color)
        self.default_font = ("Arial", 12)
        self.db_path = 'nova.db'
        if self.check_database_exists():
            if self.connect_to_database():
                self.show_role_selection()
            else:
                messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных.")
                self.quit()
        else:
            messagebox.showerror("Ошибка", f"Файл базы данных '{self.db_path}' не найден.")
            self.quit()
    def check_database_exists(self):
        """
        Проверяет существование файла базы данных
        """
        return os.path.exists(self.db_path)

    def connect_to_database(self):
        """
        Подключается к базе данных SQLite и создает курсор для взаимодействия с ней
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print("Ошибка подключения к базе данных:", e)
            return False

    def show_login_screen(self):
        """Отображает экран авторизации."""
        self.clear_screen()
        login_frame = tk.Frame(self, bg=self.bg_color, padx=20, pady=20)
        login_frame.pack(pady=50)

        tk.Label(login_frame, text="Авторизация администратора", font=("Arial", 16, "bold"), bg=self.bg_color).pack(
            pady=20)
        tk.Label(login_frame, text="Логин:", bg=self.bg_color).pack(anchor="w")
        self.login_entry = tk.Entry(login_frame, font=self.default_font)
        self.login_entry.pack(fill="x", pady=5)

        tk.Label(login_frame, text="Пароль:", bg=self.bg_color).pack(anchor="w")
        self.password_entry = tk.Entry(login_frame, show="*", font=self.default_font)
        self.password_entry.pack(fill="x", pady=5)

        tk.Button(login_frame, text="Войти", command=self.authenticate_admin, font=self.default_font).pack(pady=10,
                                                                                                           fill="x")
        tk.Button(login_frame, text="Забыли пароль?", command=self.reset_password, font=self.default_font).pack(pady=5,
                                                                                                                fill="x")
        tk.Button(login_frame, text="Регистрация", command=self.register_admin, font=self.default_font).pack(pady=5,
                                                                                                             fill="x")

        back_button = tk.Button(login_frame, text="Назад", command=self.show_role_selection, font=self.default_font)
        back_button.pack(pady=10, fill="x")

    def authenticate_admin(self):
        """
        Аутентифицирует администратора, проверяя логин и пароль в базе данных.
        Если проверка успешна, отображает главный интерфейс.
        """
        login = self.login_entry.get()
        password = self.password_entry.get()
        self.cursor.execute("SELECT * FROM users WHERE user_login = ? AND user_password = ? AND role = 0",
                            (login, password))
        if self.cursor.fetchone():
            self.create_main_interface()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def register_admin(self):
        """
        Отображает окно регистрации администратора, где можно создать нового администратора.
        """
        reg_win = tk.Toplevel(self)
        reg_win.title("Регистрация администратора")
        reg_win.configure(bg=self.bg_color)

        reg_frame = tk.Frame(reg_win, padx=20, pady=20, bg=self.bg_color)
        reg_frame.pack(pady=10)

        tk.Label(reg_frame, text="Имя пользователя:", bg=self.bg_color, font=self.default_font).pack(anchor="w")
        username_entry = tk.Entry(reg_frame, font=self.default_font)
        username_entry.pack(fill="x", pady=5)

        tk.Label(reg_frame, text="Пароль:", bg=self.bg_color, font=self.default_font).pack(anchor="w")
        password_entry = tk.Entry(reg_frame, show="*", font=self.default_font)
        password_entry.pack(fill="x", pady=5)

        def save_admin():
            username = username_entry.get()
            password = password_entry.get()
            try:
                self.cursor.execute("INSERT INTO users (user_login, user_password, role) VALUES (?, ?, ?)",
                                    (username, password, 0))  # Роль 0 для администратора
                self.conn.commit()
                messagebox.showinfo("Успех", "Администратор зарегистрирован.")
                reg_win.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Не удалось создать администратора: {e}")

        tk.Button(reg_win, text="Сохранить", command=save_admin).pack(pady=10)

    def reset_password(self):
        """
        Отображает окно для восстановления пароля администратора. При вводе логина
        и успешной проверке восстанавливает пароль до стандартного.
        """
        reset_win = tk.Toplevel(self)
        reset_win.title("Восстановление пароля")
        reset_win.configure(bg=self.bg_color)
        tk.Label(reset_win, text="Введите логин для восстановления:", bg=self.bg_color, font=self.default_font).pack()
        username_entry = tk.Entry(reset_win, font=self.default_font)
        username_entry.pack()

        def reset():
            username = username_entry.get()
            self.cursor.execute("SELECT * FROM users WHERE user_login = ? AND role = 0", (username,))
            if self.cursor.fetchone():
                new_password = "new_password123"
                self.cursor.execute("UPDATE users SET user_password = ? WHERE user_login = ?", (new_password, username))
                self.conn.commit()
                messagebox.showinfo("Восстановление", f"Ваш новый пароль: {new_password}")
                reset_win.destroy()
            else:
                messagebox.showerror("Ошибка", "Пользователь не найден")

        tk.Button(reset_win, text="Сбросить пароль", command=reset).pack(pady=10)
    def create_main_interface(self):
        """
        Создает главный интерфейс приложения.
        """
        self.clear_screen()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        self.create_products_tab()
        self.create_orders_tab()
        self.create_reviews_tab()
        self.create_analytics_tab()
        self.create_settings_tab()

    def create_products_tab(self):
        """
        Создает вкладку для управления товарами с таблицей и кнопками для добавления,
        редактирования и удаления товаров
        """

        products_tab = ttk.Frame(self.notebook)
        products_tab.configure(style="Custom.TFrame")
        self.notebook.add(products_tab, text="Товары")

        style = ttk.Style()
        style.configure("Custom.Treeview", background=self.bg_color, fieldbackground=self.bg_color,
                        font=self.default_font)
        style.configure("Custom.Treeview.Heading", font=("Arial", 10, "bold"))

        self.products_table = ttk.Treeview(
            products_tab, columns=("ID", "Name", "Price", "Category", "Stock"), show="headings", style="Custom.Treeview"
        )
        self.products_table.heading("ID", text="ID")
        self.products_table.heading("Name", text="Название")
        self.products_table.heading("Price", text="Цена")
        self.products_table.heading("Category", text="Категория")
        self.products_table.heading("Stock", text="Наличие")
        self.products_table.pack(fill="both", expand=True)

        button_frame = tk.Frame(products_tab, bg=self.bg_color)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame, text="Добавить товар", command=self.add_product, font=self.default_font, bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame, text="Редактировать товар", command=self.edit_product, font=self.default_font,
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame, text="Поиск", command=self.search_product, font=self.default_font, bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame, text="Удалить товар", command=self.delete_product, font=self.default_font, bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)

        self.load_products()

    def load_products(self):
        """
        Загружает данные о продуктах из базы данных и отображает их в таблице на вкладке "Товары"
        """
        for item in self.products_table.get_children():
            self.products_table.delete(item)

        self.cursor.execute("""
            SELECT p.id, p.name, p.price, c.name AS category, p.stock 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
        """)

        for product in self.cursor.fetchall():
            self.products_table.insert("", "end", values=product)

    def add_product(self):
        """
        Открывает окно для добавления нового товара с полями для ввода названия, цены,
        категории и количества на складе. После сохранения данные добавляются в базу
        """
        add_win = tk.Toplevel(self)
        add_win.title("Добавить товар")
        add_win.configure(bg=self.bg_color)

        entries = self.create_product_form(add_win)

        def save_product():
            try:
                # Получаем ID категории по её названию
                self.cursor.execute("SELECT id FROM categories WHERE name = ?", (entries["category"].get(),))
                category_id = self.cursor.fetchone()
                if category_id is None:
                    messagebox.showerror("Ошибка", "Категория не найдена.")
                    return

                self.cursor.execute("INSERT INTO products (name, price, category_id, stock) VALUES (?, ?, ?, ?)",
                                    (entries["name"].get(), float(entries["price"].get()), category_id[0],
                                     int(entries["stock"].get())))
                self.conn.commit()
                add_win.destroy()
                self.load_products()
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректные данные.")

        tk.Button(add_win, text="Сохранить", command=save_product, font=self.default_font, bg=self.bg_color).pack(
            pady=10)

    def edit_product(self):
        """
        Открывает окно для редактирования данных выбранного товара
        Изменения сохраняются в базе данных после нажатия на кнопку "Обновить"
        """
        selected = self.products_table.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите товар для редактирования.")
            return

        item = self.products_table.item(selected)
        product_id, name, price, category, stock = item["values"]
        edit_win = tk.Toplevel(self)
        edit_win.title("Редактировать товар")
        edit_win.configure(bg=self.bg_color)

        entries = self.create_product_form(edit_win, name, price, category, stock)

        def update_product():
            try:
                # Получаем ID категории по её названию
                self.cursor.execute("SELECT id FROM categories WHERE name = ?", (entries["category"].get(),))
                category_id = self.cursor.fetchone()
                if category_id is None:
                    messagebox.showerror("Ошибка", "Категория не найдена.")
                    return

                self.cursor.execute("UPDATE products SET name=?, price=?, category_id=?, stock=? WHERE id=?",
                                    (entries["name"].get(), float(entries["price"].get()), category_id[0],
                                     int(entries["stock"].get()), product_id))
                self.conn.commit()
                edit_win.destroy()
                self.load_products()
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректные данные.")

        tk.Button(edit_win, text="Обновить", command=update_product, font=self.default_font, bg=self.bg_color).pack(
            pady=10)

    def search_product(self):
        """
        Открывает окно для поиска товара по названию.
     После ввода названия и подтверждения отображает результат в таблице.
        """
        search_win = tk.Toplevel(self)
        search_win.title("Поиск товара")
        search_win.configure(bg=self.bg_color)

        tk.Label(search_win, text="Введите название товара:", font=self.default_font, bg=self.bg_color).pack(pady=10)
        search_entry = tk.Entry(search_win, font=self.default_font, bg=self.bg_color)
        search_entry.pack(fill="x", padx=10, pady=5)

        def perform_search():
            search_term = search_entry.get()
            for item in self.products_table.get_children():
                self.products_table.delete(item)
            query = """
                SELECT p.id, p.name, p.price, c.name AS category, p.stock 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id 
                WHERE p.name LIKE ?
            """
            self.cursor.execute(query, ('%' + search_term + '%',))
            results = self.cursor.fetchall()
            if results:
                for product in results:
                    self.products_table.insert("", "end", values=product)
            else:
                messagebox.showinfo("Результаты поиска", "Товары с таким названием не найдены.")
            search_win.destroy()

        tk.Button(search_win, text="Искать", command=perform_search, font=self.default_font, bg=self.bg_color).pack(
            pady=10)

    def delete_product(self):
        selected = self.products_table.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите товар для удаления.")
            return
        product_id = self.products_table.item(selected)["values"][0]
        self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        self.conn.commit()
        self.load_products()

    def create_product_form(self, window, name="", price="", category="", stock=""):
        """
        Создает форму для ввода данных о товаре
        """
        tk.Label(window, text="Название", font=self.default_font, bg=self.bg_color).pack(pady=5)
        name_entry = tk.Entry(window, font=self.default_font, bg=self.bg_color)
        name_entry.insert(0, name)
        name_entry.pack(fill="x", pady=5)

        tk.Label(window, text="Цена", font=self.default_font, bg=self.bg_color).pack(pady=5)
        price_entry = tk.Entry(window, font=self.default_font, bg=self.bg_color)
        price_entry.insert(0, price)
        price_entry.pack(fill="x", pady=5)

        tk.Label(window, text="Категория", font=self.default_font, bg=self.bg_color).pack(pady=5)
        category_entry = tk.Entry(window, font=self.default_font, bg=self.bg_color)
        category_entry.insert(0, category)
        category_entry.pack(fill="x", pady=5)

        tk.Label(window, text="Наличие", font=self.default_font, bg=self.bg_color).pack(pady=5)
        stock_entry = tk.Entry(window, font=self.default_font, bg=self.bg_color)
        stock_entry.insert(0, stock)
        stock_entry.pack(fill="x", pady=5)

        return {"name": name_entry, "price": price_entry, "category": category_entry, "stock": stock_entry}

    def create_orders_tab(self):
        """
        Создает вкладку "Заказы" с таблицей, отображающей заказы, и кнопками для фильтрации
        и изменения статуса заказов
        """
        # Создание вкладки и установка фона
        orders_tab = ttk.Frame(self.notebook)
        orders_tab.configure(style="Custom.TFrame")
        self.notebook.add(orders_tab, text="Заказы")

        # Настройка стиля для таблицы
        style = ttk.Style()
        style.configure("Custom.Treeview", background=self.bg_color, fieldbackground=self.bg_color,
                        font=self.default_font)
        style.configure("Custom.Treeview.Heading", font=("Arial", 10, "bold"))

        # Создание таблицы с использованием пользовательского стиля
        self.orders_table = ttk.Treeview(
            orders_tab, columns=("OrderID", "Customer", "Address", "Date", "Status"), show="headings",
            style="Custom.Treeview"
        )
        self.orders_table.heading("OrderID", text="Номер заказа")
        self.orders_table.heading("Customer", text="Покупатель")
        self.orders_table.heading("Address", text="Адрес")
        self.orders_table.heading("Date", text="Дата")
        self.orders_table.heading("Status", text="Статус")
        self.orders_table.pack(fill="both", expand=True)

        # Панель с фильтром
        filter_frame = tk.Frame(orders_tab, bg=self.bg_color)
        filter_frame.pack(pady=10, fill="x")

        # Элементы фильтра и кнопки управления
        tk.Label(filter_frame, text="Фильтр по статусу:", font=self.default_font, bg=self.bg_color).pack(side=tk.LEFT,
                                                                                                         padx=5)
        self.status_filter = ttk.Combobox(
            filter_frame, values=["Все", "Новый", "В обработке", "Выполнен", "Отменен"], font=self.default_font
        )
        self.status_filter.set("Все")
        self.status_filter.pack(side=tk.LEFT, padx=5)

        tk.Button(
            filter_frame, text="Применить фильтр", command=self.apply_order_filter, font=self.default_font,
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            filter_frame, text="Просмотреть детали", command=self.view_order_details, font=self.default_font,
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            filter_frame, text="Изменить статус", command=self.change_order_status, font=self.default_font,
            bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)

        self.load_orders()

    def load_orders(self, status="Все"):
        for item in self.orders_table.get_children():
            self.orders_table.delete(item)

        # Обновленный запрос для получения данных о заказах с информацией о пользователе
        query = """
            SELECT o.id, 
                   u.name || ' ' || u.lastname AS customer_name, 
                   u.address AS customer_address,
                   o.order_date, 
                   o.status 
            FROM orders o
            JOIN users u ON o.user_id = u.id
        """
        if status != "Все":
            query += " WHERE o.status = ?"
            self.cursor.execute(query, (status,))
        else:
            self.cursor.execute(query)

        for order in self.cursor.fetchall():
            self.orders_table.insert("", "end", values=order)
    def apply_order_filter(self):
        """
        Применяет фильтр к заказам по выбранному статусу
        """
        selected_status = self.status_filter.get()
        self.load_orders(selected_status)

    def view_order_details(self):
        """
        Открывает окно с деталями выбранного заказа, отображая список товаров в заказе
        """
        selected = self.orders_table.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите заказ для просмотра.")
            return
        order_id = self.orders_table.item(selected)["values"][0]

        details_win = tk.Toplevel(self)
        details_win.title("Детали заказа")
        details_win.configure(bg=self.bg_color)

        tk.Label(details_win, text=f"Детали заказа №{order_id}", font=("Arial", 14, "bold"), bg=self.bg_color).pack(
            pady=10)

        self.cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
        order_items = self.cursor.fetchall()

        if order_items:
            for item in order_items:
                tk.Label(details_win, text=f"Товар ID: {item[2]}, Количество: {item[3]}", font=self.default_font,
                         bg=self.bg_color).pack(anchor="w", padx=10, pady=5)
        else:
            tk.Label(details_win, text="Нет данных о товарах в заказе.", font=self.default_font, bg=self.bg_color).pack(
                pady=10)

    def change_order_status(self):
        """
        Открывает окно для изменения статуса выбранного заказа и обновляет его в базе данных
        """
        selected = self.orders_table.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите заказ для изменения статуса.")
            return

        order_id = self.orders_table.item(selected)["values"][0]
        status_win = tk.Toplevel(self)
        status_win.title("Изменить статус заказа")
        status_win.configure(bg=self.bg_color)  # Установка цвета фона окна

        tk.Label(status_win, text=f"Изменение статуса заказа №{order_id}", font=("Arial", 14, "bold"),
                 bg=self.bg_color).pack(pady=10)
        tk.Label(status_win, text="Новый статус:", font=self.default_font, bg=self.bg_color).pack(pady=5)

        new_status = ttk.Combobox(status_win, values=["Новый", "В обработке", "Выполнен", "Отменен"],
                                  font=self.default_font)
        new_status.pack(pady=5)

        def update_status():
            if not new_status.get():
                messagebox.showerror("Ошибка", "Выберите статус для обновления.")
                return
            self.cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status.get(), order_id))
            self.conn.commit()
            status_win.destroy()
            self.load_orders()

        tk.Button(status_win, text="Обновить статус", command=update_status, font=self.default_font,
                  bg=self.bg_color).pack(pady=10)

    def create_reviews_tab(self):
        """
        Создает вкладку "Отзывы" с таблицей, отображающей отзывы, и кнопками для обновления
        и удаления отзывов
        """
        # Создание вкладки и установка фона
        reviews_tab = ttk.Frame(self.notebook)
        reviews_tab.configure(style="Custom.TFrame")
        self.notebook.add(reviews_tab, text="Отзывы")

        # Настройка стиля для таблицы
        style = ttk.Style()
        style.configure("Custom.Treeview", background=self.bg_color, fieldbackground=self.bg_color,
                        font=self.default_font)
        style.configure("Custom.Treeview.Heading", font=("Arial", 10, "bold"))

        # Создание таблицы с использованием пользовательского стиля
        self.reviews_table = ttk.Treeview(
            reviews_tab, columns=("ID", "Product", "Rating", "Comment"), show="headings", style="Custom.Treeview"
        )
        self.reviews_table.heading("ID", text="ID")
        self.reviews_table.heading("Product", text="Товар")
        self.reviews_table.heading("Rating", text="Оценка")
        self.reviews_table.heading("Comment", text="Комментарий")
        self.reviews_table.pack(fill="both", expand=True)

        # Панель с кнопками управления
        button_frame = tk.Frame(reviews_tab, bg=self.bg_color)
        button_frame.pack(pady=10, fill="x")

        # Кнопки управления отзывами
        tk.Button(
            button_frame, text="Обновить отзывы", command=self.load_reviews, font=self.default_font, bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            button_frame, text="Удалить отзыв", command=self.delete_review, font=self.default_font, bg=self.bg_color
        ).pack(side=tk.LEFT, padx=5)

        self.load_reviews()

    def load_reviews(self):
        """
        Загружает все отзывы из базы данных и отображает их в таблице отзывов на вкладке "Отзывы"
        """
        for item in self.reviews_table.get_children():
            self.reviews_table.delete(item)

        query = """
            SELECT r.id, p.name AS product_name, r.rating, r.comment 
            FROM reviews r
            JOIN products p ON r.product_id = p.id
        """
        self.cursor.execute(query)
        for review in self.cursor.fetchall():
            self.reviews_table.insert("", "end", values=review)

    def delete_review(self):
        """
        Удаляет выбранный отзыв из базы данных
        """
        selected = self.reviews_table.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите отзыв для удаления.")
            return

        review_id = self.reviews_table.item(selected)["values"][0]  # Теперь это ID отзыва

        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить выбранный отзыв?"
        )

        if confirm:
            self.cursor.execute("DELETE FROM reviews WHERE id=?", (review_id,))
            self.conn.commit()
            self.load_reviews()

    def create_analytics_tab(self):
        """Создает вкладку "Аналитика и Отчеты" с улучшенным оформлением."""
        analytics_tab = ttk.Frame(self.notebook, style="Custom.TFrame")  # Используем стиль
        self.notebook.add(analytics_tab, text="Аналитика и Отчеты")

        # Создаем стиль для рамки с данными
        style = ttk.Style()
        style.configure("Custom.TLabelframe", background=self.bg_color, borderwidth=2, relief="groove",
                        font=("Arial", 12, "bold"))

        # Общая выручка
        revenue_frame = ttk.LabelFrame(analytics_tab, text="Общая выручка", style="Custom.TLabelframe")
        revenue_frame.pack(pady=10, padx=10, fill="x")
        total_revenue = self.cursor.execute(
            "SELECT SUM(products.price * order_items.quantity) "
            "FROM order_items JOIN products ON products.id = order_items.product_id"
        ).fetchone()[0] or 0
        revenue_label = ttk.Label(revenue_frame, text=f"{total_revenue:.2f}", font=("Arial", 16, "bold"),
                                  foreground="#336699")  # Зеленый цвет
        revenue_label.pack(pady=10)

        # Популярные товары
        popular_products_frame = ttk.LabelFrame(analytics_tab, text="Популярные товары", style="Custom.TLabelframe")
        popular_products_frame.pack(pady=10, padx=10, fill="x")
        popular_products = self.cursor.execute(
            "SELECT products.name, SUM(order_items.quantity) AS total_sold "
            "FROM order_items "
            "JOIN products ON products.id = order_items.product_id "
            "GROUP BY products.name "
            "ORDER BY total_sold DESC LIMIT 5"
        ).fetchall()
        for product_name, total_sold in popular_products:
            product_label = ttk.Label(popular_products_frame, text=f"{product_name}: {total_sold} продано",
                                      font=self.default_font)
            product_label.pack(anchor="w", padx=10, pady=5)

        # Кнопки для графиков
        tk.Label(analytics_tab, text="Графики и диаграммы", font=("Arial", 12, "bold"), bg=self.bg_color).pack(pady=10)
        tk.Button(analytics_tab, text="Показать график продаж по датам", command=self.plot_sales_graph,
                  font=self.default_font, bg=self.bg_color).pack(pady=5)
        tk.Button(analytics_tab, text="Показать диаграмму популярных товаров", command=self.plot_popular_products,
                  font=self.default_font, bg=self.bg_color).pack(pady=5)

        # Кнопка для скачивания отчета в Excel
        tk.Button(analytics_tab, text="Скачать отчет в Excel", command=self.download_excel_report,
                  font=self.default_font, bg=self.bg_color).pack(pady=5)

    def download_excel_report(self):
        """Скачивает отчет в формате Excel."""
        # Получаем данные для отчета
        query = """
            SELECT p.name AS product_name, SUM(oi.quantity) AS total_sold
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            GROUP BY p.name
        """
        data = self.cursor.execute(query).fetchall()

        # Создаем DataFrame
        df = pd.DataFrame(data, columns=["Product", "Total Sold"])

        # Открываем диалог для выбора места сохранения файла
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            try:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Успех", "Отчет успешно сохранен в формате Excel.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить отчет: {e}")

    def plot_sales_graph(self):

        """
        Отображает график продаж по датам на основе данных из базы
        """
        sales_data = self.cursor.execute(
            "SELECT strftime('%Y-%m-%d', order_date) AS date, SUM(products.price * order_items.quantity) AS total "
            "FROM orders "
            "JOIN order_items ON orders.id = order_items.order_id "
            "JOIN products ON products.id = order_items.product_id "
            "GROUP BY date ORDER BY date"
        ).fetchall()

        if sales_data:
            dates, totals = zip(*sales_data)
            plt.figure(figsize=(10, 5))
            plt.plot(dates, totals, marker='o')
            plt.title("Продажи по датам", fontsize=14)
            plt.xlabel("Дата", fontsize=12)
            plt.ylabel("Сумма продаж", fontsize=12)
            plt.xticks(rotation=45, fontsize=10)
            plt.yticks(fontsize=10)
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            messagebox.showinfo("Информация", "Нет данных для отображения графика.")

    def plot_popular_products(self):
        """
        Отображает диаграмму популярных товаров на основе данных из базы
        """
        popular_products = self.cursor.execute(
            "SELECT products.name, SUM(order_items.quantity) AS total_sold "
            "FROM order_items "
            "JOIN products ON products.id = order_items.product_id "
            "GROUP BY products.name "
            "ORDER BY total_sold DESC LIMIT 5"
        ).fetchall()

        if popular_products:
            product_names, total_sold = zip(*popular_products)
            plt.figure(figsize=(10, 5))
            plt.bar(product_names, total_sold, color='skyblue', edgecolor='black')
            plt.title("Популярные товары", fontsize=14)
            plt.xlabel("Товары", fontsize=12)
            plt.ylabel("Количество продаж", fontsize=12)
            plt.xticks(rotation=45, fontsize=10)
            plt.yticks(fontsize=10)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.show()
        else:
            messagebox.showinfo("Информация", "Нет данных для отображения диаграммы.")

    def create_settings_tab(self):
        """
        Создает вкладку "Настройки", где можно изменить настройки учетной записи и базы данных
        """
        settings_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(settings_tab, text="Настройки")

        tk.Label(
            settings_tab, text="Настройки учетной записи", font=("Arial", 14, "bold"), bg=self.bg_color
        ).pack(pady=10)
        tk.Button(
            settings_tab, text="Изменить пароль", command=self.change_password, font=self.default_font, bg=self.bg_color
        ).pack(pady=5)

        tk.Label(
            settings_tab, text="Настройки базы данных", font=("Arial", 14, "bold"), bg=self.bg_color
        ).pack(pady=10)
        tk.Button(
            settings_tab, text="Резервное копирование", command=self.backup_database, font=self.default_font,
            bg=self.bg_color
        ).pack(pady=5)

        back_button = tk.Button(settings_tab, text="Выход", command=self.show_role_selection, font=self.default_font,bg=self.bg_color)
        back_button.pack(pady=5)
    def change_password(self):
        password_win = tk.Toplevel(self)
        password_win.title("Изменить пароль")
        password_win.configure(bg=self.bg_color)  # Установка цвета фона окна

        tk.Label(password_win, text="Введите новый пароль:", font=self.default_font, bg=self.bg_color).pack(pady=10)
        new_password_entry = tk.Entry(password_win, show="*", font=self.default_font, bg=self.bg_color)
        new_password_entry.pack(fill="x", padx=10, pady=5)

        def update_password():
            new_password = new_password_entry.get()
            if not new_password:
                messagebox.showerror("Ошибка", "Пароль не может быть пустым.")
                return
            self.cursor.execute("UPDATE admin_users SET password = ? WHERE username = ?",
                                (new_password, self.login_entry.get()))
            self.conn.commit()
            password_win.destroy()
            messagebox.showinfo("Пароль изменен", "Пароль успешно обновлен")

        tk.Button(password_win, text="Сохранить", command=update_password, font=self.default_font,
                  bg=self.bg_color).pack(pady=10)
    def backup_database(self):
        """
        Создает резервную копию базы данных
        """
        filename = filedialog.asksaveasfilename(
            title="Сохранить резервную копию",
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db")],
            initialfile="backup_nova.db"
        )
        if filename:
            try:
                with open(self.db_path, 'rb') as db_file:
                    with open(filename, 'wb') as backup_file:
                        backup_file.write(db_file.read())
                messagebox.showinfo("Резервное копирование", "Резервная копия базы данных успешно создана.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать резервную копию: {e}")
        else:
            messagebox.showinfo("Отмена", "Резервное копирование отменено.")

    def clear_screen(self):
        """
        Очищает все виджеты с текущего экрана приложения.
        """
        for widget in self.winfo_children():
            widget.destroy()

    def __del__(self):
        """
        Закрывает соединение с базой данных при завершении работы приложения.
        """
        if hasattr(self, 'conn'):
            self.conn.close()


if __name__ == "__main__":
    app = NoVaOrderManagementApp()
    app.mainloop()