import gradio as gr
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from environment variable
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# LangChain LLM setup
llm = ChatOpenAI(temperature=0.7)

# Initialize user session state
user_responses = []
learning_preferences = []
current_question = "Why are you learning Generative AI?"

initial_choices = [
    "To assist with daily life tasks",
    "To build apps that use AI",
    "To train or fine-tune AI models"
]

preference_choices = [
    "Reading articles",
    "Watching videos",
    "Building side projects",
    "Taking online courses"
]

# Parse LLM output for question and choices
def parse_question_and_choices(response_text):
    lines = response_text.strip().split('\n')
    question = lines[0]
    choices = []
    for line in lines[1:]:
        match = re.match(r"[\d\-\*\.\)]?\s*(.+)", line.strip())
        if match:
            choices.append(match.group(1))
    choices.append("Other (please specify)")
    return question, choices

# Function to generate the next question using LangChain
def generate_next_question(context):
    messages = [
        SystemMessage(content="You are a GenAI tutor helping the user assess their knowledge and goals in Generative AI. Based on their previous answers, you will ask one follow-up question to assess their understanding. Return the question followed by a list of 3-5 single-choice options."),
        HumanMessage(content=f"Here are the previous responses: {context}. What is the next single-choice question I should ask them about GenAI?")
    ]
    response = llm.invoke(messages)
    return parse_question_and_choices(response.content)

# Handle user answer and generate next question
def handle_first_answer(radio_answer, other_answer):
    answer = other_answer if radio_answer == "Other (please specify)" and other_answer else radio_answer
    return handle_answer(answer)

def handle_answer(answer):
    user_responses.append(answer)
    if len(user_responses) >= 10:
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)

    context = " | ".join(user_responses)
    next_question, next_choices = generate_next_question(context)
    skip_visible = len(user_responses) >= 3

    return (
        gr.update(choices=next_choices, label=next_question, visible=True),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=skip_visible),
        gr.update(visible=False),
        gr.update(visible=False)
    )

# Generate summary after all questions
def summarize_results(responses, preferences):
    messages = [
        SystemMessage(content="You are an expert AI tutor summarizing a learner's progress and goals in GenAI. Provide a detailed learning path and recommend high-quality resources (articles, videos, courses, or project ideas) based on the user's preferences."),
        HumanMessage(content=f"These are the user's answers: {responses}. Their preferred learning methods are: {preferences}. Generate a detailed GenAI learning path with links to preferred types of resources for each step.")
    ]
    response = llm.invoke(messages)
    return response.content

# Finalize and display learning recommendations
def finalize_learning_path(preferences):
    global learning_preferences
    learning_preferences = preferences
    return gr.update(value=summarize_results(user_responses, learning_preferences), visible=True)

# Skip to summary
def skip_to_summary():
    return (
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(value=summarize_results(user_responses, learning_preferences), visible=True),
        gr.update(visible=True)
    )

with gr.Blocks() as demo:
    gr.Markdown("# Learn Generative AI")
    gr.Markdown("Start your GenAI journey by telling us why you're here. We'll guide you from there.")

    question_output = gr.Radio(label=current_question, choices=initial_choices + ["Other (please specify)"], interactive=True)
    other_input = gr.Textbox(label="Other (please specify)")
    next_btn = gr.Button("Next")
    skip_btn = gr.Button("Skip to Summary", visible=False)

    preference_output = gr.CheckboxGroup(label="How do you prefer to learn?", choices=preference_choices, visible=False)
    preference_submit_btn = gr.Button("Get My Learning Plan", visible=False)

    summary_output = gr.Markdown(visible=False)

    next_question_output = gr.Radio(visible=False, interactive=True)
    submit_next_btn = gr.Button("Next", visible=False)

    next_btn.click(handle_first_answer, inputs=[question_output, other_input], outputs=[next_question_output, submit_next_btn, question_output, next_btn, skip_btn, preference_output, summary_output])
    submit_next_btn.click(handle_first_answer, inputs=[next_question_output, other_input], outputs=[next_question_output, submit_next_btn, question_output, next_btn, skip_btn, preference_output, summary_output])
    skip_btn.click(skip_to_summary, outputs=[next_question_output, submit_next_btn, question_output, next_btn, preference_output, summary_output, preference_submit_btn])
    preference_submit_btn.click(finalize_learning_path, inputs=preference_output, outputs=summary_output)

if __name__ == "__main__":
    demo.launch()
