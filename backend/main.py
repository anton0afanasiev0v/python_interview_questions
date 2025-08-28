from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Annotated
from datetime import datetime
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from bson import ObjectId
import os
from pydantic_core import core_schema

app = FastAPI(
    title="IT Interview Questions API",
    description="API для базы вопросов и ответов на IT собеседования с MongoDB",
    version="1.0.0",
)

# Подключение к MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.interview_db
categories_collection = db.categories
questions_collection = db.questions

# Модели данных
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if ObjectId.is_valid(v):
            return str(ObjectId(v))
        raise ValueError("Invalid ObjectId")

class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class Category(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "Python",
                "description": "Вопросы по языку программирования Python"
            }
        }
    )

class Question(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    question_text: str
    answer_text: str
    category_id: PyObjectId
    difficulty: DifficultyLevel
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "question_text": "Что такое декоратор в Python?",
                "answer_text": "Декоратор - это функция, которая принимает другую функцию...",
                "category_id": "507f1f77bcf86cd799439011",
                "difficulty": "medium",
                "tags": ["python", "декораторы"]
            }
        }
    )

# Вспомогательные функции
async def get_category(category_id: str):
    category = await categories_collection.find_one({"_id": ObjectId(category_id)})
    if category:
        return Category(**category)
    return None

async def is_question_exists(question_text: str, exclude_id: Optional[str] = None) -> bool:
    """Проверяет, существует ли вопрос с таким текстом"""
    query = {"question_text": {"$regex": f"^{question_text}$", "$options": "i"}}
    if exclude_id:
        query["_id"] = {"$ne": ObjectId(exclude_id)}
    count = await questions_collection.count_documents(query)
    return count > 0

# Роуты для категорий
@app.post("/categories/", response_model=Category, tags=["Categories"])
async def create_category(category: Category):
    if await categories_collection.find_one({"name": category.name}):
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    category_dict = category.dict(by_alias=True, exclude={"id"})
    result = await categories_collection.insert_one(category_dict)
    created_category = await categories_collection.find_one({"_id": result.inserted_id})
    return Category(**created_category)

@app.get("/categories/", response_model=List[Category], tags=["Categories"])
async def read_categories(limit: int = Query(100, le=1000), skip: int = 0):
    categories = []
    async for category in categories_collection.find().skip(skip).limit(limit):
        categories.append(Category(**category))
    return categories

@app.get("/categories/{category_id}", response_model=Category, tags=["Categories"])
async def read_category(category_id: str):
    category = await get_category(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# Роуты для вопросов
@app.post("/questions/", response_model=Question, tags=["Questions"])
async def create_question(question: Question):
    # Проверяем существование категории
    if not await get_category(str(question.category_id)):
        raise HTTPException(status_code=400, detail="Category not found")
    
    # Проверяем уникальность вопроса
    if await is_question_exists(question.question_text):
        raise HTTPException(
            status_code=400,
            detail="Question with this text already exists"
        )
    
    question_dict = question.dict(by_alias=True, exclude={"id"})
    result = await questions_collection.insert_one(question_dict)
    created_question = await questions_collection.find_one({"_id": result.inserted_id})
    return Question(**created_question)

@app.get("/questions/", response_model=List[Question], tags=["Questions"])
async def read_questions(
    category_id: Optional[str] = Query(None, description="Фильтр по ID категории"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Фильтр по сложности"),
    tag: Optional[str] = Query(None, description="Фильтр по тегу"),
    limit: int = Query(10, le=100),
    skip: int = 0
):
    query = {}
    if category_id:
        query["category_id"] = ObjectId(category_id)
    if difficulty:
        query["difficulty"] = difficulty
    if tag:
        query["tags"] = tag
    
    questions = []
    async for question in questions_collection.find(query).skip(skip).limit(limit):
        questions.append(Question(**question))
    return questions

@app.get("/questions/{question_id}", response_model=Question, tags=["Questions"])
async def read_question(question_id: str):
    question = await questions_collection.find_one({"_id": ObjectId(question_id)})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return Question(**question)

@app.put("/questions/{question_id}", response_model=Question, tags=["Questions"])
async def update_question(question_id: str, updated_question: Question):
    # Проверяем существование категории
    if not await get_category(str(updated_question.category_id)):
        raise HTTPException(status_code=400, detail="Category not found")
    
    # Проверяем уникальность вопроса (исключая текущий вопрос)
    if await is_question_exists(updated_question.question_text, exclude_id=question_id):
        raise HTTPException(
            status_code=400,
            detail="Question with this text already exists"
        )
    
    update_data = updated_question.dict(
        by_alias=True,
        exclude={"id", "created_at"},
        exclude_unset=True
    )
    update_data["updated_at"] = datetime.now()
    
    question = await questions_collection.find_one_and_update(
        {"_id": ObjectId(question_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return Question(**question)

@app.delete("/questions/{question_id}", tags=["Questions"])
async def delete_question(question_id: str):
    result = await questions_collection.delete_one({"_id": ObjectId(question_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}

# Поиск по вопросам
@app.get("/search/", response_model=List[Question], tags=["Search"])
async def search_questions(
    query: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(10, le=100)
):
    questions = []
    async for question in questions_collection.find(
        {"$text": {"$search": query}},
        {"score": {"$meta": "textScore"}}
    ).sort([("score", {"$meta": "textScore"})]).limit(limit):
        questions.append(Question(**question))
    return questions

# Генерация случайного вопроса
@app.get("/questions/random/", response_model=Question, tags=["Questions"])
async def get_random_question(
    category_id: Optional[str] = Query(None),
    difficulty: Optional[DifficultyLevel] = Query(None)
):
    query = {}
    if category_id:
        query["category_id"] = ObjectId(category_id)
    if difficulty:
        query["difficulty"] = difficulty
    
    count = await questions_collection.count_documents(query)
    if count == 0:
        raise HTTPException(status_code=404, detail="No questions found with these filters")
    
    import random
    random_skip = random.randint(0, count - 1)
    question = await questions_collection.find_one(query, skip=random_skip)
    return Question(**question)

# Создание текстового индекса при старте
@app.on_event("startup")
async def create_indexes():
    await questions_collection.create_index([("question_text", "text"), ("answer_text", "text")])
    await questions_collection.create_index("category_id")
    await questions_collection.create_index("difficulty")
    await questions_collection.create_index("tags")