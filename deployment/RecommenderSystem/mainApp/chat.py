import os

from huggingface_hub import Repository
from text_generation import Client
import random
import hashlib

HF_TOKEN = os.environ.get("HF_TOKEN", None)
API_TOKEN = os.environ.get("API_TOKEN", None)

API_URL = "https://api-inference.huggingface.co/models/timdettmers/guanaco-33b-merged"
def md5(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[::-1]
def get_api_key(user_agent: str) -> str:
    part1 = str(random.randint(0, 10**11))
    part2 = md5(user_agent + md5(user_agent + md5(user_agent + part1 + "x")))

    return f"tryit-{part1}-{part2}"

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

headers = {
    "Authorization": "Bearer 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"
}
client = Client(
    API_URL,
    headers,
)
repo = None

def get_total_inputs(inputs, chatbot, preprompt, user_name, assistant_name, sep):
    past = []

    for data in chatbot:
        user_data, model_data = data

        if not user_data.startswith(user_name):
            user_data = user_name + user_data
        if not model_data.startswith(sep + assistant_name):
            model_data = sep + assistant_name + model_data

        past.append(user_data + model_data.rstrip() + sep)

    if not inputs.startswith(user_name):
        inputs = user_name + inputs

    total_inputs = preprompt + "".join(past) + inputs + sep + assistant_name.rstrip()

    return total_inputs


def has_no_history(chatbot, history):
    return not chatbot and not history

info = {"intro":"""An AI Recommondation System platform for responding briefly to Risk Management questions based on Project Management Body of Knowledge """
    ,"description":"""PMBOK stands for the "Project Management Body of Knowledge." It is a set of standard terminology and guidelines (a body of knowledge) for project management. PMBOK is developed and maintained by the Project Management Institute (PMI), a globally recognized professional organization in the field of project management.

The PMBOK Guide provides a framework for project management processes and practices and is widely used in various industries and sectors. It outlines standard practices and processes in project management, covering areas such as project initiation, planning, execution, monitoring and controlling, and project closure.

The PMBOK Guide is typically organized into knowledge areas, each addressing a specific aspect of project management, and process groups, which represent the chronological phases of a project. As of my last knowledge update in January 2022, the latest edition of the PMBOK Guide is the "PMBOK Guide – Seventh Edition."

It's important to note that the field of project management evolves, and updates to the PMBOK Guide may occur. Therefore, you may want to check the latest information and editions from the Project Management Institute (PMI) for the most up-to-date content."""

        }
total_info =  " ".join([f"{key}:{item} \n" for key,item in info.items()])


header = total_info+"""
Assume that your are a Risk Manager:

In PMBOK (Project Management Body of Knowledge) and under the framework of PMI (Project Management Institute), risk management is a crucial knowledge area that involves identifying, analyzing, and responding to project risks. The tasks of a risk manager, or someone responsible for risk management within a project, generally fall into several key areas. Below are some typical tasks associated with the role of a risk manager in the context of PMBOK and PMI:

"""
prompt_template = "### Human:"+header+" {query}\n### Assistant:{response}"


def generate(user_message):
    # Don't return meaningless message when the input is empty
    if not user_message:
        print("Empty input")


    print(user_message)
    past_messages = []


    if len(past_messages) < 1:
        prompt = header+prompt_template.format(query=user_message, response="")
    else:
        prompt = header
        for i in range(0, len(past_messages), 2):
            intermediate_prompt = prompt_template.format(query=past_messages[i]["content"], response=past_messages[i+1]["content"])
            print("intermediate: ", intermediate_prompt)
            prompt = prompt + '\n' + intermediate_prompt

        prompt = prompt + prompt_template.format(query=user_message, response="")


    generate_kwargs = {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_new_tokens": 1024,
    }

    temperature = float(0.7)
    if temperature < 1e-2:
        temperature = 1e-2
    top_p = float(0.9)

    generate_kwargs = dict(
        temperature=temperature,
        max_new_tokens=1024,
        top_p=top_p,
        repetition_penalty=1.2,
        do_sample=True,
        truncate=999,
        seed=42,
    )

    stream = client.generate_stream(
        prompt,
        **generate_kwargs,
    )

    output = ""
    for idx, response in enumerate(stream):
        if response.token.text == '':
            break

        if response.token.special:
            continue
        output += response.token.text



    output.replace("As Risk analyser,","")
    return output



