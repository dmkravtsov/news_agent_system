import logging
from abc import ABC, abstractmethod
from typing import Any, List
from pydantic import BaseModel, ConfigDict

class BaseAgent(BaseModel, ABC):
    """
    Базовый класс для всех агентов в проекте.
    Этот класс определяет общий интерфейс и базовую функциональность, 
    которую могут использовать дочерние классы.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "BaseAgent"
    logger: logging.Logger = logging.getLogger("BaseAgent")

    @abstractmethod
    async def process(self, data: Any) -> Any:
        """
        Метод для обработки данных. Должен быть переопределён в дочерних классах.

        :param data: Входные данные для обработки.
        :return: Результат обработки данных.
        """
        pass

    async def log(self, message: str, level: str = "INFO") -> None:
        """
        Логирует сообщение с указанным уровнем.

        :param message: Сообщение для логирования.
        :param level: Уровень логирования (например, INFO, WARNING, ERROR).
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"{self.name}: {message}")

    async def handle_error(self, error: Exception, context: Any = None) -> None:
        """
        Обрабатывает исключения и логирует их с уровнем ERROR.

        :param error: Исключение, которое произошло.
        :param context: Дополнительный контекст, связанный с исключением.
        """
        await self.log(f"Error: {error}. Context: {context}", level="ERROR")

    async def validate_data(self, data: List[Any]) -> bool:
        """
        Проверяет входные данные перед обработкой.
        Если данных нет, выводится предупреждение.

        :param data: Список данных для проверки.
        :return: True, если данные корректны, иначе False.
        """
        if not isinstance(data, list) or not data:
            await self.log("Invalid or empty data provided.", level="WARNING")
            return False
        return True
