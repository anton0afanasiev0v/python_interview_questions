import sys
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTreeWidget, QTreeWidgetItem, QTextEdit, 
                             QPushButton, QFileDialog, QMessageBox, QSplitter,
                             QLabel, QLineEdit, QToolBar, QAction, QMenu, QMenuBar,
                             QProgressBar)
from PyQt5.QtCore import Qt, QMimeData, QTimer
from PyQt5.QtGui import QFont, QIcon, QKeySequence

class MarkdownQAEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.setWindowTitle("Markdown QA Editor")
        self.setGeometry(100, 100, 1200, 800)
        
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
        right_layout.addWidget(self.question_edit)
        
        # Редактор содержимого
        right_layout.addWidget(QLabel("Содержимое:"))
        self.content_edit = QTextEdit()
        self.content_edit.setFont(QFont("Arial", 10))
        right_layout.addWidget(self.content_edit)
        
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

    def new_file(self):
        self.tree_widget.clear()
        self.current_file = None
        self.statusBar().showMessage("Создан новый файл")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть Markdown файл", "", "Markdown Files (*.md)"
        )
        
        if file_path:
            try:
                # Показываем прогресс-бар
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                QApplication.processEvents()  # Обновляем GUI
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Используем таймер для асинхронной загрузки
                QTimer.singleShot(100, lambda: self.load_content_async(content, file_path))
                
            except Exception as e:
                self.progress_bar.setVisible(False)
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def load_content_async(self, content, file_path):
        """Асинхронная загрузка контента"""
        try:
            self.parse_markdown(content)
            self.current_file = file_path
            self.statusBar().showMessage(f"Загружен файл: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при разборе файла: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)

    def save_file(self):
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить Markdown файл", "", "Markdown Files (*.md)"
        )
        
        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            self.statusBar().showMessage(f"Файл сохранен: {file_path}")

    def save_to_file(self, file_path):
        try:
            markdown_content = self.generate_markdown()
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(markdown_content)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")
    

    def parse_markdown(self, content):
        """Улучшенный парсинг Markdown с распознаванием тем"""
        self.tree_widget.clear()
        
        # Разбиваем на строки и фильтруем пустые
        lines = [line for line in content.split('\n') if line.strip()]
        
        stack = []  # Стек для отслеживания вложенности
        current_topic = None
        i = 0
        inside_details = False  # Флаг - находимся ли внутри блока details
        
        # Обновляем прогресс-бар
        total_lines = len(lines)
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Обновляем прогресс
            if i % 10 == 0:
                progress = int((i / total_lines) * 100)
                self.progress_bar.setValue(progress)
                QApplication.processEvents()
            
            # Игнорируем все внутри блоков details (кроме закрывающих тегов)
            if inside_details and not line.startswith('</details>'):
                # Добавляем контент к текущему вопросу
                if (stack and 
                    stack[-1].data(0, Qt.UserRole)["type"] == "question" and 
                    line and 
                    not line.startswith('<') and 
                    line != '</details>'):
                    
                    item_data = stack[-1].data(0, Qt.UserRole)
                    if item_data and line.strip():
                        content_data = item_data.get("content", [])
                        content_data.append(lines[i])
                        item_data["content"] = content_data
                        stack[-1].setData(0, Qt.UserRole, item_data)
                
                i += 1
                continue
            
            # Распознавание заголовков тем (только если не внутри details)
            if not stack and line.startswith('#') and not line.startswith('<details'):
                level = len(line) - len(line.lstrip('#'))
                topic_text = line.lstrip('#').strip()
                
                if topic_text:
                    # Закрываем предыдущую тему если есть
                    while stack and stack[-1].data(0, Qt.UserRole)["type"] == "topic":
                        stack.pop()
                    
                    # Создаем новую тему
                    current_topic = QTreeWidgetItem([f"📁 {topic_text}"])
                    current_topic.setData(0, Qt.UserRole, {
                        "type": "topic", 
                        "level": level,
                        "content": []
                    })
                    self.tree_widget.addTopLevelItem(current_topic)
                    stack.append(current_topic)
            
            # Ищем открывающий тег <details>
            elif line.startswith('<details>'):
                inside_details = True  # Входим в блок details
                
                # Извлекаем вопрос из тега <summary>
                question_match = re.search(r'<summary>(.*?)</summary>', line)
                if question_match:
                    question = question_match.group(1).strip()
                    item = QTreeWidgetItem([f"❓ {question}"])
                    item.setData(0, Qt.UserRole, {
                        "type": "question", 
                        "content": []
                    })
                    
                    # Добавляем к текущей теме или создаем общую
                    if stack and stack[-1].data(0, Qt.UserRole)["type"] == "topic":
                        stack[-1].addChild(item)
                    else:
                        # Создаем общую тему для вопросов без категории
                        general_topic = None
                        for j in range(self.tree_widget.topLevelItemCount()):
                            if self.tree_widget.topLevelItem(j).text(0) == "📁 Общие вопросы":
                                general_topic = self.tree_widget.topLevelItem(j)
                                break
                        
                        if not general_topic:
                            general_topic = QTreeWidgetItem(["📁 Общие вопросы"])
                            general_topic.setData(0, Qt.UserRole, {
                                "type": "topic", 
                                "level": 1,
                                "content": []
                            })
                            self.tree_widget.addTopLevelItem(general_topic)
                        
                        general_topic.addChild(item)
                        if general_topic not in stack:
                            stack.append(general_topic)
                    
                    stack.append(item)
            
            # Закрытие </details>
            elif line == '</details>':
                inside_details = False  # Выходим из блока details
                if stack and stack[-1].data(0, Qt.UserRole)["type"] == "question":
                    stack.pop()
            
            # Обработка конца темы (при встрече новой темы или конца файла)
            elif (stack and 
                stack[-1].data(0, Qt.UserRole)["type"] == "topic" and
                (i == len(lines) - 1 or 
                (lines[i].startswith('#') and not lines[i].startswith('<details')))):
                
                # Проверяем уровень вложенности для правильного закрытия тем
                if i < len(lines) - 1 and lines[i].startswith('#'):
                    next_level = len(lines[i]) - len(lines[i].lstrip('#'))
                    current_level = stack[-1].data(0, Qt.UserRole)["level"]
                    
                    # Если следующая тема того же или более высокого уровня, закрываем текущую
                    if next_level <= current_level:
                        stack.pop()
            
            i += 1
        
        # Завершаем прогресс-бар
        self.progress_bar.setValue(100)
        QApplication.processEvents()
        
        # Разворачиваем все элементы для лучшего обзора
        self.tree_widget.expandAll()

    def display_content(self, item, column):
        """Отображение содержимого выбранного элемента"""
        if not item:
            return
        
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return
        
        content_text = ""
        
        if item_data["type"] == "topic":
            content_text = f"# {item.text(0).replace('📁 ', '')}\n\n"
            content_text += "Эта тема содержит следующие вопросы:\n"
            for i in range(item.childCount()):
                child = item.child(i)
                content_text += f"• {child.text(0).replace('❓ ', '')}\n"
        
        elif item_data["type"] == "question":
            content_lines = item_data.get("content", [])
            content_text = f"# {item.text(0).replace('❓ ', '')}\n\n"
            content_text += "\n".join(content_lines)
        
        self.content_display.setMarkdown(content_text)


    def generate_markdown(self):
        def generate_item_markdown(item, level=0):
            markdown = []
            question = item.text(0)
            content = item.data(0, Qt.UserRole) or []
            
            # Открывающий тег details
            markdown.append("<details>")
            markdown.append(f"<summary>{question}</summary>")
            
            # Добавляем пустую строку после summary, если есть содержимое
            if content:
                markdown.append("")
            
            # Содержимое
            for line in content:
                markdown.append(line)
            
            # Добавляем пустую строку перед дочерними элементами, если они есть
            if item.childCount() > 0:
                if content:  # Если было содержимое, добавляем дополнительную пустую строку
                    markdown.append("")
                markdown.append("")
            
            # Рекурсивно обрабатываем дочерние элементы
            for i in range(item.childCount()):
                child = item.child(i)
                markdown.extend(generate_item_markdown(child, level + 1))
            
            # Закрывающий тег
            markdown.append("</details>")
            
            return markdown
        
        markdown_lines = []
        
        # Обрабатываем корневые элементы
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            markdown_lines.extend(generate_item_markdown(item))
            if i < self.tree_widget.topLevelItemCount() - 1:  # Добавляем пустую строку между элементами
                markdown_lines.append("")
        
        return '\n'.join(markdown_lines)

    def on_item_selected(self):
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            self.current_item = selected_items[0]
            self.question_edit.setText(self.current_item.text(0))
            
            content = self.current_item.data(0, Qt.UserRole) or []
            self.content_edit.setPlainText('\n'.join(content))
        else:
            self.current_item = None
            self.question_edit.clear()
            self.content_edit.clear()

    def save_current_item(self):
        if self.current_item:
            self.current_item.setText(0, self.question_edit.text())
            
            content = self.content_edit.toPlainText().split('\n')
            self.current_item.setData(0, Qt.UserRole, content)
            
            self.statusBar().showMessage("Изменения сохранены")

    def add_child_item(self):
        if self.current_item:
            new_item = QTreeWidgetItem(["Новый вопрос"])
            new_item.setData(0, Qt.UserRole, [])
            self.current_item.addChild(new_item)
            self.current_item.setExpanded(True)
            self.tree_widget.setCurrentItem(new_item)
            self.question_edit.setFocus()

    def add_sibling_item(self):
        parent = self.current_item.parent() if self.current_item else None
        new_item = QTreeWidgetItem(["Новый вопрос"])
        new_item.setData(0, Qt.UserRole, [])
        
        if parent:
            parent.addChild(new_item)
        else:
            self.tree_widget.addTopLevelItem(new_item)
        
        self.tree_widget.setCurrentItem(new_item)
        self.question_edit.setFocus()

    def delete_current_item(self):
        if self.current_item:
            parent = self.current_item.parent()
            if parent:
                parent.removeChild(self.current_item)
            else:
                index = self.tree_widget.indexOfTopLevelItem(self.current_item)
                self.tree_widget.takeTopLevelItem(index)
            
            self.current_item = None
            self.question_edit.clear()
            self.content_edit.clear()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown QA Editor")
    
    window = MarkdownQAEditor()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()