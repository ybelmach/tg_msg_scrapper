import logging

# Создаем основной логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Обработчик для файла
file_handler = logging.FileHandler('summarizer_log.log', mode='w')
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(file_handler)

# Обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(console_handler)
