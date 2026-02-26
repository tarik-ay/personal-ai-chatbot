import anthropic

PROFILE_PATH = "tarik_profile.md"

SUGGESTED_QUESTIONS = [
    "What is Tarik's background?",
    "What programming skills does Tarik have?",
    "What projects has Tarik built?",
    "What are Tarik's goals?",
    "What topics is Tarik interested in?",
]

SYSTEM_PROMPT = """\
You are a personal assistant that answers questions about Tarik based solely on the profile below.
If the answer is not found in the profile, respond with exactly: "Tarik hasn't covered that yet."
Do not use any outside knowledge. Be concise and friendly.

--- TARIK'S PROFILE ---
{profile}
--- END OF PROFILE ---"""


def load_profile(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def ask(client: anthropic.Anthropic, system: str, conversation: list, question: str) -> str:
    conversation.append({"role": "user", "content": question})
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=system,
        messages=conversation,
    )
    answer = response.content[0].text
    conversation.append({"role": "assistant", "content": answer})
    return answer


def main():
    profile = load_profile(PROFILE_PATH)
    system = SYSTEM_PROMPT.format(profile=profile)
    client = anthropic.Anthropic()
    conversation = []

    print("\n=== Tarik's Personal Chatbot ===")
    print("Ask me anything about Tarik. Type 'quit' or 'exit' to stop.\n")
    print("Suggested questions to get you started:")
    for i, q in enumerate(SUGGESTED_QUESTIONS, 1):
        print(f"  {i}. {q}")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        # Allow selecting a suggested question by number
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(SUGGESTED_QUESTIONS):
                user_input = SUGGESTED_QUESTIONS[idx]
                print(f"You: {user_input}")

        answer = ask(client, system, conversation, user_input)
        print(f"\nTarik's Bot: {answer}\n")


if __name__ == "__main__":
    main()
