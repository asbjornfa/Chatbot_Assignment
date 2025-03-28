class MongoMemory:

    def __init__(self, collection):
        self.collection = collection

    def save_message(self, subject: str, user_input: str, bot_response: str):
        self.collection.insert_one({
            "subject": subject,
            "user": user_input,
            "bot": bot_response})

    def load_messages(self, subject: str):
        messages = self.collection.find({"subject": subject}, {"_id": 0})
        return [f"User: {m['user']}\nBot: {m['bot']}" for m in messages]