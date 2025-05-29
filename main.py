import gradio as gr
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
import logging
import os
import re

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Set your OpenAI API key from environment variable
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# LangChain LLM setup
llm = ChatOpenAI(temperature=0.7)

# Initialize user session state
user_responses = []
learning_preferences = []
initial_question = "Why are you learning Generative AI?"
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
    print("Next question and choices to parse: " + response_text)
    question_and_choices = response_text.strip().split('?')
    question = question_and_choices[0]
    choice_lines = question_and_choices[1].split('\n')
    choices = []
    for line in choice_lines[1:]:
        # match = re.match(r"[\d\-\*\.\)]?\s*(.+)", line.strip())
        # if match:
        #     choices.append(match.group(1))
        if line:
            choices.append(line)
    choices.append("Other (please specify)")
    print(f"Next question: {question}")
    print(f"Next choices: {choices}")
    return question, choices

# Function to generate the next question using LangChain
def generate_next_question(context):
    messages = [
        SystemMessage(content=
                      """
                      You are a GenAI tutor helping the user assess their knowledge and goals in Generative AI. 
                      Based on their previous answers and whether they are correct, you will ask one follow-up non-trivial question to assess their understanding. 
                      The question should ask about their current progress in GenAI learning and the choices should be the next steps in their learning.
                      Return the question followed by a list of 3-5 single-choice options.
                      """
                      ),
        HumanMessage(content=f"Here are the previous responses: {context}. "
                             f"What is the next single-choice question I should ask them about GenAI?")
    ]
    response = llm.invoke(messages)

    return parse_question_and_choices(response.content)

# Handle user answer and generate next question
def handle_answer(radio_answer, other_answer):
    answer = other_answer if radio_answer == "Other (please specify)" and other_answer else radio_answer

    user_responses.append(answer)
    if len(user_responses) >= 10:
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(value=summarize_results(user_responses, learning_preferences), visible=True),
            gr.update(visible=True),
            gr.update(visible=True)
        )
    context = " | ".join(user_responses)
    next_question, next_choices = generate_next_question(context)
    skip_visible = len(user_responses) >= 3

    return (
        gr.update(choices=next_choices, label=next_question, visible=True),
        gr.update(visible=True),
        gr.update(visible=skip_visible),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True)
    )

# Generate summary after all questions
def summarize_results(responses, preferences):
    messages = [
        SystemMessage(content=
                      """
                      You are an expert AI tutor summarizing a learner's progress and goals in GenAI. 
                      Provide a detailed learning path and recommend high-quality resources (articles, videos, courses, or project ideas) based on the user's preferences.
                      """
                      ),
        HumanMessage(content=f"These are the user's answers: {responses}. Their preferred learning methods are: {preferences}. "
                             f"Generate a detailed GenAI learning path with links to preferred types of resources for each step.")
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
        gr.update(visible=True),
        gr.update(visible=True)
    )

# Reset the form and go to the first question
def restart():
    global user_responses
    user_responses= []
    return (
        gr.update(choices=initial_choices, label=initial_question, visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False)
    )

with gr.Blocks() as demo:
    gr.Markdown("# Learn Generative AI")
    gr.Markdown("Start your GenAI journey by telling us why you're here. We'll guide you from there.")

    question_output = gr.Radio(label=initial_question, choices=initial_choices + ["Other (please specify)"], interactive=True)
    other_input = gr.Textbox(label="Other (please specify)")
    next_btn = gr.Button("Next")
    skip_btn = gr.Button("Skip to Summary", visible=False)

    summary_output = gr.Markdown(visible=False)
    preference_output = gr.CheckboxGroup(label="How do you prefer to learn?", choices=preference_choices, visible=False)
    preference_submit_btn = gr.Button("Update my learning plan", visible=False)
    restart_btn = gr.Button("Restart the survey", visible=False)

    next_btn.click(handle_answer, inputs=[question_output, other_input], outputs=[question_output, next_btn, skip_btn, preference_output, summary_output, restart_btn])
    skip_btn.click(skip_to_summary, outputs=[question_output, other_input, next_btn, skip_btn, preference_output, summary_output, preference_submit_btn, restart_btn])
    preference_submit_btn.click(finalize_learning_path, inputs=preference_output, outputs=summary_output)
    restart_btn.click(restart, outputs=[question_output, other_input, next_btn, skip_btn, preference_output, summary_output, preference_submit_btn, restart_btn])

if __name__ == "__main__":
    demo.launch()
