import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class UserWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("NoVa - Пользователь")
        self.master = master
        self.db_path = 'nova.db'
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.user_id = None
        self.selected_products = []
        self.default_font = ("Arial", 12)
        self.bg_color = "#DCE4E4"
        self.create_login_screen()

    def create_login_screen(self):
        """Создает экран авторизации для пользователя."""
        self.clear_screen()
        self.configure(bg=self.bg_color)

        login_frame = tk.Frame(self, bg=self.bg_color, padx=20, pady=20)
        login_frame.pack(pady=50)
        tk.Label(login_frame, text="Авторизация", font=("Arial", 16, "bold"), bg=self.bg_color).pack(pady=20)
        tk.Label(login_frame, text="Логин:", bg=self.bg_color, font=self.default_font).pack(anchor="w")
        self.login_entry = tk.Entry(login_frame, font=self.default_font)
        self.login_entry.pack(fill="x", pady=5)
        tk.Label(login_frame, text="Пароль:", bg=self.bg_color, font=self.default_font).pack(anchor="w")
        self.password_entry = tk.Entry(login_frame, show="*", font=self.default_font)
        self.password_entry.pack(fill="x", pady=5)
        tk.Button(login_frame, text="Войти", command=self.authenticate_user, font=self.default_font).pack(pady=10,
                                                                                                          fill="x")
        tk.Button(login_frame, text="Регистрация", command=self.register_user, font=self.default_font).pack(pady=5,
                                                                                                            fill="x")

        def exit_app():
            self.quit()

        exit_button = tk.Button(login_frame, text="Выход", command=exit_app, font=self.default_font, width=20)
        exit_button.pack(pady=10)

    def authenticate_user(self):
        """Аутентифицирует пользователя, проверяя логин и пароль в базе данных."""
        login = self.login_entry.get()
        password = self.password_entry.get()
        self.cursor.execute("SELECT id, user_login, user_password FROM users WHERE user_login = ? AND role = 1",
                            (login,))
        user = self.cursor.fetchone()
        if user and user[2] == password:
            self.user_id = user[0]
            self.create_main_interface()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def register_user(self):
        """Отображает окно регистрации пользователя, где можно создать нового пользователя."""
        reg_win = tk.Toplevel(self)
        reg_win.title("Регистрация")
        reg_win.configure(bg=self.bg_color)
        reg_frame = tk.Frame(reg_win, padx=20, pady=20, bg=self.bg_color)
        reg_frame.pack(pady=10)

        def save_user():
            login = login_entry.get()
            password = password_entry.get()
            try:
                self.cursor.execute("INSERT INTO users (user_login, user_password, role) VALUES (?, ?, ?)",
                                    (login, password, 1))  # Роль 1 для обычного пользователя
                self.conn.commit()
                messagebox.showinfo("Успех", "Пользователь зарегистрирован.")
                reg_win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка регистрации: {e}")

        tk.Label(reg_frame, text="Логин:", bg=self.bg_color, font=self.default_font).pack(anchor="w")
        login_entry = tk.Entry(reg_frame, font=self.default_font)
        login_entry.pack(fill="x", pady=5)
        tk.Label(reg_frame, text="Пароль:", bg=self.bg_color, font=self.default_font).pack(anchor="w")
        password_entry = tk.Entry(reg_frame, show="*", font=self.default_font)
        password_entry.pack(fill="x", pady=5)
        tk.Button(reg_frame, text="Зарегистрироваться", command=save_user, font=self.default_font).pack(pady=10)
    def create_main_interface(self):
        self.clear_screen()
        self.configure(bg=self.bg_color)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        self.create_products_tab()
        self.create_reviews_tab()

        # Кнопка выхода
        exit_button = tk.Button(self, text="Выход", command=self.exit_application, font=self.default_font, bg=self.bg_color)
        exit_button.pack(pady=10)

    def create_products_tab(self):
        products_tab = ttk.Frame(self.notebook)
        self.notebook.add(products_tab, text="Товары")
        style = ttk.Style()
        style.configure("Custom.Treeview", background=self.bg_color, fieldbackground=self.bg_color, font=self.default_font)
        style.configure("Custom.Treeview.Heading", font=("Arial", 10, "bold"))
        self.products_tree = ttk.Treeview(products_tab, columns=("Name", "Price", "Description"), show="headings", style="Custom.Treeview")
        self.products_tree.heading("Name", text="Название")
        self.products_tree.heading("Price", text="Цена")
        self.products_tree.heading("Description", text="Описание")
        self.products_tree.pack(fill="both", expand=True)
        self.load_products()
        tk.Button(products_tab, text="Сформировать заказ", command=self.create_order, font=self.default_font).pack(pady=10)

    def load_products(self):
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        self.cursor.execute("SELECT name, price, description FROM products")
        for product in self.cursor.fetchall():
            self.products_tree.insert("", "end", values=product)

    def create_order(self):
        if self.user_id is None:
            messagebox.showerror("Ошибка", "Вы не авторизованы.")
            return
        selected_products = self.products_tree.selection()
        if not selected_products:
            messagebox.showerror("Ошибка", "Выберите товары для заказа.")
            return
        order_window = tk.Toplevel(self)
        order_window.title("Оформление заказа")

        name_label = tk.Label(order_window, text="Имя:")
        name_label.grid(row=0, column=0, sticky="w")
        name_entry = tk.Entry(order_window)
        name_entry.grid(row=0, column=1)

        surname_label = tk.Label(order_window, text="Фамилия:")
        surname_label.grid(row=1, column=0, sticky="w")
        surname_entry = tk.Entry(order_window)
        surname_entry.grid(row=1, column=1)

        address_label = tk.Label(order_window, text="Адрес:")
        address_label.grid(row=2, column=0, sticky="w")
        address_entry = tk.Entry(order_window)
        address_entry.grid(row=2, column=1)

        items_frame = tk.Frame(order_window)
        items_frame.grid(row=3, column=0, columnspan=2, pady=10)
        item_labels = []
        quantity_entries = {}

        try:
            # Словарь для хранения количества каждого товара
            product_quantities = {}

            for product_id in selected_products:
                product_info = self.products_tree.item(product_id)
                product_name = product_info['values'][0]

                # Увеличиваем количество для данного товара
                if product_name in product_quantities:
                    product_quantities[product_name] += 1
                else:
                    product_quantities[product_name] = 1

            # Создаем интерфейс для каждого уникального товара
            for product_name, quantity in product_quantities.items():
                label = tk.Label(items_frame, text=f"{product_name}:")
                label.pack(anchor="w")
                entry = tk.Entry(items_frame)
                entry.insert(0, quantity)  # Устанавливаем начальное количество
                entry.pack(anchor="w")
                item_labels.append(label)
                quantity_entries[product_name] = entry

            def place_order():
                name = name_entry.get()
                surname = surname_entry.get()
                address = address_entry.get()
                quantities = {name: int(entry.get()) for name, entry in quantity_entries.items()}

                if not all([name, surname, address]) or any(q <= 0 for q in quantities.values()):
                    messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля корректно.")
                    return
                try:
                    self.cursor.execute("UPDATE users SET name = ?, lastname = ?, address = ? WHERE id = ?",
                                        (name, surname, address, self.user_id))
                    self.conn.commit()

                    self.cursor.execute(
                        "INSERT INTO orders (order_date, status, user_id) VALUES (DATE('now'), 'Новый', ?)",
                        (self.user_id,))
                    order_id = self.cursor.lastrowid
                    self.conn.commit()

                    for product_name, quantity in quantities.items():
                        self.cursor.execute("SELECT id FROM products WHERE name = ?", (product_name,))
                        product_db_id = self.cursor.fetchone()[0]
                        self.cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
                                            (order_id, product_db_id, quantity))
                        self.conn.commit()

                    messagebox.showinfo("Успех", "Заказ успешно оформлен!")
                    order_window.destroy()

                except sqlite3.IntegrityError as e:
                    messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")
                    self.conn.rollback()
                except ValueError as e:
                    messagebox.showerror("Ошибка", f"Ошибка ввода данных: {e}")
                    self.conn.rollback()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка оформления заказа: {e}")
                    self.conn.rollback()

            place_order_button = tk.Button(order_window, text="Оформить заказ", command=place_order)
            place_order_button.grid(row=4, column=0, columnspan=2, pady=10)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании окна заказа: {e}")

    def get_ordered_products(self):
        self.cursor.execute("""
            SELECT p.id, p.name 
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.user_id = ?
        """, (self.user_id,))
        return self.cursor.fetchall()

    def create_reviews_tab(self):
        reviews_tab = ttk.Frame(self.notebook)
        self.notebook.add(reviews_tab, text="Отзывы")

        self.reviews_tree = ttk.Treeview(reviews_tab, columns=("Product", "Rating", "Comment"), show="headings")
        self.reviews_tree.heading("Product", text="Товар")
        self.reviews_tree.heading("Rating", text="Оценка")
        self.reviews_tree.heading("Comment", text="Комментарий")
        self.reviews_tree.pack(fill="both", expand=True)  # Увеличиваем размер таблицы
        self.load_reviews()

        tk.Button(reviews_tab, text="Добавить отзыв", command=self.add_review).pack(pady=10)

    def load_reviews(self):
        for item in self.reviews_tree.get_children():
            self.reviews_tree.delete(item)
        self.cursor.execute("SELECT p.name, r.rating, r.comment FROM reviews r JOIN products p ON r.product_id = p.id")
        for review in self.cursor.fetchall():
            self.reviews_tree.insert("", "end", values=review)

    def add_review(self):
        if self.user_id is None:
            messagebox.showerror("Ошибка", "Вы не авторизованы.")
            return

        products = self.get_ordered_products()
        if not products:
            messagebox.showerror("Ошибка", "Вы не заказали ни одного товара.")
            return

        review_window = tk.Toplevel(self)
        review_window.title("Добавить отзыв")
        product_var = tk.StringVar(review_window)
        product_var.set(products[0][1])
        product_menu = tk.OptionMenu(review_window, product_var, *[product[1] for product in products])
        product_menu.pack(pady=5)

        rating_var = tk.IntVar(review_window)
        rating_scale = tk.Scale(review_window, from_=1, to=5, orient=tk.HORIZONTAL, variable=rating_var)
        rating_scale.pack(pady=5)

        comment_text = tk.Text(review_window, height=5, width=30)
        comment_text.pack(pady=5)

        def save_review():
            try:
                product_id = next((p[0] for p in products if p[1] == product_var.get()), None)
                rating = rating_var.get()
                comment = comment_text.get("1.0", tk.END).strip()

                if not product_id or not comment:
                    messagebox.showerror("Ошибка", "Заполните все поля.")
                    return
                self.cursor.execute("INSERT INTO reviews (product_id, rating, comment, user_id) VALUES (?, ?, ?, ?)",
                                    (product_id, rating, comment, self.user_id))
                self.conn.commit()
                self.load_reviews()
                review_window.destroy()
                messagebox.showinfo("Успех", "Отзыв успешно добавлен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления отзыва: {e}")
                self.conn.rollback()

        save_button = tk.Button(review_window, text="Сохранить", command=save_review)
        save_button.pack(pady=10)

    def exit_application(self):
        self.conn.close()
        self.master.destroy()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def __del__(self):
        self.conn.close()