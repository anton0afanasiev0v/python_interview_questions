class ValidationError(Exception):
    """Исключение для ошибок валидации"""
    
    def __init__(self, message, field_name=None, value=None):
        self.message = message
        self.field_name = field_name
        self.value = value
        super().__init__(message)
    
    def __str__(self):
        if self.field_name:
            return f"{self.message} (Поле: {self.field_name}, Значение: {self.value})"
        return self.message

# Использование
def validate_age(age):
    if not isinstance(age, int):
        raise ValidationError("Возраст должен быть числом", "age", age)
    if age < 0:
        raise ValidationError("Возраст не может быть отрицательным", "age", age)
    if age > 150:
        raise ValidationError("Возраст слишком большой", "age", age)

try:
    validate_age(-5)
except ValidationError as e:
    print(f"Ошибка валидации: {e}")
    print(f"Поле: {e.field_name}")
    print(f"Значение: {e.value}")