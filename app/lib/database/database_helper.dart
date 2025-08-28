import 'dart:convert';
import 'dart:io';
import 'package:csv/csv.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import '../models/qa_model.dart';
import '../models/topic_model.dart';

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._init();
  static Database? _database;

  DatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('qa_database.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasePath();
    final path = join(dbPath, filePath);
    return await openDatabase(
      path,
      version: 2, // <-- повышаем версию
      onCreate: _createDB,
      onUpgrade: _upgradeDB,
    );
  }

  Future _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
      )
    ''');
    await db.execute('''
      CREATE TABLE qa_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        topic_id INTEGER,
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE SET NULL
      )
    ''');
  }

  Future<void> _upgradeDB(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      // то же самое – без «...»
      await db.execute('''
        CREATE TABLE topics (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE
        )
      ''');
      await db.execute(
          'ALTER TABLE qa_items ADD COLUMN topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL');
    }
  }

  Future<String> getDatabasePath() async {
    if (Platform.isAndroid || Platform.isIOS) return await getDatabasesPath();
    final appDir = await getApplicationDocumentsDirectory();
    return appDir.path;
  }

  Future<int> insertQA(QA qa) async {
    final db = await instance.database;
    return await db.insert('qa_items', qa.toMap());
  }

  Future<List<QA>> getAllQA({int? topicId}) async {
    final db = await instance.database;
    final maps = topicId == null
        ? await db.query('qa_items')
        : await db.query('qa_items',
            where: 'topic_id = ?', whereArgs: [topicId]);
    return maps.map(QA.fromMap).toList();
  }

  Future<List<Topic>> getAllTopics() async {
    final db = await instance.database;
    final maps = await db.query('topics', orderBy: 'name');
    return maps.map(Topic.fromMap).toList();
  }

  Future<int> insertTopic(Topic topic) async {
    final db = await instance.database;
    return await db.insert('topics', topic.toMap());
  }

  Future<void> clearAllQA() async {
    final db = await instance.database;
    await db.delete('qa_items');
  }

  Future<int> importFromCSV(String csvContent) async {
    final lines = const LineSplitter().convert(csvContent);
    int importedCount = 0;
    for (var line in lines.skip(1)) {
      if (line.trim().isEmpty) continue;
      final rows = const CsvToListConverter().convert(line).first;
      if (rows.length >= 3) {
        final question = rows[0].toString();
        final answer = rows[1].toString();
        final topicName = rows[2].toString();
        final topicId = await _ensureTopic(topicName);
        await insertQA(QA(question: question, answer: answer, topicId: topicId));
        importedCount++;
      }
    }
    return importedCount;
  }

  Future<int> _ensureTopic(String name) async {
    final db = await instance.database;
    final res = await db.query('topics',
        where: 'name = ?', whereArgs: [name], limit: 1);
    if (res.isNotEmpty) return res.first['id'] as int;
    return await insertTopic(Topic(name: name));
  }

  Future<String> exportToCSV({int? topicId}) async {
    final qa = await getAllQA(topicId: topicId);
    final rows = [
      ['question', 'answer', 'topic']
    ];
    for (var q in qa) {
      final topicName = q.topicId == null
          ? ''
          : (await getTopic(q.topicId!))?.name ?? '';
      rows.add([q.question, q.answer, topicName]);
    }
    return const ListToCsvConverter().convert(rows);
  }

  Future<Topic?> getTopic(int id) async {
    final db = await instance.database;
    final maps =
        await db.query('topics', where: 'id = ?', whereArgs: [id], limit: 1);
    return maps.isEmpty ? null : Topic.fromMap(maps.first);
  }


  // Add these methods to your DatabaseHelper class

Future<int> importFromJSON(String jsonContent) async {
  final List<dynamic> jsonData = jsonDecode(jsonContent);
  int importedCount = 0;
  
  for (var item in jsonData) {
    final question = item['question']?.toString() ?? '';
    final answer = item['answer']?.toString() ?? '';
    final topicName = item['topic']?.toString() ?? '';
    
    if (question.isNotEmpty && answer.isNotEmpty) {
      final topicId = await _ensureTopic(topicName);
      await insertQA(QA(question: question, answer: answer, topicId: topicId));
      importedCount++;
    }
  }
  
  return importedCount;
}

Future<String> exportToJSON({int? topicId}) async {
    final qa = await getAllQA(topicId: topicId);
    final List<Map<String, dynamic>> jsonData = [];
    
    for (var q in qa) {
      final topicName = q.topicId == null 
          ? '' 
          : (await getTopic(q.topicId!))?.name ?? '';
      
      jsonData.add({
        'question': q.question,
        'answer': q.answer,
        'topic': topicName,
      });
    }
    
    return jsonEncode(jsonData);
  }
}