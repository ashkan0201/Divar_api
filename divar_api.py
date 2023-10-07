import requests, lxml, bs4
import re
import csv
import tkinter as tk
from selenium import webdriver
from persiantools.jdatetime import JalaliDate
from datetime import datetime
from tkinter import ttk
from tkinter import messagebox
from time import sleep
from random import randint

response = requests.get("https://divar.ir/s/tehran/rent-apartment?sort=sort_date")
soup = bs4.BeautifulSoup(response.text , "lxml")
names = []
for link in soup.find_all("a"):
    href = link.get("href")
    if "/s/tehran/rent-apartment/" in href:
        href = href.replace("/s/tehran/rent-apartment/","")
        search = re.search("[\S]+\?", href)
        names.append(search.group())

def search(event=None):
    search_text = combo.get().lower()
    search_results = []
    for item in names:
        if search_text in item.lower():
            search_results.append(item)
    update_combobox(search_results)

def update_combobox(results):
    combo['values'] = results 

names.sort()

def api():
    value1 = entry1.get()
    value2 = entry2.get()
    selected_item = combo.get()

    timer1 = 0
    links = []
    page = 0
    state = True

    year_0_until_5 = []
    year_6_until_10 = []
    year_11_until_20 = []
    year_21_until_30 = []

    shamsi_year = JalaliDate.today().year
    driver = webdriver.Firefox()
    while state:
        get_name = f"https://divar.ir/s/tehran/rent-apartment/{selected_item}size={value1}-{value2}&building-age=0-30&user_type=agency&sort=sort_date&page={page}"
        driver.get(get_name)
        a_elements = driver.find_elements_by_tag_name("a")

        for a_element in a_elements:
            href = a_element.get_attribute("href")
            if "/v/" in href:
                links.append(href)

        elements = driver.find_elements_by_class_name("kt-empty-state__title")
        if elements and elements[0].text == "نتیجه‌ای با مشخصات مورد نظر شما پیدا نشد.":
            state = False
        else:
            page += 1

    while True:
        try:
            timer1 += 1
            if timer1 == 20:
                sleep(randint(10,15))
                timer1 = 0

            driver.get(links[0])
            details = []
            skip = []

            def convert_farsi_number_to_english(number):
                translation_table = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
                english_number = number.translate(translation_table)
                return english_number

            try:
                element_of_text = driver.find_elements_by_class_name("kt-unexpandable-row__value")
                for everything in element_of_text:
                    if everything.text == "توافقی":
                        skip.append(everything.text)
                if len(skip) != 0:
                    raise
            except:
                pass
            else:
                try:
                    slider = driver.find_elements_by_class_name("kt-range-slider__input")
                    if len(slider) == 0:
                        raise

                except:
                    elements_of_text_item = driver.find_elements_by_class_name("kt-group-row-item__value")
                    index1 = 0 
                    for everything in elements_of_text_item:
                        index1 += 1
                        details.append(everything.text)
                        if index1 == 2:
                            break

                    elements_of_text_ = driver.find_elements_by_class_name("kt-unexpandable-row__value")
                    index2 = 0 
                    for everything in elements_of_text_:
                        index2 += 1    
                        if everything.text == "مجانی":
                            details.append("*")
                        else:
                            details.append(everything.text)
                        if index2 == 2:
                            break
                    demo_datails = []
                    for everything in details:
                        english_number = convert_farsi_number_to_english(everything)
                        if english_number == "*":
                            demo_datails.append("*")
                        elif "٬" in english_number:
                            english_number = english_number.replace("٬","")
                            english_number = english_number.replace(" تومان","")
                            demo_datails.append(int(english_number))
                        else:
                            demo_datails.append(int(english_number))
                    size = demo_datails[0]
                    year = shamsi_year - demo_datails[1]
                    vadieh = demo_datails[2]
                    if demo_datails[3] == "*":
                        ejareh = "*"
                    else:
                        ejareh = demo_datails[3]

                    if "*" in details:
                        result = vadieh / size
                    else:
                        result = (((ejareh/3)*100) + vadieh) / size

                else:
                    elements_of_text_item = driver.find_elements_by_class_name("kt-group-row-item__value")
                    for everything in elements_of_text_item:
                        if everything.text == "رایگان":
                            details.append("*")
                        else:
                            details.append(everything.text)

                    details = details[:2] + details[3:5]
                    demo_datails = []
                    for everything in details:
                        english_number = convert_farsi_number_to_english(everything)
                        if english_number == "*":
                            demo_datails.append("*")
                        elif "میلیارد" in english_number:
                            english_number = english_number.split(" ")
                            demo_datails.append(int(float(english_number[0])*1000000000))
                        elif "میلیون" in english_number:
                            english_number = english_number.split(" ")
                            demo_datails.append(int(float(english_number[0])*1000000))
                        elif "هزار" in english_number:
                            english_number = english_number.split(" ")
                            demo_datails.append(int(float(english_number[0])*1000))
                        else:
                            demo_datails.append(int(english_number))

                    size = demo_datails[0]
                    year = shamsi_year - demo_datails[1]
                    vadieh = demo_datails[2]
                    if demo_datails[3] == "*":
                        ejareh = "*"
                    else:
                        ejareh = demo_datails[3]

                    if "*" in details:
                        result = vadieh / size
                    else:
                        result = (((ejareh/3)*100) + vadieh) / size
            try:
                if year <= 5:
                    year_0_until_5.append(int(result))
                elif 6 <= year <= 10:
                    year_6_until_10.append(int(result))
                elif 11 <= year <= 20:
                    year_11_until_20.append(int(result))
                elif 21 <= year <= 30:
                    year_21_until_30.append(int(result))
            except:
                pass
        except:
            links.append(links[0])
        else:
            links.remove(links[0])
        
        if len(links) == 0:
            break

    time = f"{JalaliDate.today().year}/{JalaliDate.today().month}/{JalaliDate.today().day} {datetime.today().hour}:{datetime.today().minute}:{datetime.today().second}"
    if len(year_0_until_5) == 0:
        index1 = "-"
    elif len(year_0_until_5) == 1:
        index1 = max(year_0_until_5)
    else:
        index1 = f"{min(year_0_until_5)}_{max(year_0_until_5)}"

    if len(year_6_until_10) == 0:
        index2 = "-"
    elif len(year_6_until_10) == 1:
        index2 = max(year_6_until_10)
    else:
        index2 = f"{min(year_6_until_10)}_{max(year_6_until_10)}"

    if len(year_11_until_20) == 0:
        index3 = "-"
    elif len(year_11_until_20) == 1:
        index3 = max(year_11_until_20)
    else:
        index3 = f"{min(year_11_until_20)}_{max(year_11_until_20)}"
    
    if len(year_21_until_30) == 0:
        index4 = "-"
    elif len(year_21_until_30) == 1:
        index4 = max(year_21_until_30)
    else:
        index4 = f"{min(year_21_until_30)}_{max(year_21_until_30)}"
    
    lst = [selected_item, f"{value1} until {value2}", time, index1, index2, index3, index4]
    with open("output.csv", 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(lst)
    driver.quit()
    messagebox.showinfo("پیام", f"متراژ: {value1}\nتا: {value2}\nمنطقه: {selected_item}")

root = tk.Tk()
root.title("divar_ip")

label1 = ttk.Label(root, text="متراژ: ")
label1.grid(row=0, column=0, padx=5, pady=5)
entry1 = ttk.Entry(root)
entry1.grid(row=0, column=1, padx=5, pady=5)

label2 = ttk.Label(root, text="تا: ")
label2.grid(row=1, column=0, padx=5, pady=5)
entry2 = ttk.Entry(root)
entry2.grid(row=1, column=1, padx=5, pady=5)

label3 = ttk.Label(root, text="منطقه: ")
label3.grid(row=2, column=0, padx=5, pady=5)
combo = ttk.Combobox(root, values=names)
combo.grid(row=2, column=1, padx=5, pady=5)

button = ttk.Button(root, text="ارسال", command=api)
button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

update_combobox(names)
combo.bind("<KeyRelease>", search)

root.mainloop()