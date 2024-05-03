import streamlit as st
from openai import OpenAI
import constants
from tqdm import tqdm


def gen_chunks(max_tokens=4096, limit=None):
    chunks = []
    chunk = ""
    with open(filename, "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if limit and i >= limit:
                break
            if len(chunk) + len(line) > max_tokens - 250:
                chunks.append(chunk)
                chunk = line
            elif line == lines[-1]:
                chunk += line
                chunks.append(chunk)
            else:
                chunk += line
    return chunks


def main():
    client = OpenAI(
        api_key=constants.APIKEY
    )

    GPT4 = "gpt-4-turbo-preview"

    gpt_msgs = []
    chunks = gen_chunks(limit=600)  # Truncate records to 50

    for i, chunk in enumerate(tqdm(chunks)):
        gpt_msgs.append({"role": "user",
                         "content": f"Here is a chunk {i} of {len(chunks)} of a CSV dataset. Respond with OK to "
                                    f"acknowledge that you have received this chunk. Remember each line that I give you"
                                    f"and their line number. Do not explain the data. Here is the data: \n{chunk}"})

    recommendations = \
        """
        I present you the message suppression (MS) attack, denial-of-
        service (DoS) attack, network error (NE), for GOOSE communications. 
        
        These attacks can be described as follows. A failure to satisfy at least one
        recommendation leads to the relevant attack.
        
        Attacks/errors on GOOSE datasets:
        - MS: the stNum value is higher or slightly higher than the previously recorded stNum, 
        and sqNum is not 0.
        - MS: Replaying a previously valid GOOSE frame that contains a high stNum and sqNum is 0, but has a stale timestamp.
        - MS: When a frame has a high stNum and sqNum is 0, and there is a valid timestamp.
        - MS: When a frame has a high sqNum causes GOOSE frames to arrive at the receiver out of sequence.
        - DoS: Up to 10 packets are sent within 10 ms.
        - NE: There should be a packet (dataset) within 10s.
        """

    gpt_msgs.extend([
        {"role": "system",
         "content": "You will detect anomalies in patterns in sets of GOOSE messages, you will be given "
                    "anomaly recommendations. You will need to follow the instructions for the "
                    "recommendations-- if you need to check a field on the next row for a recommendation, "
                    "you need to do that. If a pattern shows up that matches something in the "
                    "recommendations, then you need to acknowledge that you've found an anomaly. "
                    "Reply with either 'MS', 'DoS', 'NE' or 'Other' depending on the type of anomaly. "
                    "If there is no anomaly, reply with 'Normal'. Concisely explain your reasoning, "
                    "stating in which line the violation happened. You need to be sure that you carefully look at "
                    "each line in detail so that you do not make generalizations over hundreds of lines. Be sure that "
                    "you state how many anomalies there are, if any, by looking at each line."},
        {"role": "user",
         "content": f"Here are the anomaly recommendations while analyzing each line:\n{recommendations} "
                    f"You have already been given a dataset of GOOSE messages. Look at the context of "
                    f"the previous lines when checking for anomalies. If you detect an anomaly based on "
                    f"the provided recommendations, state the type of anomaly (e.g., 'MS', 'DoS', 'NE', "
                    f"'Other') and specify the line numbers where the violation occurred. If there is "
                    f"no anomaly, reply with 'Normal'. Make sure to check yourself to make sure you "
                    f"don't contradict yourself."}
    ])
    
    response = client.chat.completions.create(
        model=GPT4,
        messages=gpt_msgs
    )
    results = response.choices[0].message.content
    gpt_msgs.append(
        {"role": "assistant",
         "content": results}
    )

    # st.header("AI Chat with GPT-4 for Anomaly Detection in GOOSE Protocol")
    # st.markdown("Powered by OpenAI LLM")

    st.header("💬 AI Chat with GPT-4 for Anomaly Detection in GOOSE Protocol", divider='rainbow')
    st.markdown("🚀 A Streamlit chatbot powered by OpenAI LLM")
    
    st.header("AI's Response:")
    with st.chat_message("assistant"):
        st.write(results)

    with st.chat_message("user"):
        query = st.text_input("Prompt:", key="prompt-question")
    if query and query not in ["q", "quit"]:
        gpt_msgs.append(
            {"role": "user",
             "content": query}
        )
        resp = client.chat.completions.create(
            model=GPT4,
            messages=gpt_msgs
        )
        res = resp.choices[0].message.content
        gpt_msgs.append(
            {"role": "assistant",
             "content": res}
        )
        st.header("AI's Response:")
        with st.chat_message("assistant"):
            st.write(res)


if __name__ == "__main__":
    filename = r"data/as1.csv"
    main()
