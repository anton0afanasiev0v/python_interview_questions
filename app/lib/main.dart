import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:file_picker/file_picker.dart';
import 'package:csv/csv.dart';
import 'dart:convert';
import 'dart:io';

import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'database/database_helper.dart';
import 'models/qa_model.dart';
import 'models/topic_model.dart';

void main() {
  if (Platform.isWindows || Platform.isLinux || Platform.isMacOS) {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  }
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Q&A Manager',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const QAListScreen(),
    );
  }
}

class QAListScreen extends StatefulWidget {
  const QAListScreen({super.key});

  @override
  State<QAListScreen> createState() => _QAListScreenState();
}

class _QAListScreenState extends State<QAListScreen> {
  final DatabaseHelper _dbHelper = DatabaseHelper.instance;
  List<Topic> _topics = [];
  List<QA> _qaItems = [];
  bool _isLoading = false;
  Topic? _selectedTopic;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    _topics = await _dbHelper.getAllTopics();
    if (_selectedTopic != null) {
      _qaItems = await _dbHelper.getAllQA(topicId: _selectedTopic!.id);
    } else {
      _qaItems = await _dbHelper.getAllQA();
    }
    setState(() => _isLoading = false);
  }

  Future<void> _importCSV() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['csv'],
      withData: true,
    );
    if (result == null) return;
    setState(() => _isLoading = true);
    try {
      final csv = utf8.decode(result.files.first.bytes!);
      await _dbHelper.importFromCSV(csv);
      await _loadData();
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('CSV импортирован')));
    } catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Ошибка импорта: $e')));
    }
    setState(() => _isLoading = false);
  }

  Future<void> _exportCSV() async {
    try {
      setState(() => _isLoading = true);
      final csv = await _dbHelper.exportToCSV(topicId: _selectedTopic?.id); // Исправлено на exportToCSV
      final fileName =
          'qa_export${_selectedTopic == null ? '' : '_${_selectedTopic!.name.replaceAll(RegExp(r'[^\w]'), '_')}'}.csv';
      final path = await FilePicker.platform.saveFile(
        fileName: fileName,
        allowedExtensions: ['csv'],
      );
      if (path == null) return;
      await File(path).writeAsString(csv);
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('CSV экспортирован')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Ошибка экспорта: $e')));
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _clearDatabase() async {
    setState(() => _isLoading = true);
    await _dbHelper.clearAllQA();
    await _loadData();
    setState(() => _isLoading = false);
  }

  Future<void> _addQAManually() async {
    final questionCtrl = TextEditingController();
    final answerCtrl = TextEditingController();
    final topicCtrl = TextEditingController();
    await showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Добавить вопрос'),
        content: SingleChildScrollView(
          child: Column(
            children: [
              TextField(
                controller: questionCtrl,
                decoration: const InputDecoration(labelText: 'Вопрос'),
              ),
              TextField(
                controller: answerCtrl,
                maxLines: 5,
                decoration: const InputDecoration(labelText: 'Ответ'),
              ),
              TextField(
                controller: topicCtrl,
                decoration: const InputDecoration(labelText: 'Тема (необязательно)'),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Отмена'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (questionCtrl.text.trim().isEmpty ||
                  answerCtrl.text.trim().isEmpty) return;
              int? topicId;
              if (topicCtrl.text.trim().isNotEmpty) {
                topicId = await _dbHelper
                    .insertTopic(Topic(name: topicCtrl.text.trim()));
              }
              await _dbHelper.insertQA(
                QA(
                  question: questionCtrl.text.trim(),
                  answer: answerCtrl.text.trim(),
                  topicId: topicId,
                ),
              );
              Navigator.pop(context);
              await _loadData();
            },
            child: const Text('Добавить'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Вопросы и ответы'),
        actions: [
          PopupMenuButton<Topic?>(
            icon: const Icon(Icons.filter_list),
            onSelected: (t) {
              _selectedTopic = t;
              _loadData();
            },
            itemBuilder: (_) => [
              const PopupMenuItem<Topic?>(
                value: null,
                child: Text('Все темы'),
              ),
              ..._topics.map(
                (t) => PopupMenuItem<Topic?>(
                  value: t,
                  child: Text(t.name),
                ),
              ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.download),
            tooltip: 'Экспорт CSV',
            onPressed: _isLoading ? null : _exportCSV,
          ),
          IconButton(
            icon: const Icon(Icons.upload_file),
            tooltip: 'Импорт CSV',
            onPressed: _isLoading ? null : _importCSV,
          ),
          IconButton(
            icon: const Icon(Icons.delete),
            tooltip: 'Очистить БД',
            onPressed: _isLoading ? null : _clearDatabase,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _isLoading ? null : _addQAManually,
        child: const Icon(Icons.add),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_qaItems.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.inbox, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('Нет данных'),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              icon: const Icon(Icons.upload),
              label: const Text('Импортировать CSV'),
              onPressed: _importCSV,
            ),
          ],
        ),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.only(bottom: 80),
      itemCount: _qaItems.length,
      itemBuilder: (_, i) {
        final qa = _qaItems[i];
        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Card(
            elevation: 2,
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ExpansionTile(
              tilePadding: const EdgeInsets.symmetric(horizontal: 16),
              title: Row(
                children: [
                  Expanded(
                    child: Text(
                      qa.question,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.edit, size: 20),
                    onPressed: () => _editQA(qa),
                  ),
                ],
              ),
              children: [
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: MarkdownBody(
                    data: qa.answer,
                    styleSheet: MarkdownStyleSheet(
                      p: const TextStyle(fontSize: 16, height: 1.5),
                      code: TextStyle(
                        backgroundColor: Colors.grey[200],
                        fontFamily: 'monospace',
                        fontSize: 14,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _editQA(QA qa) async {
    final questionCtrl = TextEditingController(text: qa.question);
    final answerCtrl = TextEditingController(text: qa.answer);
    final topicCtrl = TextEditingController(
      text: qa.topicId == null
          ? ''
          : (await _dbHelper.getTopic(qa.topicId!))?.name ?? '',
    );

    // Переход на полноэкранный редактор
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => QAEditScreen(
          qa: qa,
          questionController: questionCtrl,
          answerController: answerCtrl,
          topicController: topicCtrl,
          onSave: (updatedQA) async {
            final db = await _dbHelper.database;
            await db.update(
              'qa_items',
              updatedQA.toMap(),
              where: 'id = ?',
              whereArgs: [qa.id],
            );
            await _loadData();
          },
        ),
      ),
    );
  }
}

// Новый полноэкранный экран редактирования
class QAEditScreen extends StatefulWidget {
  final QA qa;
  final TextEditingController questionController;
  final TextEditingController answerController;
  final TextEditingController topicController;
  final Function(QA) onSave;

  const QAEditScreen({
    super.key,
    required this.qa,
    required this.questionController,
    required this.answerController,
    required this.topicController,
    required this.onSave,
  });

  @override
  State<QAEditScreen> createState() => _QAEditScreenState();
}

class _QAEditScreenState extends State<QAEditScreen> {
  final DatabaseHelper _dbHelper = DatabaseHelper.instance;
  bool _isPreview = false;
  final ScrollController _scrollController = ScrollController();
  final FocusNode _answerFocusNode = FocusNode();

  @override
  void dispose() {
    _scrollController.dispose();
    _answerFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Редактирование вопроса'),
        actions: [
          IconButton(
            icon: Icon(_isPreview ? Icons.edit : Icons.visibility),
            onPressed: () {
              setState(() {
                _isPreview = !_isPreview;
              });
            },
            tooltip: _isPreview ? 'Редактировать' : 'Предпросмотр',
          ),
          IconButton(
            icon: const Icon(Icons.save),
            onPressed: _saveChanges,
            tooltip: 'Сохранить',
          ),
        ],
      ),
      body: Builder(
        builder: (BuildContext scaffoldContext) {
          return Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Поле вопроса
                TextField(
                  controller: widget.questionController,
                  decoration: const InputDecoration(
                    labelText: 'Вопрос',
                    border: OutlineInputBorder(),
                    contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 16),
                  ),
                  maxLines: 2,
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
                ),
                const SizedBox(height: 16),

                // Поле темы
                TextField(
                  controller: widget.topicController,
                  decoration: const InputDecoration(
                    labelText: 'Тема (необязательно)',
                    border: OutlineInputBorder(),
                    contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 16),
                  ),
                ),
                const SizedBox(height: 16),

                // Переключатель между редактором и предпросмотром
                Expanded(
                  child: _isPreview ? _buildPreview() : _buildEditor(),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildEditor() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Ответ (поддерживается Markdown)',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 8),
        Expanded(
          child: Container(
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.shade400),
              borderRadius: BorderRadius.circular(4),
            ),
            child: TextField(
              controller: widget.answerController,
              focusNode: _answerFocusNode,
              decoration: const InputDecoration(
                border: InputBorder.none, // Убираем стандартную границу
                contentPadding: EdgeInsets.all(12),
                hintText: 'Введите ответ...',
                alignLabelWithHint: true,
              ),
              maxLines: null,
              expands: true,
              textAlignVertical: TextAlignVertical.top,
              style: const TextStyle(fontSize: 16),
            ),
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          'Подсказка: используйте *курсив*, **жирный**, `код`, ## Заголовки',
          style: TextStyle(color: Colors.grey, fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildPreview() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Предпросмотр ответа',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 8),
        Expanded(
          child: Container(
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.shade300),
              borderRadius: BorderRadius.circular(8),
            ),
            padding: const EdgeInsets.all(12),
            child: SingleChildScrollView(
              child: MarkdownBody(
                data: widget.answerController.text.isEmpty
                    ? '*Ответ еще не добавлен*'
                    : widget.answerController.text,
                styleSheet: MarkdownStyleSheet(
                  p: const TextStyle(fontSize: 16, height: 1.6),
                  h1: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  h2: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  h3: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  code: TextStyle(
                    backgroundColor: Colors.grey[100],
                    fontFamily: 'monospace',
                    fontSize: 14,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _saveChanges() async {
    final context = this.context;
    
    if (widget.questionController.text.trim().isEmpty ||
        widget.answerController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Вопрос и ответ не могут быть пустыми')),
      );
      return;
    }

    int? newTopicId;
    if (widget.topicController.text.trim().isNotEmpty) {
      newTopicId = await _dbHelper.insertTopic(
        Topic(name: widget.topicController.text.trim()),
      );
    }

    final updatedQA = QA(
      id: widget.qa.id,
      question: widget.questionController.text.trim(),
      answer: widget.answerController.text.trim(),
      topicId: newTopicId,
    );

    await widget.onSave(updatedQA);
    Navigator.pop(context);
  }
}