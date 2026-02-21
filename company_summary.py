import anthropic


def main():
    company_name = input("Enter a company name: ").strip()
    if not company_name:
        print("No company name provided.")
        return

    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": (
    f"Analyze '{company_name}' as a potential debt financing candidate. Structure your response in 4 short sections:\n"
    f"1. Business Type: What type of company they are and their revenue model\n"
    f"2. Funding History: Known funding rounds and notable investors\n"
    f"3. Leadership: Who runs the company\n"
    f"4. Debt Risk Flags: Any red flags from a debt perspective\n"
    f"Keep each section to 2-3 sentences maximum. If unknown, say 'Insufficient public data'."
                ),
            }
        ],
    )

    print(response.content[0].text)


if __name__ == "__main__":
    main()
