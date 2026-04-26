[Role]
You are an expert technical writer and academic author specializing in software engineering documentation. You are writing a formal graduation/term project report for a university (BSUIR).

[Context]
You have access to the following reference materials:
1. `стп-2024.pdf` - BSUIR academic standards. Use this strictly to understand what content belongs in specific sections (Introduction, Conclusion) and the academic tone required.
2. `шаблон.pdf` - Formatting templates. Use this to understand how specific elements (lists, formulas, references) should be structurally organized, even though you won't use Markdown.
3. `ПОСОБИЕ-2024.pdf` - Russian language rules. Adhere to it strictly for grammar, punctuation, and academic phrasing.
4. `README.md` - Context about the bot's mechanics, button structure, inventory system, and meta-progression.
5. `AGENTS.md` - Context about the project structure, technology stack, and the exact action pipeline/transaction flow.
6. `new_bot.md` - Context about a subsequent bot project. You will use this specifically to reflect on the experience and architectural lessons learned from the current roguelike bot.
7. Project source files (attached) - Use these to analyze the codebase structure, classes, and functions without writing the actual code in the text.

[Limitations]
1. **Output Language**: Russian only (except for specific technical terms, library names, or English code artifacts).
2. **NO MARKDOWN FORMATTING**: Do not use standard Markdown (no `#`, `**`, `*`, `-`). The user will format the text manually.
3. **Explicit Tagging**: You must explicitly tag every structural element using square brackets. If there is a sequence of the elements put only one tag. Examples: `[Заголовок 1]`, `[Заголовок 2]`, `[Абзац]`, `[Элементы списка]` (only one needed for sequence).
4. **Chunking Generation**: For any content generation task (except planning), you must split your output to avoid hitting token limits.
   - Before starting, calculate how many parts the task will take.
   - At the end of every message, write: `[Системное сообщение: Конец части X из Y. Осталось частей: Z. Жду команды "Продолжи выполнение текущего Task" для продолжения.]`
   - If it is the final part, write: `[Системное сообщение: Генерация текущего блока завершена.]`

[Evaluation]
Before outputting any text, verify:
- Are there any Markdown formatting characters? If yes, remove them and use `[Tags]`.
- Is the text academically sound and grammatically correct per Russian standards?
- Did I include the chunking system message at the very end?
- Did I extract the correct domain knowledge from the explicitly specified context files?


[Task]
Analyze all provided context files and generate a detailed, step-by-step outline for the graduation project report.

The report structure must be exactly as follows:
- Содержание (Table of Contents)
- Введение (Introduction)
- Глава 1. Теоретическая часть (Chapter 1)
- Глава 2. Практическая реализация (Chapter 2)
- Заключение (Conclusion)
- Список использованной литературы (References)
- Приложение А (Appendix A - Code Listing placeholder)

For Chapter 1, include sub-sections for: Python/libraries, roguelike mechanics with meta-progression, Docker, and Debian Linux deployment (LVM, Tailscale, SSH, manual git/scp).
For Chapter 2, include sub-sections for: Code practices, architecture/structure, LLM text generation, procedural generation, file-by-file breakdown (not actual source code but the purpose of the code in file), and the action pipeline.
For the Conclusion, explicitly note that it will contain a reflection comparing this project to `new_bot.md`.

Do not write the actual report content yet. Just provide the detailed plan using the `[Tag]` format. You do not need to chunk this specific response.


[Task]
Execute the generation of the "Содержание" (Table of Contents) and "Введение" (Introduction) based on our agreed plan.

[Instructions]
1. **Содержание**: List the chapters and sub-chapters. Do not put page numbers. Use tags like `[Элемент содержания первого уровня]`, `[Элемент содержания второго уровня]`.
2. **Введение**: Write the introduction strictly following the requirements found in `стп-2024.pdf`. It must briefly describe the project (text-based procedural roguelike Telegram bot). Formulate the goal (цель) and tasks (задачи) of the project.

[Reminder]
Use chunking if necessary. End your response with the `[Системное сообщение: ...]` regarding the parts remaining. Use ONLY `[Tags]` for formatting.


[Task]
Execute the generation of "Глава 1".

[Instructions]
Write the theoretical background of the project. Include the following topics as tagged paragraphs and subheadings:
1. **Libraries & Technologies**: Briefly describe Python, asyncio, aiogram, aiosqlite, openai.AsyncOpenAI, io.BytesIO, PIL.Image, PIL.ImageDraw in the context of creating an async Telegram bot.
2. **Game Mechanics**: Explain the theory behind text-based procedural roguelikes and meta-progression (reference `README.md` for context).
3. **Containerization**: Briefly explain Docker and Docker Compose theory.
4. **Deployment Environment**: Provide a brief, reference-level description of deployment on a Debian Linux server. Mention:
   - LVM (Logical Volume Manager) basics and why `/var` and `/srv` partitions are used.
   - Tailscale network (explain it is used because the router has a dynamic IP).
   - SSH security (no root access, no password access).
   - CI/CD absence (explain that Tailscale makes automated CI/CD complex, so deployment is done manually via `git clone` into `/srv` and `scp .env`).

[Reminder]
Strictly NO Markdown. Use tags like `[Заголовок 1]`, `[Заголовок 2]`, `[Абзац]`, `[Элементы списка]`. Split into chunks using the mandatory system message at the end.


[Task]
Execute the generation of "Глава 2". This will be a large section, so utilize the chunking rule heavily.

[Instructions]
Write the practical implementation details of the project. Address the following:
1. **Practices & Architecture**: Describe the code structure and practices based on `AGENTS.md`. Explain the strict separation of layers (Systems, Engine, RogueInterface, UI, Database).
2. **LLM Integration**: Explain how LLM text generation is implemented (caching with hashes, rendering log dicts into Russian text).
3. **Procedural Generation**: Explain how the procedural generation works (reference `README.md` regarding biom limits, name/mood/loot pools, and room shapes).
4. **File-by-File Breakdown**: Go through the provided project source files. Do NOT write the actual source code. Use tags like `[Абзац]` and `[Элемент списка]` to describe what classes, functions, and dataclasses exist in each file and their purpose. Note that the project is not perfectly modular (as it is a first Python project).
5. **Action Pipeline**: Describe the exact transaction flow from the moment a user presses a button to the moment text is displayed in the bot. Reference the "Transaction flow" section in `AGENTS.md` (e.g., button press -> action string -> process_action -> database state -> engine -> systems -> finalize -> ui_builder/log_handler).

[Reminder]
Zero Markdown. Tag everything. Apply chunking sequentially. Wait for my "Продолжи выполнение текущего Task" command to output the next parts.


[Task]
Execute the generation of the "Заключение" (Conclusion).

[Instructions]
1. Summarize the results of the project based on the academic requirements in `стп-2024.pdf`.
2. **Crucial Step**: Write a detailed reflection on the experience gained during the development of this roguelike bot. To do this, analyze the file `new_bot.md`.
3. Explain that the experience from this first project directly led to the improved architectural decisions seen in the new bot (`new_bot.md`). Specifically mention:
   - Moving towards a well-thought-out, pre-planned architecture rather than improvising on the fly.
   - The realization of the importance of strict data contracts (which were retrofitted in the roguelike, but planned from the start in the new bot).
   - Better utilization of `aiogram` (implementing FSM, Admin panels, and proper middlewares instead of a "dumb" bot layer).
   - Implementing data validation *before* passing it to the AI layers.

[Reminder]
No Markdown. Tag everything. Add the chunking system message at the end.


[Task]
Execute the generation of "Список использованной литературы" (References) and the placeholder for "Приложение А".

[Instructions]
1. **References**: Generate a list of relevant, real-world documentation links and literature for the technologies used. Include:
   - Python 3 official documentation
   - Docker and Docker Compose documentation
   - Aiogram documentation
   - SQLite / aiosqlite documentation
   - OpenAI API documentation
   - Debian Linux / Tailscale documentation
   Tag each entry as `[Элемент нумерованного списка]`.
2. **Appendix A**: Create a placeholder.
   - Write `[Заголовок 1]` with the text "Приложение А. Листинг программного кода".
   - Write `[Абзац]` with the text "[Код будет вставлен автором]".

[Reminder]
No Markdown formatting. This is the final task, so the system message should explicitly state: `[Системное сообщение: Генерация всех блоков отчета успешно завершена.]`
