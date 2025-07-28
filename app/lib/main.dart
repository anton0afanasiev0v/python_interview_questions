import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:file_picker/file_picker.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'database/database_helper.dart';
import 'models/qa_model.dart';

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
      title: 'Q&A Importer',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        cardTheme: CardTheme(
          elevation: 2,
          margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
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
  List<QA> _qaItems = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadQAItems();
  }

  Future<void> _loadQAItems() async {
    setState(() => _isLoading = true);
    _qaItems = await _dbHelper.getAllQA();
    setState(() => _isLoading = false);
  }

  Future<void> _importCSV() async {
    try {
      debugPrint('Начало выбора файла...');
      
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['csv'],
        allowMultiple: false,
        withData: true,
      );

      if (result == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Выбор файла отменён')),
        );
        return;
      }

      setState(() => _isLoading = true);
      final file = result.files.first;
      final csvContent = file.bytes != null 
          ? utf8.decode(file.bytes!) 
          : await File(file.path!).readAsString();

      await _processCSVImport(csvContent);
    } catch (e, stackTrace) {
      debugPrint('Ошибка импорта: $e\n$stackTrace');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Ошибка импорта: ${e.toString()}'),
          duration: const Duration(seconds: 5),
        ),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _processCSVImport(String csvContent) async {
    await _dbHelper.clearAllQA();
    final count = await _dbHelper.importFromCSV(csvContent);
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Успешно импортировано $count вопросов')),
    );
    
    await _loadQAItems();
  }

  Future<void> _clearDatabase() async {
    try {
      setState(() => _isLoading = true);
      await _dbHelper.clearAllQA();
      await _loadQAItems();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('База данных очищена')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка при очистке: ${e.toString()}')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Вопросы и ответы'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete, color: Colors.white),
            onPressed: _isLoading ? null : _clearDatabase,
            tooltip: 'Очистить базу данных',
          ),
          IconButton(
            icon: const Icon(Icons.upload_file, color: Colors.white),
            onPressed: _isLoading ? null : _importCSV,
            tooltip: 'Импорт CSV',
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(
          strokeWidth: 3,
          valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
        ),
      );
    }
    
    if (_qaItems.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.inbox, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text(
              'Нет данных',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              icon: const Icon(Icons.upload),
              label: const Text('Импортировать CSV'),
              onPressed: _importCSV,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
            ),
          ],
        ),
      );
    }
    
    return ListView.builder(
      padding: const EdgeInsets.only(bottom: 16),
      itemCount: _qaItems.length,
      itemBuilder: (context, index) {
        final qa = _qaItems[index];
        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: ExpansionTile(
              tilePadding: const EdgeInsets.symmetric(horizontal: 16),
              title: Text(
                qa.question,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
              children: [
                Container(
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardTheme.color,
                    borderRadius: const BorderRadius.only(
                      bottomLeft: Radius.circular(12),
                      bottomRight: Radius.circular(12),
                    ),
                  ),
                  padding: const EdgeInsets.all(16),
                  child: MarkdownBody(
                    data: qa.answer,
                    styleSheet: MarkdownStyleSheet(
                      p: const TextStyle(fontSize: 15, height: 1.5),
                      code: TextStyle(
                        backgroundColor: Colors.grey[200],
                        fontFamily: 'monospace',
                        fontSize: 14,
                      ),
                      blockquote: TextStyle(
                        color: Colors.grey[700],
                        fontStyle: FontStyle.italic,
                        // padding: const EdgeInsets.only(left: 16),
                        // borderLeft: BorderLeft(
                        //   color: Colors.grey,
                        //   width: 4,
                        // ),
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
}