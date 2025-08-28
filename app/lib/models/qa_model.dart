

class QA {
  final int? id;
  final String question;
  final String answer;
  final int? topicId;

  QA({this.id, required this.question, required this.answer, this.topicId});

  Map<String, dynamic> toMap() =>
      {'id': id, 'question': question, 'answer': answer, 'topic_id': topicId};

  factory QA.fromMap(Map<String, dynamic> map) => QA(
        id: map['id'],
        question: map['question'],
        answer: map['answer'],
        topicId: map['topic_id'],
      );
}