# -*- coding: utf-8 -*-
# Copyright (c) 2025 mashu3
# This software is released under the MIT License, see LICENSE.

import os
import sys
import i18n
import json
import tkface
import pikepdf
import zipfile
import datetime
import platform
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from .manga2pdf import MangaPdfConverter, __version__


class MangaPdfConverterGUI:
    def __init__(self, master):
        self.master = master
        self.lang_map = {'English': 'en_US', '日本語': 'ja_JP', 'Français': 'fr_FR', 'Español': 'es_ES', 'Deutsch': 'de_DE', '简体中文': 'zh_CN', '繁體中文': 'zh_TW'}
        self.rev_lang_map = {v: k for k, v in self.lang_map.items()}
        self.setup_i18n()
        master.title(f"Manga PDF Converter v{__version__}")
        self.master.resizable(0, 0)
        self.processing_window = None
        self.system = platform.system()
        
        # Enable DPI awareness for Windows
        if self.system == "Windows":
            tkface.win.dpi(master)

        self.long_languages = {'fr', 'de', 'es'}
        if self.system == "Windows":
            self.default_entry_width = 90
            self.long_entry_width = 110
            self.default_meta_entry_width = 65
            self.long_meta_entry_width = 80
        else:
            self.default_entry_width = 65
            self.long_entry_width = 80
            self.default_meta_entry_width = 50
            self.long_meta_entry_width = 65
            
        current_entry_width = self.long_entry_width if i18n.get('locale') in self.long_languages else self.default_entry_width
        current_meta_entry_width = self.long_meta_entry_width if i18n.get('locale') in self.long_languages else self.default_meta_entry_width

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
        self.input_label = ttk.Label(input_frame, text=i18n.t('gui.input_path'))
        self.input_label.pack(side="left", padx=10, pady=2)
        self.input_file_button = ttk.Button(input_frame, text=i18n.t('gui.select_file'), command=self.browse_input_file)
        self.input_file_button.pack(side="right", pady=2)
        self.input_directory_button = ttk.Button(input_frame, text=i18n.t('gui.select_directory'), command=self.browse_input_directory)
        self.input_directory_button.pack(side="right", padx=10, pady=2)
        self.input_entry = ttk.Entry(path_frame, width=current_entry_width)
        self.input_entry.grid(row=1, column=0, columnspan=3, padx=10, pady=2, sticky="ew")

        # Add output path label and entry
        output_frame = ttk.Frame(path_frame)
        output_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
        self.output_label = ttk.Label(output_frame, text=i18n.t('gui.output_path'))
        self.output_label.pack(side="left", padx=10, pady=2)
        self.output_browse_button = ttk.Button(output_frame, text=i18n.t('gui.browse'), command=self.browse_output_path)
        self.output_browse_button.pack(side="right", pady=2)
        self.auto_output_button = ttk.Button(output_frame, text=i18n.t('gui.auto'), command=self.auto_output_path)
        self.auto_output_button.pack(side="right", padx=10, pady=2)
        self.output_entry = ttk.Entry(path_frame, width=current_entry_width)
        self.output_entry.grid(row=3, column=0, columnspan=3, padx=10, pady=2, sticky="ew")

        # Create a LabelFrame for the conversion options
        self.conversion_labelframe = ttk.LabelFrame(conversion_frame, text=i18n.t('gui.conversion_options'), padding=5)
        self.conversion_labelframe.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=2, pady=1)

        self.conversion_var = tk.StringVar(value="none")
        self.conversion_text_keys = ["no_compression", "convert_to_jpeg", "convert_to_grayscale"]
        self.conversion_value = ["none", "jpeg", "grayscale"]
        self.conversion_radio = []
        for i, key in enumerate(self.conversion_text_keys):
            conversion_radio = ttk.Radiobutton(
                self.conversion_labelframe, text=i18n.t(f'gui.{key}'), variable=self.conversion_var, value=self.conversion_value[i]
            )
            self.conversion_radio.append(conversion_radio)
            conversion_radio.grid(row=i+1, column=0, sticky="nsew", padx=2, pady=1)

        # Create a LabelFrame for the direction options
        self.direction_labelframe = ttk.LabelFrame(direction_frame, text=i18n.t('gui.direction'), padding=5)
        self.direction_labelframe.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=2, pady=1)

        self.direction_var = tk.StringVar(value="R2L")
        self.direction_text_keys = ["l2r", "r2l"]
        self.direction_value = ["L2R", "R2L"]
        self.direction_radio = []
        for i, key in enumerate(self.direction_text_keys):
            direction_radio = ttk.Radiobutton(
                self.direction_labelframe, text=i18n.t(f'gui.{key}'), variable=self.direction_var, value=self.direction_value[i])
            self.direction_radio.append(direction_radio)
            direction_radio.grid(row=i+1, column=0, sticky="nsew", padx=2, pady=1)
        
        # Create a LabelFrame for the page layout options
        self.pagelayout_labelframe = ttk.LabelFrame(pagelayout_frame, text=i18n.t('gui.page_layout'), padding=5)
        self.pagelayout_labelframe.grid(row=0, column=0, rowspan=10, sticky="nsew", padx=2, pady=1)

        self.pagelayout_var = tk.StringVar(value="TwoPageRight")
        self.pagelayout_value = ["SinglePage", "OneColumn", "TwoPageLeft", "TwoColumnLeft", "TwoPageRight", "TwoColumnRight"]
        self.pagelayout_radio = []
        for i, text in enumerate(i18n.t('gui.page_layouts')):
            pagelayout_radio = ttk.Radiobutton(
                self.pagelayout_labelframe, text=text, variable=self.pagelayout_var, value=self.pagelayout_value[i]
            )
            self.pagelayout_radio.append(pagelayout_radio)
            pagelayout_radio.grid(row=i+1, column=0, sticky="nsew", padx=2, pady=1)

        # Create a LabelFrame for the page mode options
        self.pagemode_labelframe = ttk.LabelFrame(pagemode_frame, text=i18n.t('gui.page_mode'), padding=5)
        self.pagemode_labelframe.grid(row=0, column=0, rowspan=10, sticky="nsew", padx=2, pady=1)

        self.pagemode_var = tk.StringVar(value="UseNone")
        self.pagemode_value = ["UseNone", "UseOutlines", "UseThumbs", "FullScreen", "UseOC", "UseAttachments"]
        self.pagemode_radio = []
        for i, text in enumerate(i18n.t('gui.page_modes')):
            pagemode_radio = ttk.Radiobutton(
                self.pagemode_labelframe, text=text, variable=self.pagemode_var, value=self.pagemode_value[i]
            )
            self.pagemode_radio.append(pagemode_radio)
            pagemode_radio.grid(row=i+1, column=0, sticky="nsew", padx=2, pady=1)

        # Create a LabelFrame for the metadata options
        self.metadata_labelframe = ttk.LabelFrame(metadata_frame, text=i18n.t('gui.metadata'), padding=5)
        self.metadata_labelframe.grid(row=0, column=0, columnspan=3, padx=5, pady=2, sticky="ew")

        self.title_label = ttk.Label(self.metadata_labelframe, text=i18n.t('gui.title'))
        self.title_label.grid(row=0, column=0, padx=10, pady=2, sticky="w")
        self.title_entry = ttk.Entry(self.metadata_labelframe, width=current_meta_entry_width)
        self.title_entry.grid(row=0, column=1, padx=10, pady=2, sticky="w")

        self.author_label = ttk.Label(self.metadata_labelframe, text=i18n.t('gui.author'))
        self.author_label.grid(row=1, column=0, padx=10, pady=2, sticky="w")
        self.author_entry = ttk.Entry(self.metadata_labelframe, width=current_meta_entry_width)
        self.author_entry.grid(row=1, column=1, padx=10, pady=2, sticky="w")

        self.publisher_label = ttk.Label(self.metadata_labelframe, text=i18n.t('gui.publisher'))
        self.publisher_label.grid(row=2, column=0, padx=10, pady=2, sticky="w")
        self.publisher_entry = ttk.Entry(self.metadata_labelframe, width=current_meta_entry_width)
        self.publisher_entry.grid(row=2, column=1, padx=10, pady=2, sticky="w")

        self.creation_date_label = ttk.Label(self.metadata_labelframe, text=i18n.t('gui.create_date'))
        self.creation_date_label.grid(row=3, column=0, padx=10, pady=2, sticky="w")
        creation_date_frame = ttk.Frame(self.metadata_labelframe)
        creation_date_frame.grid(row=3, column=1, columnspan=2, padx=10, pady=2, sticky="w")
        
        # Use DateEntry widget
        current_date = datetime.datetime.now()
        self.creation_date_entry = tkface.DateEntry(
            creation_date_frame,
            year=current_date.year,
            month=current_date.month,
            language="ja" if i18n.get('locale') == 'ja_JP' else "en"
        )
        self.creation_date_entry.pack(side="left")
        
        self.creation_time_combobox = self.create_time_combobox(creation_date_frame)
        self.creation_time_combobox.pack(side="left", padx=5)
        self.ctime_var = tk.BooleanVar()
        self.ctime_var.set(True)
        self.ctime_check_box = ttk.Checkbutton(creation_date_frame, text=i18n.t('gui.sync_file_timestamp'), variable=self.ctime_var)        
        self.ctime_check_box.pack(side="left", padx=5)
        if self.system not in ["Windows", "Darwin"]:
            self.ctime_check_box.configure(state=tk.DISABLED)

        self.modify_date_label = ttk.Label(self.metadata_labelframe, text=i18n.t('gui.modify_date'))
        self.modify_date_label.grid(row=4, column=0, padx=10, pady=2, sticky="w")
        modify_date_frame = ttk.Frame(self.metadata_labelframe)
        modify_date_frame.grid(row=4, column=1, columnspan=2, padx=10, pady=2, sticky="w")
        
        # Use DateEntry widget
        self.modify_date_entry = tkface.DateEntry(
            modify_date_frame,
            year=current_date.year,
            month=current_date.month,
            language="ja" if i18n.get('locale') == 'ja_JP' else "en"
        )
        self.modify_date_entry.pack(side="left")
        
        self.modify_time_combobox = self.create_time_combobox(modify_date_frame)
        self.modify_time_combobox.pack(side="left", padx=5)
        self.mtime_var = tk.BooleanVar()
        self.mtime_var.set(True)
        self.mtime_check_box = ttk.Checkbutton(modify_date_frame, text=i18n.t('gui.sync_file_timestamp'), variable=self.mtime_var)        
        self.mtime_check_box.pack(side="left", padx=5)

        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.creation_time_combobox.set(current_time)
        self.modify_time_combobox.set(current_time)

        # Add language toggle button
        self.language_label = ttk.Label(button_frame, text="Language:")
        self.language_label.pack(side="left", padx=(15, 5), pady=5)
        self.language_var = tk.StringVar()
        self.language_combobox = ttk.Combobox(button_frame, textvariable=self.language_var, state='readonly', width=12)
        
        self.language_combobox['values'] = list(self.lang_map.keys())

        current_lang_name = self.rev_lang_map.get(i18n.get('locale'), 'English')
        self.language_combobox.set(current_lang_name)
        
        self.language_combobox.pack(side="left", padx=5, pady=5)
        self.language_combobox.bind('<<ComboboxSelected>>', self.change_language)

        # Add quit button
        self.quit_button = ttk.Button(button_frame, text=i18n.t('gui.quit'), command=sys.exit)
        self.quit_button.pack(side="left", padx=15, pady=5)

        # Add convert button
        self.convert_button = ttk.Button(button_frame, text=i18n.t('gui.convert'), command=self.run_convert)
        self.convert_button.pack(side="right", padx=15, pady=5)

        # Add padding to all widgets
        for child in master.winfo_children():
            child.grid_configure(padx=10, pady=5)

        # Set minimum size of the window
        master.minsize(400, 250)

        # Center the window
        master.eval('tk::PlaceWindow . center')

    def setup_i18n(self):
        i18n.load_path.append(os.path.join(os.path.dirname(__file__), 'locales'))
        i18n.set('file_format', 'yml')
        i18n.set('filename_format', '{locale}.{format}')
        i18n.set('skip_locale_root_data', True)
        i18n.set('fallback', 'en_US')
        
        locale = 'en_US'
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                config_locale = config.get('language')
                if config_locale in self.lang_map.values():
                    locale = config_locale
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        i18n.set('locale', locale)


        
    def create_time_combobox(self, frame):
        hours = [f"{h:02d}" for h in range(24)]
        minutes = [f"{m:02d}" for m in range(60)]
        time_values = [f"{h}:{m}:00" for h in hours for m in minutes]
        time_combobox = ttk.Combobox(frame, values=time_values, width=8)
        return time_combobox

    def change_language(self, event=None):
        selected_language = self.language_var.get()
        locale = self.lang_map.get(selected_language)
        if locale and locale != i18n.get('locale'):
            i18n.set('locale', locale)
            try:
                with open('config.json', 'w') as f:
                    json.dump({'language': locale}, f)
            except IOError:
                print("Error: Could not write to config.json")
            self.update_language()

    def update_language(self):
        locale = i18n.get('locale')
        
        entry_width = self.long_entry_width if locale in self.long_languages else self.default_entry_width
        self.input_entry.configure(width=entry_width)
        self.output_entry.configure(width=entry_width)

        meta_entry_width = self.long_meta_entry_width if locale in self.long_languages else self.default_meta_entry_width
        self.title_entry.configure(width=meta_entry_width)
        self.author_entry.configure(width=meta_entry_width)
        self.publisher_entry.configure(width=meta_entry_width)
        
        # Update buttons and labels
        self.input_label.configure(text=i18n.t('gui.input_path'))
        self.input_file_button.configure(text=i18n.t('gui.select_file'))
        self.input_directory_button.configure(text=i18n.t('gui.select_directory'))
        self.output_label.configure(text=i18n.t('gui.output_path'))
        self.output_browse_button.configure(text=i18n.t('gui.browse'))
        self.auto_output_button.configure(text=i18n.t('gui.auto'))
        
        # Update conversion options
        self.conversion_labelframe.configure(text=i18n.t('gui.conversion_options'))
        for i, key in enumerate(self.conversion_text_keys):
            self.conversion_radio[i].configure(text=i18n.t(f'gui.{key}'))
        
        # Update direction options
        self.direction_labelframe.configure(text=i18n.t('gui.direction'))
        for i, key in enumerate(self.direction_text_keys):
            self.direction_radio[i].configure(text=i18n.t(f'gui.{key}'))

        # Update page layout options
        self.pagelayout_labelframe.configure(text=i18n.t('gui.page_layout'))
        for i, text in enumerate(i18n.t('gui.page_layouts')):
            self.pagelayout_radio[i].configure(text=text)

        # Update page mode options
        self.pagemode_labelframe.configure(text=i18n.t('gui.page_mode'))
        for i, text in enumerate(i18n.t('gui.page_modes')):
            self.pagemode_radio[i].configure(text=text)

        # Update metadata labels
        self.metadata_labelframe.configure(text=i18n.t('gui.metadata'))
        self.title_label.configure(text=i18n.t('gui.title'))
        self.author_label.configure(text=i18n.t('gui.author'))
        self.publisher_label.configure(text=i18n.t('gui.publisher'))
        self.creation_date_label.configure(text=i18n.t('gui.create_date'))
        self.ctime_check_box.configure(text=i18n.t('gui.sync_file_timestamp'))
        self.modify_date_label.configure(text=i18n.t('gui.modify_date'))
        self.mtime_check_box.configure(text=i18n.t('gui.sync_file_timestamp'))

        # Update main buttons
        self.language_label.configure(text=i18n.t('gui.language'))
        self.convert_button.configure(text=i18n.t('gui.convert'))
        self.quit_button.configure(text=i18n.t('gui.quit'))

    def set_output_path(self, path):
        self.output_path = path
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, path)

    def browse_output_path(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if path:
            self.set_output_path(path)

    def browse_input_file(self):
        filetypes = (
            ("zip files", "*.zip"),
            ("cbz files", "*.cbz"),
            ("rar files", "*.rar"),
            ("cbr files", "*.cbr"),
            ("7z files", "*.7z"),
            ("cb7 files", "*.cb7"),
            ("tar files", "*.tar"),
            ("cbt files", "*.cbt"),
            ("epub files", "*.epub"),
            ("all files", "*.*"),
        )
        path = filedialog.askopenfilename(filetypes=filetypes)

        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.publisher_entry.delete(0, tk.END)
        current_date = datetime.datetime.now()
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        # DateEntryは自動的に現在の日付が設定されるので、時間のみ設定
        self.creation_time_combobox.set(current_time)
        self.modify_time_combobox.set(current_time)

        if path:
            self.input_path = path.replace('/', os.sep)
            self.set_output_path(os.path.splitext(path)[0] + ".pdf")
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)

            converter = MangaPdfConverter(input_path=self.input_path, output_path=self.output_path, pagelayout=self.pagelayout_var.get(), pagemode=self.pagemode_var.get(), direction=self.direction_var.get())
            if converter.is_epub_file(self.input_path):
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
                        # EPUBの日付をDateEntryに設定
                        try:
                            epub_date = datetime.datetime.strptime(epub_metadata['date'], "%Y-%m-%d")
                            self.creation_date_entry.set_selected_date(epub_date.date())
                        except (ValueError, AttributeError):
                            # 日付形式が異なる場合やDateEntryが初期化されていない場合は無視
                            pass
            #print(pdf_metadata)

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
            tkface.messagebox.showerror(master=self.master, message=i18n.t('gui.error_no_input_path'), title=i18n.t('gui.error'))
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
                tkface.messagebox.showerror(master=self.master, message=i18n.t('gui.error_output_not_pdf'), title=i18n.t('gui.error'))
                return

        # Set the output path and filename
        self.output_path = output_path

    def set_metadata(self, output_path):
        with pikepdf.Pdf.open(output_path, allow_overwriting_input=True) as pdf:
            with pdf.open_metadata(set_pikepdf_as_editor=False) as pdf_metadata:
                pdf_metadata['dc:title'] = self.title_entry.get() if self.title_entry.get() else ''
                pdf_metadata['dc:creator'] = [self.author_entry.get() if self.author_entry.get() else '']
                pdf_metadata['dc:publisher'] = self.publisher_entry.get() if self.publisher_entry.get() else ''
                creation_date_obj = self.creation_date_entry.get_date()
                if creation_date_obj is None:
                    creation_date_obj = datetime.datetime.now().date()
                creation_date = creation_date_obj.strftime("%Y-%m-%d")
                modify_date_obj = self.modify_date_entry.get_date()
                if modify_date_obj is None:
                    modify_date_obj = datetime.datetime.now().date()
                modify_date = modify_date_obj.strftime("%Y-%m-%d")
                pdf_metadata['xmp:CreateDate'] = f"{creation_date} {self.creation_time_combobox.get()}"
                pdf_metadata['xmp:ModifyDate'] = f"{modify_date} {self.modify_time_combobox.get()}"
                pdf_metadata['pdf:Producer'] = ''
            pdf.save(output_path, linearize=True)

    def set_timestamp(self, output_path):
        if self.ctime_var.get():
           if self.system == "Windows":
                import win32_setctime
                creation_date_obj = self.creation_date_entry.get_date()
                if creation_date_obj is None:
                    creation_date_obj = datetime.datetime.now().date()
                creation_date = creation_date_obj.strftime("%Y-%m-%d")
                ctime_new = datetime.datetime.strptime(f"{creation_date} {self.creation_time_combobox.get()}", "%Y-%m-%d %H:%M:%S")
                win32_setctime.setctime(output_path, ctime_new.timestamp())
           elif self.system == "Darwin":
                creation_date_obj = self.creation_date_entry.get_date()
                if creation_date_obj is None:
                    creation_date_obj = datetime.datetime.now().date()
                creation_date = creation_date_obj.strftime("%Y-%m-%d")
                date_object = datetime.datetime.strptime(creation_date, "%Y-%m-%d")
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

        modify_date_obj = self.modify_date_entry.get_date()
        if modify_date_obj is None:
            modify_date_obj = datetime.datetime.now().date()
        modify_date = modify_date_obj.strftime("%Y-%m-%d")
        mtime_new = datetime.datetime.strptime(f"{modify_date} {self.modify_time_combobox.get()}", "%Y-%m-%d %H:%M:%S")
        if self.mtime_var.get():
            os.utime(path=output_path, times=(mtime_new.timestamp(), mtime_new.timestamp()))

    def run_convert(self):
        # Get input and output paths
        input_path = self.input_entry.get()
        output_path = self.output_entry.get()

        # Check if input path is empty
        if not input_path:
            tkface.messagebox.showerror(master=self.master, message=i18n.t('gui.please_specify_input'), title=i18n.t('gui.error'))
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
            tkface.messagebox.showerror(master=self.master, message=i18n.t('gui.please_specify_output'), title=i18n.t('gui.error'))
            return
        
        # Determine the conversion options
        convert_to_jpeg = self.conversion_var.get() == "jpeg"
        convert_to_grayscale = self.conversion_var.get() == "grayscale"

        # Call MangaPdfConverter with the appropriate arguments
        try:
            converter = MangaPdfConverter(input_path=input_path, output_path=output_path, pagelayout=self.pagelayout_var.get(), pagemode=self.pagemode_var.get(), direction=self.direction_var.get())

            # Ask user if they want to convert
            answer = tkface.messagebox.askyesno(master=self.master, message=i18n.t('gui.are_you_sure'), title=i18n.t('gui.confirm_conversion'))

            if not answer:
                tkface.messagebox.showinfo(master=self.master, message=i18n.t('gui.conversion_canceled'), title=i18n.t('gui.conversion'))
                return
            
            # Create "Processing..." window
            processing_window = tk.Toplevel(self.master)
            # Get the position and size of the parent window
            main_x, main_y = self.master.winfo_x(), self.master.winfo_y()
            main_width, main_height = self.master.winfo_width(), self.master.winfo_height()
            # Calculate the position of the processing window
            if self.system == "Windows":
                sub_width, sub_height = 350, 80
            else:
                sub_width, sub_height = 250, 30
            sub_x = main_x + (main_width - sub_width) // 2
            sub_y = main_y + (main_height - sub_height) // 2
            processing_window.geometry(f"{sub_width}x{sub_height}+{sub_x}+{sub_y}")
            # Set the title of the window
            processing_window.title(f"Manga PDF Converter v{__version__}")
            # Set the parent of the processing window
            processing_window.transient(self.master)
            # Add widgets to the frame
            processing_label = tk.Label(processing_window, text=i18n.t('gui.processing'), anchor='center')
            processing_label.pack(expand=True, fill='both')

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
            if "processing_window" in locals(): processing_window.grab_release()
            if "processing_window" in locals(): processing_window.destroy()

            # Re-enable main window
            #self.master.deiconify()

            # Check if output file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                tkface.messagebox.showinfo(master=self.master, message=i18n.t('gui.conversion_complete'), title=i18n.t('gui.success'))
            else:
                tkface.messagebox.showerror(master=self.master, message=i18n.t('gui.conversion_failed'), title=i18n.t('gui.error'))

        except Exception as e:
            # Close process window when done
            if "processing_window" in locals(): processing_window.grab_release()
            if "processing_window" in locals(): processing_window.destroy()
            tkface.messagebox.showerror(title=i18n.t('gui.error'), message=f"{i18n.t('gui.conversion_failed_with_error')}\n{str(e)}", master=self.master)

            # Re-enable main window
            self.master.deiconify()

def launch_gui():
    root = tk.Tk()
    MangaPdfConverterGUI(root)
    root.mainloop()

if __name__ == '__main__':
    launch_gui()