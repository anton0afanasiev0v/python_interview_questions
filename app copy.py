import sys
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTreeWidget, QTreeWidgetItem, QTextEdit, 
                             QPushButton, QFileDialog, QMessageBox, QSplitter,
                             QLabel, QLineEdit, QToolBar, QAction, QMenu, QMenuBar,
                             QProgressBar, QComboBox, QTabWidget)
from PyQt5.QtCore import Qt, QMimeData, QTimer
from PyQt5.QtGui import QFont, QIcon, QKeySequence, QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown

class MarkdownQAEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.dark_theme = True  # По умолчанию темная тема
        self.setWindowTitle("Markdown QA Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Применяем темную тему
        self.apply_dark_theme()
        
        # Инициализируем tree_widget ДО создания меню
        self.tree_widget = QTreeWidget()
        
        # Создаем центральный виджет и основной layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Создаем меню (теперь tree_widget уже инициализирован)
        self.create_menus()
        
        # Создаем панель инструментов
        self.create_toolbar()
        
        # Настраиваем tree_widget
        self.tree_widget.setHeaderLabel("Вопросы")
        self.tree_widget.setDragDropMode(QTreeWidget.InternalMove)
        self.tree_widget.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setAcceptDrops(True)
        self.tree_widget.setDropIndicatorShown(True)
        self.tree_widget.itemSelectionChanged.connect(self.on_item_selected)
        
        # Настраиваем стиль tree_widget для темной темы
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3a3a3a;
            }
            QTreeWidget::item:selected {
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #3a3a3a;
            }
        """)
        
        # Создаем сплиттер для разделения дерева и редактора
        splitter = QSplitter(Qt.Horizontal)
        
        # Правая панель - редактор
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Заголовок редактора
        self.editor_title = QLabel("Редактор вопроса/ответа")
        self.editor_title.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(self.editor_title)
        
        # Поле для заголовка вопроса
        right_layout.addWidget(QLabel("Заголовок вопроса:"))
        self.question_edit = QLineEdit()
        self.question_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        right_layout.addWidget(self.question_edit)
        
        # Выбор типа контента
        right_layout.addWidget(QLabel("Тип контента:"))
        self.content_type_combo = QComboBox()
        self.content_type_combo.addItems(["question", "answer", "topic"])
        self.content_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
            }
        """)
        right_layout.addWidget(self.content_type_combo)
        
        # Создаем вкладки для содержимого
        right_layout.addWidget(QLabel("Содержимое:"))
        self.content_tabs = QTabWidget()
        
        # Вкладка редактирования
        self.content_edit = QTextEdit()
        self.content_edit.setFont(QFont("Consolas", 10))
        self.content_edit.textChanged.connect(self.update_preview)
        self.content_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #555555;
                border-radius: 5px;
                font-family: Consolas, monospace;
            }
        """)
        
        # Вкладка предпросмотра
        self.preview_view = QWebEngineView()
        self.preview_view.setHtml(self.get_dark_preview_html("<p>Предпросмотр будет отображаться здесь...</p>"))
        
        self.content_tabs.addTab(self.content_edit, "Редактирование")
        self.content_tabs.addTab(self.preview_view, "Предпросмотр")
        
        # Стиль для вкладок
        self.content_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #555555;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3a3a3a;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #3a3a3a;
            }
        """)
        
        right_layout.addWidget(self.content_tabs)
        
        # Кнопки для редактора
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить изменения")
        self.save_button.clicked.connect(self.save_current_item)
        self.add_child_button = QPushButton("Добавить подвопрос")
        self.add_child_button.clicked.connect(self.add_child_item)
        self.add_sibling_button = QPushButton("Добавить вопрос")
        self.add_sibling_button.clicked.connect(self.add_sibling_item)
        self.delete_button = QPushButton("Удалить вопрос")
        self.delete_button.clicked.connect(self.delete_current_item)
        
        # Стиль для кнопок
        button_style = """
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
            QPushButton:disabled {
                background-color: #2b2b2b;
                color: #777777;
            }
        """
        
        self.save_button.setStyleSheet(button_style)
        self.add_child_button.setStyleSheet(button_style)
        self.add_sibling_button.setStyleSheet(button_style)
        self.delete_button.setStyleSheet(button_style)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.add_child_button)
        button_layout.addWidget(self.add_sibling_button)
        button_layout.addWidget(self.delete_button)
        right_layout.addLayout(button_layout)
        
        # Добавляем панели в сплиттер
        splitter.addWidget(self.tree_widget)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        
        # Статус бар
        self.statusBar().showMessage("Готов к работе")
        
        # Текущий выбранный элемент
        self.current_item = None

    def apply_dark_theme(self):
        """Применение темной темы ко всему приложению"""
        dark_palette = QPalette()
        
        # Базовые цвета
        dark_palette.setColor(QPalette.Window, QColor(43, 43, 43))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        # Отключенные элементы
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
        
        QApplication.setPalette(dark_palette)
        
        # Дополнительные стили
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMenuBar {
                background-color: #2b2b2b;
                color: #ffffff;
                border-bottom: 1px solid #555555;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #3a3a3a;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QMenu::item {
                padding: 4px 16px;
            }
            QMenu::item:selected {
                background-color: #3a3a3a;
            }
            QToolBar {
                background-color: #2b2b2b;
                border: 1px solid #555555;
                spacing: 3px;
                padding: 2px;
            }
            QStatusBar {
                background-color: #2b2b2b;
                color: #ffffff;
                border-top: 1px solid #555555;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
            QSplitter::handle {
                background-color: #555555;
            }
            QSplitter::handle:hover {
                background-color: #777777;
            }
            QLabel {
                color: #ffffff;
            }
        """)

    def get_dark_preview_html(self, html_content):
        """Генерация HTML для темного предпросмотра"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #d4d4d4;
                    background-color: #1e1e1e;
                    max-width: 100%;
                    padding: 20px;
                    margin: 0;
                }}
                pre {{
                    background-color: #2d2d2d;
                    color: #d4d4d4;
                    padding: 12px;
                    border-radius: 5px;
                    overflow-x: auto;
                    border: 1px solid #404040;
                }}
                code {{
                    background-color: #2d2d2d;
                    color: #d4d4d4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Cascadia Code', 'Consolas', monospace;
                    font-size: 0.9em;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                blockquote {{
                    border-left: 4px solid #404040;
                    margin: 15px 0;
                    padding-left: 15px;
                    color: #a0a0a0;
                    font-style: italic;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                    background-color: #2b2b2b;
                }}
                th, td {{
                    border: 1px solid #404040;
                    padding: 10px;
                    text-align: left;
                }}
                th {{
                    background-color: #363636;
                    color: #ffffff;
                    font-weight: bold;
                }}
                td {{
                    color: #d4d4d4;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #ffffff;
                    margin-top: 20px;
                    margin-bottom: 10px;
                    border-bottom: 1px solid #404040;
                    padding-bottom: 5px;
                }}
                h1 {{ color: #569cd6; }}
                h2 {{ color: #4ec9b0; }}
                h3 {{ color: #c586c0; }}
                h4 {{ color: #dcdcaa; }}
                h5 {{ color: #9cdcfe; }}
                h6 {{ color: #ce9178; }}
                
                a {{
                    color: #569cd6;
                    text-decoration: none;
                }}
                a:hover {{
                    color: #4ec9b0;
                    text-decoration: underline;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 3px;
                    border: 1px solid #404040;
                }}
                ul, ol {{
                    color: #d4d4d4;
                    padding-left: 20px;
                }}
                li {{
                    margin: 5px 0;
                }}
                hr {{
                    border: none;
                    border-top: 2px solid #404040;
                    margin: 20px 0;
                }}
                strong, b {{
                    color: #ffffff;
                }}
                em, i {{
                    color: #dcdcaa;
                }}
                
                /* Синтаксис для кода */
                .hljs {{
                    background: #1e1e1e;
                    color: #d4d4d4;
                }}
                .hljs-keyword {{ color: #569cd6; }}
                .hljs-string {{ color: #ce9178; }}
                .hljs-comment {{ color: #6a9955; }}
                .hljs-function {{ color: #dcdcaa; }}
                .hljs-number {{ color: #b5cea8; }}
                .hljs-params {{ color: #9cdcfe; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

    def update_preview(self):
        """Обновление предпросмотра Markdown"""
        markdown_text = self.content_edit.toPlainText()
        
        # Используем расширения для лучшей поддержки Markdown
        html_content = markdown.markdown(
            markdown_text, 
            extensions=['extra', 'codehilite', 'tables', 'toc']
        )
        
        self.preview_view.setHtml(self.get_dark_preview_html(html_content))

    def create_menus(self):
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu('Файл')
        
        new_action = QAction('Новый', self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('Открыть', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('Сохранить', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('Сохранить как...', self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Правка
        edit_menu = menubar.addMenu('Правка')
        
        expand_all_action = QAction('Развернуть все', self)
        expand_all_action.triggered.connect(self.tree_widget.expandAll)
        edit_menu.addAction(expand_all_action)
        
        collapse_all_action = QAction('Свернуть все', self)
        collapse_all_action.triggered.connect(self.tree_widget.collapseAll)
        edit_menu.addAction(collapse_all_action)

        # Меню Вид
        view_menu = menubar.addMenu('Вид')
        
        preview_action = QAction('Предпросмотр', self)
        preview_action.setShortcut('F5')
        preview_action.triggered.connect(lambda: self.content_tabs.setCurrentIndex(1))
        view_menu.addAction(preview_action)
        
        edit_action = QAction('Редактирование', self)
        edit_action.setShortcut('F4')
        edit_action.triggered.connect(lambda: self.content_tabs.setCurrentIndex(0))
        view_menu.addAction(edit_action)
        
        view_menu.addSeparator()
        
        # Переключение темы
        self.theme_action = QAction('Светлая тема', self)
        self.theme_action.setShortcut('F2')
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)

    def toggle_theme(self):
        """Переключение между темной и светлой темой"""
        self.dark_theme = not self.dark_theme
        
        if self.dark_theme:
            self.apply_dark_theme()
            self.theme_action.setText('Светлая тема')
            self.update_preview()  # Обновляем предпросмотр для темной темы
        else:
            QApplication.setPalette(QApplication.style().standardPalette())
            self.setStyleSheet("")
            self.theme_action.setText('Темная тема')
            # Сброс стилей виджетов для светлой темы
            self.tree_widget.setStyleSheet("")
            self.question_edit.setStyleSheet("")
            self.content_type_combo.setStyleSheet("")
            self.content_edit.setStyleSheet("")
            self.content_tabs.setStyleSheet("")
            self.save_button.setStyleSheet("")
            self.add_child_button.setStyleSheet("")
            self.add_sibling_button.setStyleSheet("")
            self.delete_button.setStyleSheet("")
            
            # Обновляем предпросмотр для светлой темы
            markdown_text = self.content_edit.toPlainText()
            html_content = markdown.markdown(
                markdown_text, 
                extensions=['extra', 'codehilite', 'tables', 'toc']
            )
            # Используем стандартный светлый стиль
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 100%;
                        padding: 20px;
                        background-color: #ffffff;
                    }}
                    pre {{
                        background-color: #f4f4f4;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                    code {{
                        background-color: #f4f4f4;
                        padding: 2px 4px;
                        border-radius: 3px;
                        font-family: 'Courier New', monospace;
                    }}
                    pre code {{
                        background-color: transparent;
                        padding: 0;
                    }}
                    blockquote {{
                        border-left: 4px solid #ddd;
                        margin: 10px 0;
                        padding-left: 15px;
                        color: #666;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 10px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        color: #2c3e50;
                        margin-top: 20px;
                        margin-bottom: 10px;
                    }}
                    a {{
                        color: #3498db;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            self.preview_view.setHtml(styled_html)

    def create_toolbar(self):
        toolbar = self.addToolBar('Основные')
        
        new_action = QAction('Новый', self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction('Открыть', self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction('Сохранить', self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        preview_action = QAction('Предпросмотр', self)
        preview_action.triggered.connect(lambda: self.content_tabs.setCurrentIndex(1))
        toolbar.addAction(preview_action)