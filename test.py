from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="QuantFactory/Phi-3-mini-128k-instruct-GGUF",
    filename="Phi-3-mini-128k-instruct.Q4_K_M.gguf",
    verbose=False
)

msg = """Номады, общий сбор! 🚨 Тут представили (https://www.tomsguide.com/computing/peripherals/this-suitcase-transforms-into-a-dual-display-workstation-and-im-shocked-how-well-it-works) переносную рабочую станцию с двумя мониторами — Base Case.

Устройство оснащено двумя дисплеями с разрешением Full HD (1920×1080) и ножками, которые поднимают мониторы на 25 см.

И вся эта конструкция складывается в виде чемодана с выдвижной ручкой и колесиками. Весит чудо 9 кг, так что в ручную кладь пройдет, но тщательные проверки в аэропорту — гарантированы.

Цена неизвестна, но
продажи запланированы на февраль через платформу Indiegogo.

@xor_journal"""


prompt = f"""Составь краткий анонс для сообщения ниже, состоящий не более чем из {25} слов.
        Анонс должен давать краткое саммари сообщения, не упуская важные детали.
        Включи в анонс ключевые факты из сообщения, если нужно.
        Если в сообщении есть абзац точно и емко описывающий все сообщение, используй его в качестве анонса. 

        <message>
            {msg}
        </message>
        """

response = llm.create_chat_completion(
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print(f"Response: {response['choices'][0]['message']['content']}".lstrip())
