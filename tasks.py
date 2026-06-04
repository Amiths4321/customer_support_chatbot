from crewai import Task


def build_tasks(topic: str, researcher, writer, reviewer, saver):

    research_task = Task(
        description=(
            f"Research the topic: '{topic}'\n\n"
            "Steps:\n"
            "1. Search for background information, key facts, and recent developments.\n"
            "2. Search for expert opinions and notable statistics.\n"
            "3. Search for real-world examples or case studies.\n"
            "4. Compile everything into structured research notes with source URLs.\n\n"
            "Your output must be detailed research notes (400-600 words) covering: "
            "overview, key facts & stats, current trends, expert views, examples."
        ),
        expected_output=(
            "Detailed, structured research notes on the topic with sections for: "
            "Overview, Key Facts & Statistics, Current Trends, Expert Opinions, "
            "Real-World Examples, and Sources."
        ),
        agent=researcher,
    )

    writing_task = Task(
        description=(
            f"Write a comprehensive article on: '{topic}'\n\n"
            "Use the research notes provided. Your article must:\n"
            "- Start with a strong, engaging hook (first paragraph grabs attention)\n"
            "- Have clear Markdown headings (##, ###)\n"
            "- Be 600-800 words in length\n"
            "- Include an introduction, 3-4 body sections, and a conclusion\n"
            "- Use concrete examples and stats from the research\n"
            "- End with a clear takeaway or call to action"
        ),
        expected_output=(
            "A well-structured, engaging 600-800 word article in Markdown format with "
            "a title, introduction, multiple sections with headings, and a conclusion."
        ),
        agent=writer,
        context=[research_task],
    )

    review_task = Task(
        description=(
            "Review and improve the article written by the Content Writer.\n\n"
            "Check for:\n"
            "- Clarity: Is every sentence easy to understand?\n"
            "- Structure: Does the article flow logically?\n"
            "- Engagement: Is the opening hook strong? Does it hold interest?\n"
            "- Accuracy: Are claims supported by the research?\n"
            "- Conciseness: Remove redundancy and filler phrases.\n"
            "- Grammar and style: Fix any errors.\n\n"
            "Rewrite and return the complete polished article in Markdown. "
            "Keep the same structure but make it significantly better."
        ),
        expected_output=(
            "A polished, publication-ready article in Markdown format that is clearer, "
            "more engaging, and better structured than the original draft."
        ),
        agent=reviewer,
        context=[writing_task],
    )

    save_task = Task(
        description=(
            "Take the final reviewed article and:\n"
            "1. Ensure it has a proper Markdown title (# Title) at the top.\n"
            f"2. Add a metadata header: Topic: {topic}, Date: today's date.\n"
            "3. Save it to disk using the Save Article tool.\n"
            "4. Return the complete final article text."
        ),
        expected_output=(
            "Confirmation that the article was saved, plus the complete final article text in Markdown."
        ),
        agent=saver,
        context=[review_task],
    )

    return research_task, writing_task, review_task, save_task
