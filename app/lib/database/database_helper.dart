import 'dart:convert';
import 'dart:io';

import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import '../models/qa_model.dart';

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
    // Инициализация для десктопных платформ (если используется sqflite_common_ffi)
    if (Platform.isLinux || Platform.isMacOS || Platform.isWindows) {
      // Раскомментируйте, если используете sqflite_common_ffi
      // databaseFactory = databaseFactoryFfi;
    }

    final dbPath = await getDatabasePath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDB,
    );
  }

  Future<String> getDatabasePath() async {
    if (Platform.isAndroid || Platform.isIOS) {
      // Для мобильных платформ
      return await getDatabasesPath();
    } else {
      // Для десктопных платформ
      final appDir = await getApplicationDocumentsDirectory();
      return appDir.path;
    }
  }

  Future _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE qa_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
      )
    ''');
  }

  Future<int> insertQA(QA qa) async {
    final db = await instance.database;
    return await db.insert('qa_items', qa.toMap());
  }

  Future<List<QA>> getAllQA() async {
    final db = await instance.database;
    final maps = await db.query('qa_items');
    return maps.map((map) => QA.fromMap(map)).toList();
  }

  Future<void> clearAllQA() async {
    final db = await instance.database;
    await db.delete('qa_items');
  }

  Future<int> importFromCSV(String csvContent) async {
    final lines = LineSplitter().convert(csvContent);
    int importedCount = 0;

    for (var line in lines.skip(1)) { // Пропускаем заголовок
      if (line.trim().isEmpty) continue;
      
      final parts = line.split(',');
      if (parts.length >= 2) {
        final question = parts[0].replaceAll('"', '');
        final answer = parts.sublist(1).join(',').replaceAll('"', '').trim();
        
        await insertQA(QA(question: question, answer: answer));
        importedCount++;
      }
    }

    return importedCount;
  }
}