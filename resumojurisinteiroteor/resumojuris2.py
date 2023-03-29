import openai
from time import time,sleep
import re
import nltk
nltk.download('punkt')


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


openai.api_key = open_file('openaiapikey.txt')


def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def gpt3_completion(prompt, engine='text-davinci-003', temp=0.4, top_p=1.0, TOKENS=1150, freq_pen=0, pres_pen=0.0, stop=['<<END>>'], max_retry=5):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=TOKENS,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            with open('gpt3_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


if __name__ == '__main__':
    alltext = open_file('input.txt')
    sentence_list = nltk.sent_tokenize(alltext)
    chunks = []
    output = []
    count = 0

    CHUNK_SIZE = 19
    CHUNK_LEN = 0
    chunk = []

    for sentence in sentence_list:
        if CHUNK_LEN + len(sentence) > 2850 and CHUNK_LEN > 0:
            chunks.append(" ".join(chunk))
            chunk = []
            CHUNK_LEN = 0

        chunk.append(sentence)
        CHUNK_LEN += len(sentence)

        if len(chunk) >= CHUNK_SIZE or CHUNK_LEN > 3050:
            chunks.append(" ".join(chunk))
            chunk = []
            CHUNK_LEN = 0

    if chunk:
        chunks.append(" ".join(chunk))

    for chunk in chunks:
        count += 1
        prompt = open_file('prompt.txt').replace('<<SUMMARY>>', chunk)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        summary = gpt3_completion(prompt)
        print('\n\n\n', count, 'of', len(chunks), ' - ', summary)
        output.append(summary)
    save_file('\n\n'.join(output), 'output_%d.txt' % int(time()))