# -*- coding: utf-8 -*-
# Copyright (c) 2023 mashu3
# This software is released under the MIT License, see LICENSE.

import os
import sys
import pikepdf
import zipfile
import datetime
import platform
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from manga2pdf import MangaPdfConverter

class CalendarWidget(tk.Toplevel):
    def __init__(self, master=None, callback=None, x=0, y=0, **kw):
        super().__init__(master, **kw)
        self.attributes('-topmost', True)
        self.callback = callback
        self.geometry(f"+{x}+{y}")
        self.current_date = datetime.datetime.now()
        self.create_widgets()

    def create_widgets(self):
        self.frame_top = tk.Frame(self)
        self.frame_top.pack(pady=1)
        self.prev_year_btn = tk.Button(self.frame_top, text="<", font=("", 10), command=self.prev_year, relief="flat", repeatdelay=100, repeatinterval=300)
        self.prev_year_btn.pack(side="left", padx=1)
        self.label_year = tk.Label(self.frame_top, text=self.current_date.year, font=("", 10))
        self.label_year.pack(side="left")
        self.next_year_btn = tk.Button(self.frame_top, text=">", font=("", 10), command=self.next_year, relief="flat", repeatdelay=100, repeatinterval=300)
        self.next_year_btn.pack(side="left", padx=1)
        self.previous_month = tk.Button(self.frame_top, text="<", font=("", 10), command=self.prev_month, relief="flat", repeatdelay=100, repeatinterval=300)
        self.previous_month.pack(side="left", padx=1)
        self.label_month = tk.Label(self.frame_top, text=self.current_date.strftime("%B"), font=("", 10))
        self.label_month.pack(side="left", padx=1)
        self.next_month = tk.Button(self.frame_top, text=">", font=("", 10), command=self.next_month, relief="flat", repeatdelay=100, repeatinterval=300)
        self.next_month.pack(side="left", padx=1)

        self.frame_week = tk.Frame(self)
        self.frame_week.pack()

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        colors = ["black", "black", "black", "black", "black", "blue", "red"]
        for i, (day, color) in enumerate(zip(days, colors)):
            lbl = tk.Button(self.frame_week, text=day, font=("", 10), disabledforeground=color, state="disabled", height=1, width=1, relief="flat", padx=5, pady=1)
            lbl.grid(column=i, row=0)

        self.frame_calendar = tk.Frame(self)
        self.frame_calendar.pack()
        self.update_calendar()

    def update_calendar(self):
        for widget in self.frame_calendar.winfo_children():
            widget.destroy()

        start_date = self.current_date.replace(day=1)
        if start_date.weekday() != 0:
            start_date -= datetime.timedelta(days=start_date.weekday())
        end_date = start_date + datetime.timedelta(weeks=6)

        delta = datetime.timedelta(days=1)
        current_date = start_date

        row = 0
        while current_date < end_date:
            for col in range(7):
                day = current_date.day
                btn_state = "disabled" if current_date.month != self.current_date.month else "normal"
                btn = tk.Button(self.frame_calendar, text=day, font=("", 10), height=1, width=1, relief="flat", state=btn_state, padx=5, pady=1,
                                command=lambda d=current_date: self.set_date(d))
                btn.grid(column=col, row=row)
                current_date += delta
            row += 1

        self.label_year["text"] = self.current_date.year
        self.label_month["text"] = self.current_date.strftime("%B")

    def set_date(self, date):
        if self.callback:
            self.callback(date)
        self.destroy()

    def prev_month(self):
        self.current_date -= datetime.timedelta(days=28)
        self.update_calendar()

    def next_month(self):
        self.current_date += datetime.timedelta(days=28)
        self.update_calendar()

    def prev_year(self):
        self.current_date = datetime.date(self.current_date.year - 1, self.current_date.month, 1)
        self.update_calendar()

    def next_year(self):
        self.current_date = datetime.date(self.current_date.year + 1, self.current_date.month, 1)
        self.update_calendar()

class MangaPdfConverterGUI:
    def __init__(self, master):
        self.master = master
        self.language = "en" # Set default language to english
        master.title("Manga PDF Converter")
        self.master.resizable(0, 0)
        self.processing_window = None
        self.system = platform.system()

        # Create five frames
        path_frame =ttk.Frame(master)
        conversion_frame = ttk.Frame(master)
        direction_frame = ttk.Frame(master)
        pagelayout_frame = ttk.Frame(master)
        pagemode_frame = ttk.Frame(master)
        metadata_frame = ttk.Frame(master)
        button_frame = ttk.Frame(master)

        # Set grid layout
        path_frame.grid(row=0, column=0, columnspan=3, sticky='we')
        conversion_frame.grid(row=1, column=0, sticky='nswe')
        direction_frame.grid(row=2, column=0, sticky='nswe')
        pagelayout_frame.grid(row=1, column=1, rowspan=2, sticky='nswe')
        pagemode_frame.grid(row=1, column=2, rowspan=2, sticky='nswe')
        metadata_frame.grid(row=3, column=0, columnspan=3, sticky='we')
        button_frame.grid(row=4, column=0, columnspan=3, sticky='we')

        # Add input path label and entry
        input_frame = ttk.Frame(path_frame)
        input_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
        self.input_label_text = {"en": "Input Path:", "ja": "入力パス:"}
        self.input_label = ttk.Label(input_frame, text=self.input_label_text[self.language])
        self.input_label.pack(side="left", padx=10, pady=2)
        self.input_file_button_text = {"en": "Select File", "ja": "ファイル選択"}
        self.input_file_button = ttk.Button(input_frame, text=self.input_file_button_text[self.language], command=self.browse_input_file)
        self.input_file_button.pack(side="right", pady=2)
        self.input_directory_button_text = {"en": "Select Directory", "ja": "フォルダ選択"}
        self.input_directory_button = ttk.Button(input_frame, text=self.input_directory_button_text[self.language], command=self.browse_input_directory)
        self.input_directory_button.pack(side="right", padx=10, pady=2)
        if self.system == "Windows":
            self.input_entry = ttk.Entry(path_frame, width=90)
        else:
            self.input_entry = ttk.Entry(path_frame, width=65)
        self.input_entry.grid(row=1, column=0, columnspan=3, padx=10, pady=2, sticky="ew")

        # Add output path label and entry
        output_frame = ttk.Frame(path_frame)
        output_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
        self.output_label_text = {"en": "Output Path:", "ja": "出力パス:"}
        self.output_label = ttk.Label(output_frame, text=self.output_label_text[self.language])
        self.output_label.pack(side="left", padx=10, pady=2)
        self.output_browse_button_text = {"en": "Browse", "ja": "参照"}
        self.output_browse_button = ttk.Button(output_frame, text=self.output_browse_button_text[self.language], command=self.browse_output_path)
        self.output_browse_button.pack(side="right", pady=2)
        self.auto_output_button_text = {"en": "Auto", "ja": "自動設定"}
        self.auto_output_button = ttk.Button(output_frame, text=self.auto_output_button_text[self.language], command=self.auto_output_path)
        self.auto_output_button.pack(side="right", padx=10, pady=2)
        if self.system == "Windows":
            self.output_entry = ttk.Entry(path_frame, width=90)
        else:
            self.output_entry = ttk.Entry(path_frame, width=65)
        self.output_entry.grid(row=3, column=0, columnspan=3, padx=10, pady=2, sticky="ew")

        # Create a LabelFrame for the conversion options
        self.conversion_label_text = {"en": "Conversion Options:", "ja": "圧縮方式:"}
        self.conversion_labelframe = ttk.LabelFrame(conversion_frame, text=self.conversion_label_text[self.language], padding=5)
        self.conversion_labelframe.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=2, pady=1)

        self.conversion_var = tk.StringVar(value="none")
        self.conversion_text = {
            "en": ["No Compression", "Convert images to JPEG", "Convert images to grayscale"],
            "ja": ["圧縮なし", "JPEG画像に変換", "グレースケール画像に変換"],
        }
        self.conversion_value = ["none", "jpeg", "grayscale"]
        self.conversion_radio = []
        for i, conversion in enumerate(self.conversion_text[self.language]):
            conversion_radio = ttk.Radiobutton(
                self.conversion_labelframe, text=conversion, variable=self.conversion_var, value=self.conversion_value[i]
            )
            self.conversion_radio.append(conversion_radio)
            conversion_radio.grid(row=i+1, column=0, sticky="nsew", padx=2, pady=1)

        # Create a LabelFrame for the direction options
        self.direction_label_text = {"en": "Direction:", "ja": "綴じ方向:"}
        self.direction_labelframe = ttk.LabelFrame(direction_frame, text=self.direction_label_text[self.language], padding=5)
        self.direction_labelframe.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=2, pady=1)

        self.direction_var = tk.StringVar(value="R2L")
        self.direction_text = {
            "en": ["L2R", "R2L"],
            "ja": ["左綴じ", "右綴じ"],
        }
        self.direction_value = ["L2R", "R2L"]
        self.direction_radio = []
        for i, direction in enumerate(self.direction_text[self.language]):
            direction_radio = ttk.Radiobutton(
                self.direction_labelframe, text=direction, variable=self.direction_var, value=self.direction_value[i])
            self.direction_radio.append(direction_radio)
            direction_radio.grid(row=i+1, column=0, sticky="nsew", padx=2, pady=1)
        
        # Create a LabelFrame for the page layout options
        self.pagelayout_label_text = {"en": "Page Layout:", "ja": "ページレイアウト:"}
        self.pagelayout_labelframe = ttk.LabelFrame(pagelayout_frame, text=self.pagelayout_label_text[self.language], padding=5)
        self.pagelayout_labelframe.grid(row=0, column=0, rowspan=10, sticky="nsew", padx=2, pady=1)

        self.pagelayout_var = tk.StringVar(value="TwoPageRight")
        self.pagelayout_text = {
            "en": ["SinglePage", "OneColumn", "TwoPageLeft", "TwoColumnLeft", "TwoPageRight", "TwoColumnRight"],
            "ja": ["単一ページ表示", "スクロールを有効にする", "見開きページ表示", "見開きページでスクロール", "見開きページ\n(表紙は単独表示)", "見開きページでスクロール\n(表紙は単独表示)"],
        }
        self.pagelayout_value = ["SinglePage", "OneColumn", "TwoPageLeft", "TwoColumnLeft", "TwoPageRight", "TwoColumnRight"]
        self.pagelayout_radio = []
        for i, pagelayout in enumerate(self.pagelayout_text[self.language]):
            pagelayout_radio = ttk.Radiobutton(
                self.pagelayout_labelframe, text=pagelayout, variable=self.pagelayout_var, value=self.pagelayout_value[i]
            )
            self.pagelayout_radio.append(pagelayout_radio)
            pagelayout_radio.grid(row=i+1, column=0, sticky="nsew", padx=2, pady=1)

        # Create a LabelFrame for the page mode options
        self.pagemode_label_text = {"en": "Page Mode:", "ja": "ページモード:"}
        self.pagemode_labelframe = ttk.LabelFrame(pagemode_frame, text=self.pagemode_label_text[self.language], padding=5)
        self.pagemode_labelframe.grid(row=0, column=0, rowspan=10, sticky="nsew", padx=2, pady=1)

        self.pagemode_var = tk.StringVar(value="UseNone")
        self.pagemode_text = {
            "en": ["UseNone", "UseOutlines", "UseThumbs", "FullScreen", "UseOC", "UseAttachments"],
            "ja": ["デフォルト表示", "アウトラインパネルを表示", "サムネイルパネルを表示", "フルスクリーンモード", "コンテンツパネルを表示", "添付ファイルパネルを表示"],
        }
        self.pagemode_value = ["UseNone", "UseOutlines", "UseThumbs", "FullScreen", "UseOC", "UseAttachments"]
        self.pagemode_radio = []
        for i, pagemode in enumerate(self.pagemode_text[self.language]):
            pagemode_radio = ttk.Radiobutton(
                self.pagemode_labelframe, text=pagemode, variable=self.pagemode_var, value=self.pagemode_value[i]
            )
            self.pagemode_radio.append(pagemode_radio)
            pagemode_radio.grid(row=i+1, column=0, sticky="nsew", padx=2, pady=1)

        # Create a LabelFrame for the metadata options
        self.metadata_label_text = {"en": "Metadata:", "ja": "メタデータ:"}
        self.metadata_labelframe = ttk.LabelFrame(metadata_frame, text=self.metadata_label_text[self.language], padding=5)
        self.metadata_labelframe.grid(row=0, column=0, columnspan=3, padx=5, pady=2, sticky="ew")

        self.title_label_text = {"en": "Title:", "ja": "タイトル:"}
        self.title_label = ttk.Label(self.metadata_labelframe, text=self.title_label_text[self.language])
        self.title_label.grid(row=0, column=0, padx=10, pady=2, sticky="w")
        if self.system == "Windows":
            self.title_entry = ttk.Entry(self.metadata_labelframe, width=65)
        else:
            self.title_entry = ttk.Entry(self.metadata_labelframe, width=50)
        self.title_entry.grid(row=0, column=1, padx=10, pady=2, sticky="w")

        self.author_label_text = {"en": "Author:", "ja": "作成者:"}
        self.author_label = ttk.Label(self.metadata_labelframe, text=self.author_label_text[self.language])
        self.author_label.grid(row=1, column=0, padx=10, pady=2, sticky="w")
        if self.system == "Windows":
            self.author_entry = ttk.Entry(self.metadata_labelframe, width=65)
        else:
            self.author_entry = ttk.Entry(self.metadata_labelframe, width=50)
        self.author_entry.grid(row=1, column=1, padx=10, pady=2, sticky="w")

        self.publisher_label_text = {"en": "Publisher:", "ja": "出版社:"}
        self.publisher_label = ttk.Label(self.metadata_labelframe, text=self.publisher_label_text[self.language])
        self.publisher_label.grid(row=2, column=0, padx=10, pady=2, sticky="w")
        if self.system == "Windows":
            self.publisher_entry = ttk.Entry(self.metadata_labelframe, width=65)
        else:
            self.publisher_entry = ttk.Entry(self.metadata_labelframe, width=50)
        self.publisher_entry.grid(row=2, column=1, padx=10, pady=2, sticky="w")

        self.creation_date_label_text = {"en": "Create Date:", "ja": "作成日:"}
        self.creation_date_label = ttk.Label(self.metadata_labelframe, text=self.creation_date_label_text[self.language])
        self.creation_date_label.grid(row=3, column=0, padx=10, pady=2, sticky="w")
        creation_date_frame = ttk.Frame(self.metadata_labelframe)
        creation_date_frame.grid(row=3, column=1, columnspan=2, padx=10, pady=2, sticky="w")
        self.creation_date_combobox = ttk.Combobox(creation_date_frame, width=10)
        self.creation_date_combobox.bind('<Button-1>', lambda e: self.select_date(self.creation_date_combobox, master))
        self.creation_date_combobox.pack(side="left")
        self.creation_time_combobox = self.create_time_combobox(creation_date_frame)
        self.creation_time_combobox.pack(side="left", padx=5)
        self.ctime_var = tk.BooleanVar()
        self.ctime_var.set(True)
        self.ctime_label_text = {"en": "Sync File Timestamp", "ja": "ファイルのタイムスタンプ変更"}
        self.ctime_check_box = ttk.Checkbutton(creation_date_frame, text=self.ctime_label_text[self.language], variable=self.ctime_var)        
        self.ctime_check_box.pack(side="left", padx=5)
        if self.system not in ["Windows", "Darwin"]:
            self.ctime_check_box.configure(state=tk.DISABLED)

        self.modify_date_label_text = {"en": "Modify Date:", "ja": "更新日:"}
        self.modify_date_label = ttk.Label(self.metadata_labelframe, text=self.modify_date_label_text[self.language])
        self.modify_date_label.grid(row=4, column=0, padx=10, pady=2, sticky="w")
        modify_date_frame = ttk.Frame(self.metadata_labelframe)
        modify_date_frame.grid(row=4, column=1, columnspan=2, padx=10, pady=2, sticky="w")
        self.modify_date_combobox = ttk.Combobox(modify_date_frame, width=10)
        self.modify_date_combobox.bind('<Button-1>', lambda e: self.select_date(self.modify_date_combobox, master))
        self.modify_date_combobox.pack(side="left")
        self.modify_time_combobox = self.create_time_combobox(modify_date_frame)
        self.modify_time_combobox.pack(side="left", padx=5)
        self.mtime_var = tk.BooleanVar()
        self.mtime_var.set(True)
        self.mtime_label_text = {"en": "Sync File Timestamp", "ja": "ファイルのタイムスタンプ変更"}
        self.mtime_check_box = ttk.Checkbutton(modify_date_frame, text=self.mtime_label_text[self.language], variable=self.mtime_var)        
        self.mtime_check_box.pack(side="left", padx=5)

        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.creation_date_combobox.set(current_date)
        self.creation_time_combobox.set(current_time)
        self.modify_date_combobox.set(current_date)
        self.modify_time_combobox.set(current_time)

        # Add language toggle button
        self.language_button_text = {"en": "日本語表示に切替", "ja": "Display in English"}
        self.language_button = ttk.Button(button_frame, text=self.language_button_text[self.language], command=self.toggle_language)
        self.language_button.pack(side="left", padx=15, pady=5)

        # Add quit button
        self.quit_button_text = {"en": "Quit", "ja": "終了"}
        self.quit_button = ttk.Button(button_frame, text=self.quit_button_text[self.language], command=sys.exit)
        self.quit_button.pack(side="left", padx=15, pady=5)

        # Add convert button
        self.convert_button_text = {"en": "Convert", "ja": "変換"}
        self.convert_button = ttk.Button(button_frame, text=self.convert_button_text[self.language], command=self.run_convert)
        self.convert_button.pack(side="right", padx=15, pady=5)

        # Add padding to all widgets
        for child in master.winfo_children():
            child.grid_configure(padx=10, pady=5)

        # Set minimum size of the window
        master.minsize(400, 250)

        # Center the window
        master.eval('tk::PlaceWindow . center')

    def select_date(self, combobox, root):
        def date_callback(selected_date):
            combobox.delete(0, tk.END)
            combobox.insert(0, selected_date.strftime("%Y-%m-%d"))
            combobox.set(selected_date.strftime("%Y-%m-%d"))

        x = combobox.winfo_rootx()
        y = combobox.winfo_rooty() + combobox.winfo_height()
        CalendarWidget(master=root, callback=date_callback, x=x, y=y)
        
    def create_time_combobox(self, frame):
        hours = [f"{h:02d}" for h in range(24)]
        minutes = [f"{m:02d}" for m in range(60)]
        time_values = [f"{h}:{m}:00" for h in hours for m in minutes]
        time_combobox = ttk.Combobox(frame, values=time_values, width=8)
        return time_combobox

    def toggle_language(self):
        # Toggle the language between english and japanese
        if self.language == "en":
            self.language = "ja"
            self.language_button.configure(text="Display in English")
        else:
            self.language = "en"
            self.language_button.configure(text="日本語表示に切替")
        self.update_language()

    def update_language(self):
        self.input_file_button.configure(text=self.input_file_button_text[self.language])
        self.input_directory_button.configure(text=self.input_directory_button_text[self.language])
        self.input_label.configure(text=self.input_label_text[self.language])
        self.output_label.configure(text=self.output_label_text[self.language])
        self.output_browse_button.configure(text=self.output_browse_button_text[self.language])
        self.auto_output_button.configure(text=self.auto_output_button_text[self.language])
        self.conversion_labelframe.configure(text=self.conversion_label_text[self.language])
        for i, conversion in enumerate(self.conversion_text[self.language]):
            self.conversion_radio[i].configure(text=conversion)
        self.conversion_var.set(self.conversion_var.get())
        self.direction_labelframe.configure(text=self.direction_label_text[self.language])
        for i, direction in enumerate(self.direction_text[self.language]):
            self.direction_radio[i].configure(text=direction)
        self.direction_var.set(self.direction_var.get())
        self.pagelayout_labelframe.configure(text=self.pagelayout_label_text[self.language])
        for i, pagelayout in enumerate(self.pagelayout_text[self.language]):
            self.pagelayout_radio[i].configure(text=pagelayout)
        self.pagemode_var.set(self.pagemode_var.get())
        self.pagemode_labelframe.configure(text=self.pagemode_label_text[self.language])
        for i, pagemode in enumerate(self.pagemode_text[self.language]):
            self.pagemode_radio[i].configure(text=pagemode)
        self.pagelayout_var.set(self.pagelayout_var.get())
        self.metadata_labelframe.configure(text=self.metadata_label_text[self.language])
        self.title_label.configure(text=self.title_label_text[self.language])
        self.author_label.configure(text=self.author_label_text[self.language])
        self.publisher_label.configure(text=self.publisher_label_text[self.language])
        self.creation_date_label.configure(text=self.creation_date_label_text[self.language])
        self.ctime_check_box.configure(text=self.ctime_label_text[self.language])
        self.modify_date_label.configure(text=self.modify_date_label_text[self.language])
        self.mtime_check_box.configure(text=self.mtime_label_text[self.language])
        self.language_button.configure(text=self.language_button_text[self.language])
        self.convert_button.configure(text=self.convert_button_text[self.language])
        self.quit_button.configure(text=self.quit_button_text[self.language])

    def set_output_path(self, path):
        self.output_path = path
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, path)

    def browse_output_path(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if path:
            self.set_output_path(path)

    def browse_input_file(self):
        filetypes = (("zip files", "*.zip"), ("cbz files", "*.cbz"), ("rar files", "*.rar"), ("cbr files", "*.cbr"), ("epub files", "*.epub"), ("mobi files", "*.mobi"), ("azw files", "*.azw3"), ("azw files", "*.azw"), ("all files", "*.*"))
        path = filedialog.askopenfilename(filetypes=filetypes)

        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.publisher_entry.delete(0, tk.END)
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.creation_date_combobox.set(current_date)
        self.creation_time_combobox.set(current_time)
        self.modify_date_combobox.set(current_date)
        self.modify_time_combobox.set(current_time)

        if path:
            self.input_path = path.replace('/', os.sep)
            self.set_output_path(os.path.splitext(path)[0] + ".pdf")
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)

            def read_metadata(input_path=self.input_path):
                converter = MangaPdfConverter(input_path=self.input_path, output_path=self.output_path, pagelayout=self.pagelayout_var.get(), pagemode=self.pagemode_var.get(), direction=self.direction_var.get())
                if converter.is_epub_file(input_path):
                    with zipfile.ZipFile(self.input_path) as epub:
                        opf_name = converter.extract_epub_contents(epub)[3]
                        epub_metadata = converter.extract_epub_metadata(epub, opf_name)
                        self.title_entry.delete(0, tk.END)
                        self.title_entry.insert(0, epub_metadata['title'])
                        self.author_entry.delete(0, tk.END)
                        self.author_entry.insert(0, epub_metadata['creator'])
                        self.publisher_entry.delete(0, tk.END)
                        self.publisher_entry.insert(0, epub_metadata['publisher'])
                        if epub_metadata['date']:
                            self.creation_date_combobox.set(epub_metadata['date'])
                #print(pdf_metadata)
            read_metadata()

    def browse_input_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.input_path = path
            # set output path to the input directory with ".pdf" extension
            output_path = os.path.join(path, os.path.basename(path) + ".pdf").replace(os.sep, '/')
            self.set_output_path(output_path)
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)
    
    def auto_output_path(self):
        # Get input path
        input_path = self.input_entry.get()

        # Notify user if no input path is provided
        if input_path == "":
            messagebox.showerror("Error", "Please select an input path first.", parent=self.master)
            return

        # Get output path
        output_path = self.output_entry.get()

        # Determine the output path if it is not specified
        if not output_path:
            input_basename = os.path.basename(input_path)
            input_directory = os.path.dirname(input_path)
            if os.path.isdir(input_path):
                output_path = os.path.join(input_path, input_basename + ".pdf").replace(os.sep, '/')
            else:
                output_path = os.path.join(input_directory, os.path.splitext(input_basename)[0] + ".pdf").replace(os.sep, '/')
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, output_path)
        # Notify user if the output path is not a PDF file
        elif not output_path.endswith(".pdf"):
            if os.path.isdir(output_path):
                input_basename = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(output_path, input_basename + ".pdf").replace(os.sep, '/')
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, output_path)
            else:
                messagebox.showerror("Error", "Output path is not a PDF file", parent=self.master)
                return

        # Set the output path and filename
        self.output_path = output_path

    def set_metadata(self, output_path):
        with pikepdf.Pdf.open(output_path, allow_overwriting_input=True) as pdf:
            with pdf.open_metadata(set_pikepdf_as_editor=False) as pdf_metadata:
                pdf_metadata['dc:title'] = self.title_entry.get() if self.title_entry.get() else ''
                pdf_metadata['dc:creator'] = [self.author_entry.get() if self.author_entry.get() else '']
                pdf_metadata['dc:publisher'] = self.publisher_entry.get() if self.publisher_entry.get() else ''
                pdf_metadata['xmp:CreateDate'] = f"{self.creation_date_combobox.get()} {self.creation_time_combobox.get()}"
                pdf_metadata['xmp:ModifyDate'] = f"{self.modify_date_combobox.get()} {self.modify_time_combobox.get()}"
                pdf_metadata['pdf:Producer'] = ''
            pdf.save(output_path, linearize=True)

    def set_timestamp(self, output_path):
        if self.ctime_var.get():
           if self.system == "Windows":
                import win32_setctime
                ctime_new = datetime.datetime.strptime(f"{self.creation_date_combobox.get()} {self.creation_time_combobox.get()}", "%Y-%m-%d %H:%M:%S")
                win32_setctime.setctime(output_path, ctime_new.timestamp())
           elif self.system == "Darwin":
                date_object = datetime.datetime.strptime(self.creation_date_combobox.get(), "%Y-%m-%d")
                formatted_date = date_object.strftime("%m/%d/%Y")
                command = ["SetFile", "-d", f"{formatted_date} {self.creation_time_combobox.get()}", output_path]
                try:
                    subprocess.run(command, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error: {e}")
                except FileNotFoundError:
                    print("SetFile command not found. Please ensure that Xcode Command Line Tools are installed.")
           else:
                print("Error: Unable to modify 'ctime' in Linux environment")

        mtime_new = datetime.datetime.strptime(f"{self.modify_date_combobox.get()} {self.modify_time_combobox.get()}", "%Y-%m-%d %H:%M:%S")
        if self.mtime_var.get():
            os.utime(path=output_path, times=(mtime_new.timestamp(), mtime_new.timestamp()))

    def run_convert(self):
        # Get input and output paths
        input_path = self.input_entry.get()
        output_path = self.output_entry.get()

        # Check if input path is empty
        if not input_path:
            messagebox.showerror("Error", "Please specify an input path.", parent=self.master)
            return

        # Determine the output path if it is not specified
        if not output_path:
            if os.path.isdir(input_path):
                input_dir, dir_name = os.path.split(input_path)
                output_path = os.path.join(input_dir, f"{dir_name}.pdf").replace(os.sep, '/')
            else:
                output_path = os.path.splitext(input_path)[0] + ".pdf"

        # Notify user if no output path is provided
        if not output_path:
            messagebox.showerror("Error", "Please specify an output path.", parent=self.master)
            return
        
        # Determine the conversion options
        convert_to_jpeg = self.conversion_var.get() == "jpeg"
        convert_to_grayscale = self.conversion_var.get() == "grayscale"

        # Call MangaPdfConverter with the appropriate arguments
        try:
            converter = MangaPdfConverter(input_path=input_path, output_path=output_path, pagelayout=self.pagelayout_var.get(), pagemode=self.pagemode_var.get(), direction=self.direction_var.get())

            # Ask user if they want to convert
            confirm_text = {"en": "Are you sure you want to convert?", "ja": "変換処理を開始しますか？"}
            answer = messagebox.askyesno("Confirm Conversion", confirm_text[self.language], parent=self.master)

            if not answer:
                cancele_text = {"en": "Conversion canceled.", "ja": "変換処理を中止しました"}
                messagebox.showinfo("Conversion", cancele_text[self.language], parent=self.master)
                return
            
            # Create "Processing..." window
            processing_window = tk.Toplevel(self.master)
            # Get the position and size of the parent window
            main_x, main_y = self.master.winfo_x(), self.master.winfo_y()
            main_width, main_height = self.master.winfo_width(), self.master.winfo_height()
            # Calculate the position of the processing window
            sub_width, sub_height = 250, 30
            sub_x = main_x + (main_width - sub_width) // 2
            sub_y = main_y + (main_height - sub_height) // 2
            processing_window.geometry(f"{sub_width}x{sub_height}+{sub_x}+{sub_y}")
            # Set the title of the window
            processing_window.title("Manga PDF Converter")
            # Set the parent of the processing window
            processing_window.transient(self.master)
            # Add widgets to the frame
            processing_text = {"en": "Processing...", "ja": "変換処理中..."}
            processing_label = tk.Label(processing_window, text=processing_text[self.language])
            processing_label.pack()

            # Disable main window while process window is open
            #self.master.withdraw()

            # Make the processing window a modal dialog
            processing_window.lift()
            processing_window.focus_force()
            processing_window.wait_visibility()
            processing_window.grab_set()
            processing_label.update()

            if convert_to_jpeg:
                converter.set_convert_to_jpeg(True)
                converter.convert()
            elif convert_to_grayscale:
                converter.set_convert_to_grayscale(True)
                converter.convert()
            else:
                converter.convert()
            self.set_metadata(output_path)
            self.set_timestamp(output_path)

            # Close process window when done
            processing_window.grab_release()
            processing_window.destroy()

            # Re-enable main window
            #self.master.deiconify()

            # Check if output file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                complete_success_text = {"en": "Conversion complete!", "ja": "変換処理が完了しました！"}
                messagebox.showinfo("Success", complete_success_text[self.language], parent=self.master)
            else:
                complete_error_text = {"en": "Conversion failed", "ja": "変換処理に失敗しました"}
                messagebox.showerror("Error", complete_error_text[self.language], parent=self.master)

        except Exception as e:
            # Close process window when done
            processing_window.grab_release()
            processing_window.destroy()
            complete_error_text = {"en": "Conversion failed", "ja": "エラーで変換処理に失敗しました"}
            messagebox.showerror(title="Error", message=f"{complete_error_text[self.language]}\n{str(e)}", parent=self.master)

            # Re-enable main window
            self.master.deiconify()

def launch_gui():
    root = tk.Tk()
    MangaPdfConverterGUI(root)
    root.mainloop()

if __name__ == '__main__':
    launch_gui()