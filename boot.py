import random
import os
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

class ITQuizBot:
    def __init__(self, token):
        self.questions = [
            {
                "question": "Какой язык программирования создал Guido van Rossum?",
                "options": ["Java", "Python", "C++", "JavaScript"],
                "correct": 1,
                "explanation": "✅ Правильно! Python был создан Гвидо ван Россумом в 1991 году."
            },
            {
                "question": "Что означает аббревиатура 'HTML'?",
                "options": [
                    "Hyperlinks and Text Markup Language",
                    "Home Tool Markup Language",
                    "Hyper Text Markup Language",
                    "Hyper Transfer Markup Language"
                ],
                "correct": 2,
                "explanation": "✅ Верно! HTML - Hyper Text Markup Language."
            },
            {
                "question": "Какой тип данных используется для хранения истинного/ложного значения?",
                "options": ["String", "Boolean", "Integer", "Float"],
                "correct": 1,
                "explanation": "✅ Точно! Boolean (булев тип) используется для True/False."
            },
            {
                "question": "Какой алгоритм сортировки имеет сложность O(n log n) в среднем случае?",
                "options": ["Пузырьковая", "Быстрая", "Вставками", "Выбором"],
                "correct": 1,
                "explanation": "✅ Правильно! Быстрая сортировка (QuickSort) имеет O(n log n)."
            },
            {
                "question": "Что такое 'репозиторий' в Git?",
                "options": [
                    "Текстовый редактор",
                    "Хранилище кода",
                    "Язык программирования",
                    "Тип базы данных"
                ],
                "correct": 1,
                "explanation": "✅ Верно! Репозиторий - это хранилище кода и его истории изменений."
            }
        ]
        
        self.application = Application.builder().token(token).build()
        
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("quiz", self.start_quiz))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        self.user_data = {}
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        chat_id = update.effective_chat.id
        self.user_data[chat_id] = {
            'score': 0,
            'current_question': None,
            'quiz_active': False
        }
        await update.message.reply_text(
            "👋 Привет! Я IT-викторина бот.\n"
            "Проверь свои знания в программировании и технологиях!\n\n"
            "Нажми /quiz чтобы начать викторину.",
            reply_markup=ReplyKeyboardRemove()
        )
    
    async def start_quiz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало викторины"""
        chat_id = update.effective_chat.id
        
        if chat_id not in self.user_data:
            self.user_data[chat_id] = {
                'score': 0,
                'current_question': None,
                'quiz_active': False
            }
        
        questions = random.sample(self.questions, len(self.questions))
        self.user_data[chat_id].update({
            'score': 0,
            'current_question': 0,
            'quiz_active': True,
            'questions': questions
        })
        
        await self.ask_question(update, chat_id)
    
    async def ask_question(self, update: Update, chat_id: int):
        """Задаем текущий вопрос пользователю"""
        user_state = self.user_data[chat_id]
        question_num = user_state['current_question']
        question_data = user_state['questions'][question_num]
        
        keyboard = [[option] for option in question_data['options']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        
        await update.message.reply_text(
            f"❓ Вопрос {question_num + 1}/{len(self.questions)}:\n"
            f"{question_data['question']}",
            reply_markup=reply_markup
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ответов пользователя"""
        chat_id = update.effective_chat.id
        
        if chat_id not in self.user_data or not self.user_data[chat_id]['quiz_active']:
            await update.message.reply_text("Нажми /quiz чтобы начать викторину!")
            return
        
        user_state = self.user_data[chat_id]
        question_data = user_state['questions'][user_state['current_question']]
        user_answer = update.message.text
        
        if user_answer in question_data['options']:
            answer_index = question_data['options'].index(user_answer)
            if answer_index == question_data['correct']:
                user_state['score'] += 1
                reply_text = question_data['explanation']
            else:
                correct_answer = question_data['options'][question_data['correct']]
                reply_text = f"❌ Неправильно. Правильный ответ: {correct_answer}"
            
            await update.message.reply_text(reply_text)
            
            user_state['current_question'] += 1
            if user_state['current_question'] < len(self.questions):
                await self.ask_question(update, chat_id)
            else:
                await self.end_quiz(update, chat_id)
        else:
            await update.message.reply_text("Пожалуйста, выберите один из предложенных вариантов.")
    
    async def end_quiz(self, update: Update, chat_id: int):
        """Завершение викторины"""
        user_state = self.user_data[chat_id]
        total = len(self.questions)
        score = user_state['score']
        
        result_message = (
            f"🏆 Викторина завершена!\n"
            f"Ваш результат: {score} из {total}\n\n"
        )
        
        if score == total:
            result_message += "🔥 Потрясающе! Идеальный результат! Вы IT-гений!"
        elif score >= total / 2:
            result_message += "👍 Хороший результат! Вы знаете основы IT!"
        else:
            result_message += "💪 Неплохо, но есть куда расти! Попробуйте еще раз!"
        
        result_message += "\n\nНажми /quiz чтобы сыграть снова."
        
        await update.message.reply_text(
            result_message,
            reply_markup=ReplyKeyboardRemove()
        )
        user_state['quiz_active'] = False
    
    def run(self):
        """Запуск бота"""
        print("Бот запущен...")
        self.application.run_polling()

if __name__ == '__main__':
    TOKEN = "7651311186:AAHBlwOnTV49ssQpGY1hoiBRUmGRTjrcYsg"  # Замените на реальный токен
    bot = ITQuizBot(TOKEN)
    bot.run()