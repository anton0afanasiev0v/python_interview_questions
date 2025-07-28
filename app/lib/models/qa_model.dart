

class QA {
  final int? id;
  final String question;
  final String answer;

  QA({this.id, required this.question, required this.answer});

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'question': question,
      'answer': answer,
    };
  }

  factory QA.fromMap(Map<String, dynamic> map) {
    return QA(
      id: map['id'],
      question: map['question'],
      answer: map['answer'],
    );
  }
}