from crewai import Crew, Process
from agents import build_agents
from tasks import build_tasks


def run_pipeline(topic: str, base_url: str, model: str = "mistral:latest") -> dict:
    researcher, writer, reviewer, saver = build_agents(base_url, model)
    research_task, writing_task, review_task, save_task = build_tasks(
        topic, researcher, writer, reviewer, saver
    )

    crew = Crew(
        agents=[researcher, writer, reviewer, saver],
        tasks=[research_task, writing_task, review_task, save_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff(inputs={"topic": topic})

    return {
        "final":    str(result),
        "research": str(research_task.output.raw  if research_task.output else ""),
        "draft":    str(writing_task.output.raw   if writing_task.output  else ""),
        "reviewed": str(review_task.output.raw    if review_task.output   else ""),
    }
