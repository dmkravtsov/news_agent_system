from abc import ABC, abstractmethod
from typing import Any, List

class BaseAgent(ABC):
    """
    Базовый класс для всех агентов в проекте.
    Этот класс определяет общий интерфейс и базовую функциональность, 
    которую могут переопределять дочерние классы.
    """

    def __init__(self, name: str = "BaseAgent"):
        """
        Инициализирует базовый агент с заданным именем.

        :param name: Имя агента, используется для логирования.
        """
        self.name = name  # Устанавливаем имя агента

    @abstractmethod
    async def process(self, data: Any) -> Any:
        """
        Абстрактный метод для обработки данных.
        Каждый агент должен реализовать эту функцию в своём классе.

        :param data: Входные данные для обработки.
        :return: Результат обработки данных.
        """
        pass  # Этот метод должен быть переопределён в дочерних классах

    async def log(self, message: str, level: str = "INFO") -> None:
        """
        Логирует сообщение с указанным уровнем.

        :param message: Сообщение для логирования.
        :param level: Уровень логирования (например, INFO, WARNING, ERROR).
        """
        print(f"[{level}] {self.name}: {message}")  # Форматируем и выводим сообщение

    async def handle_error(self, error: Exception, context: Any = None) -> None:
        """
        Обрабатывает исключения и логирует их с уровнем ERROR.

        :param error: Исключение, которое произошло.
        :param context: Дополнительный контекст, связанный с исключением.
        """
        # Логируем сообщение об ошибке с контекстом (если он есть)
        await self.log(f"Error: {error}. Context: {context}", level="ERROR")

    async def validate_data(self, data: List[Any]) -> bool:
        """
        Проверяет входные данные перед обработкой.
        Если данных нет, выводится предупреждение.

        :param data: Список данных для проверки.
        :return: True, если данные корректны, иначе False.
        """
        if not data:  # Проверяем, переданы ли данные
            await self.log("No data provided.", level="WARNING")  # Логируем предупреждение
            return False  # Данные некорректны (их нет)
        return True  # Данные корректны
