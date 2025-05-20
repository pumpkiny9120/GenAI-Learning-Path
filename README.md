# GenAI-Learning-Path
This project is a webpage that uses GenAI to help you learn GenAI.
It prompts you with up to 10 questions to assess your current knowledge and provides suggestions on your next steps.

## Main Logic
1. Click the "start assessment" button to start assessing the user's current knowledge of GenAI.
2. The first question is fixed. It is always asked to understand why someone is learning GenAI, for example, if they are learning to use AI to assist with activities in their daily life, to develop apps that use AI, or to train/fine-tune AI. A text input is also provided for other answers not included in the default choices.
3. After each question, a call is made to OpenAI with the context so far in order to generate the next question that explores deeper into their knowledge of AI.
4. Based on the answers of those questions, the user is provided with a summary and suggestions on what the next steps are in their GenAI learning journey.
5. Select "skip to summary" after at least 3 questions allows the user to jump straight to the summary/suggestions without having to answer all 10 questions.
6. In the suggestion of next steps, the detailed learning path contains links to useful articles for each item by default. A multiple-choice question is presented for the user to select their preferred learning styles: reading articles, watching videos, building side projects, and/or taking online courses. When the choices are submitted, update the resource links to the resources they prefer.

## Technology Used
OpenAI, LangChain, Gradio

## How to Run Locally
1. Add a `.env` file with your OpenAI key:
```commandline
OPENAI_API_KEY=<your_own_key>
```
3. Create virtual env
```commandline
pyenv install 3.9
pyenv virtualenv 3.9 genai_learner
pyenv activate genai_learner
```
3. You might need to export the following environment variables to connect
```commandline
export REQUESTS_CA_BUNDLE=~/.ssl/<valid_certs>.pem
export SSL_CERT_FILE=~/.ssl/<valid_certs>.pem
```
4. Run the main program and visit the local url `http://127.0.0.1:7860`
```commandline
python main.py
```
