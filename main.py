from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options
import mysql.connector
import tkinter as tk
from tkinter import ttk


def tkinter(db, driver):
    def submit_action():
        global global_name, global_surname, global_url
        global_name = name_entry.get()
        global_surname = surname_entry.get()
        global_url = url_entry.get()

        save_user_data(db, global_name, global_surname, global_url)

        product_data = get_product_data(driver, global_url)

        save_product_data(db, global_url, product_data)

        db.commit()

        root.destroy()

        information_action(product_data['price'], product_data['sizes'])

    def information_action(price, sizes):
        info_root = tk.Tk()
        info_root.title("Kaydedilen Bilgiler")

        tk.Label(info_root, text=f"İsim: {global_name}").grid(row=0, column=1)
        tk.Label(info_root, text=f"Soyisim: {global_surname}").grid(row=1, column=1)
        tk.Label(info_root, text=f"URL: {global_url}").grid(row=2, column=1)

        tk.Label(info_root, text=f"Ürün Fiyat: {price}").grid(row=3, column=1)
        tk.Label(info_root, text=f"Stokta Kalan Ürünler: {sizes}").grid(row=4, column=1)

        istek_fiyat_label = tk.Label(info_root, text="Bu Fiyata Gelince Haber Ver:")
        istek_fiyat_label.grid(row=5, column=0, sticky=tk.E)
        istek_fiyat_entry = tk.Entry(info_root, width=15)
        istek_fiyat_entry.grid(row=5, column=1, sticky=tk.W + tk.E)
        info_root.grid_columnconfigure(0, weight=1)
        info_root.grid_columnconfigure(1, weight=1)

        istek_beden_label = tk.Label(info_root, text="İstediğiniz Beden:")
        istek_beden_label.grid(row=6, column=0, sticky=tk.E)
        istek_beden_entry = tk.Entry(info_root, width=15)
        istek_beden_entry.grid(row=6, column=1, sticky=tk.W + tk.E)
        info_root.grid_columnconfigure(0, weight=1)
        info_root.grid_columnconfigure(1, weight=1)

        def on_save_clicked():
            istenen_fiyat = istek_fiyat_entry.get()
            istenen_beden = istek_beden_entry.get()
            save_request_data(db, global_url, istenen_fiyat, istenen_beden)
            info_root.destroy()

        gonder_button = ttk.Button(info_root, text="Kaydet", command=on_save_clicked)
        gonder_button.grid(column=2, row=7, sticky=tk.E, pady=10)

        info_root.update_idletasks()
        width = info_root.winfo_width()
        height = info_root.winfo_height()
        x = (info_root.winfo_screenwidth() // 2) - (width // 2)
        y = (info_root.winfo_screenheight() // 2) - (height // 2)
        info_root.geometry(f'{width}x{height}+{x}+{y}')

        info_root.mainloop()

    root = tk.Tk()
    root.title("Ürün Bilgisi Kaydı")

    # Yazı tipi ve boyutları
    large_font = ('Verdana', 14)
    entry_font = ('Verdana', 14)
    button_font = ('Verdana', 12)

    style = ttk.Style()
    style.configure('TEntry', font=entry_font)
    style.configure('TButton', font=button_font)
    style.configure('TLabel', font=large_font)

    form_frame = ttk.Frame(root, padding="20")
    form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    name_label = ttk.Label(form_frame, text="İsim:")
    name_label.grid(column=0, row=0, sticky=tk.W)
    name_entry = ttk.Entry(form_frame, style='TEntry', width=30)
    name_entry.grid(column=1, row=0)

    surname_label = ttk.Label(form_frame, text="Soyisim:")
    surname_label.grid(column=0, row=1, sticky=tk.W)
    surname_entry = ttk.Entry(form_frame, style='TEntry', width=30)
    surname_entry.grid(column=1, row=1)

    url_label = ttk.Label(form_frame, text="URL:")
    url_label.grid(column=0, row=2, sticky=tk.W)
    url_entry = ttk.Entry(form_frame, style='TEntry', width=30)
    url_entry.grid(column=1, row=2)

    submit_button = ttk.Button(form_frame, text="Kaydet", style='TButton', command=submit_action)
    submit_button.grid(column=1, row=3, sticky=tk.E, pady=10)

    root.eval('tk::PlaceWindow . center')
    root.mainloop()


def get_product_data(driver, url):
    """Fetches the price and sizes of a product from a specific URL."""
    driver.get(url)
    WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "prc-dsc")))
    price = driver.find_element(By.CLASS_NAME, "prc-dsc").text

    WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "variants")))
    sizes = driver.find_element(By.CLASS_NAME, "variants").text.split('\n')
    sizes_text = ', '.join(sizes)

    return {'price': price, 'sizes': sizes_text}


def save_product_data(connection, url, product_data):
    """Saves product data to the database."""
    cursor = connection.cursor()  # Bir cursor oluştur
    query = "INSERT INTO commerce.sorgu(URL, Fiyat, Stok) VALUES (%s, %s, %s)"
    values = (url, product_data['price'], product_data['sizes'])
    cursor.execute(query, values)
    connection.commit()
    cursor.close()


def save_user_data(db, name, surname, url):
    """Saves user data to the database."""
    cursor = db.cursor()  # Bir cursor oluştur
    query = "INSERT INTO commerce.kullanıcılar(isim,soyisim,url) VALUES (%s, %s, %s)"
    values = (name, surname, url)
    cursor.execute(query, values)
    db.commit()  # commit işlemini connection üzerinden yap
    cursor.close()  # Cursor'u kapat

def save_request_data(db, url, istenen_fiyat, istenen_beden):
    """Saves the user's request data to the database."""
    cursor = db.cursor()
    query = "INSERT INTO istekler (url, istenen_fiyat, istenen_beden) VALUES (%s, %s, %s)"
    values = (url, istenen_fiyat, istenen_beden)
    cursor.execute(query, values)
    db.commit()
    cursor.close()





def setup_driver():
    """Configures web driver settings and returns it."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)


def setup_database_connection():
    """Establishes a database connection and returns a cursor."""
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="myPassword",
        database="myDatabase"
    )
    return connection


def main():
    driver = setup_driver()
    connection = setup_database_connection()
    tkinter(connection, driver)

    connection.close()
    driver.quit()


if __name__ == "__main__":
    main()