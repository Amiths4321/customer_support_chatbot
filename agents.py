from crewai import Agent, LLM
from tools import web_search, save_article


def get_llm(base_url: str, model: str = "mistral:latest"):
    return LLM(model=f"ollama/{model}", base_url=base_url, temperature=0.2)


def build_agents(base_url: str, model: str = "mistral:latest"):
    llm = get_llm(base_url, model)

    researcher = Agent(
        role="Senior Research Analyst",
        goal="Research the given topic thoroughly and gather comprehensive, accurate information from multiple sources.",
        backstory=(
            "You are an expert research analyst with 15 years of experience in content research. "
            "You dig deep into topics, cross-reference sources, and distil key facts, trends, "
            "statistics, and expert opinions into clear, structured research notes."
        ),
        tools=[web_search],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )

    writer = Agent(
        role="Expert Content Writer",
        goal="Transform research notes into a compelling, well-structured, engaging article.",
        backstory=(
            "You are a seasoned journalist and content strategist who writes for top publications. "
            "You turn raw research into clear narratives with a strong hook, logical flow, "
            "concrete examples, and a memorable conclusion. You write for a general educated audience."
        ),
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    reviewer = Agent(
        role="Chief Editor & Quality Reviewer",
        goal="Review the article and produce a polished, improved final version ready for publication.",
        backstory=(
            "You are a chief editor at a major publication with two decades of editing experience. "
            "You improve clarity, fix structure, strengthen arguments, eliminate redundancy, "
            "and ensure every paragraph earns its place. Your edits make good articles great."
        ),
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    saver = Agent(
        role="Content Manager",
        goal="Format the final reviewed article cleanly in Markdown and save it to disk.",
        backstory=(
            "You are a meticulous content manager responsible for final formatting and archiving. "
            "You ensure the article has proper Markdown headings, a clean structure, "
            "and is saved correctly so it is ready for publishing or sharing."
        ),
        tools=[save_article],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )

    return researcher, writer, reviewer, saver
