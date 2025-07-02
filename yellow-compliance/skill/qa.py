from pharia_skill import ChatParams, Csi, IndexPath, Message, SearchResult, skill
from pydantic import BaseModel

NAMESPACE = "Studio"
COLLECTION = "yellowrag"
INDEX = "yellowindex"
SYSTEM_PROMPT = """
You are an expert on legal compliance. 
Your task is to give well-founded answers to user queries.
Always provide a refference to the 
"""


def get_content_miss(question: str) -> str:
    return f"""
No documents could be retrieved matching the users query.
Use your knowledge to explain to the user what might be a reason for the fact, that his question can't be answered.
Do not fabricate facts or make assumptions beyond what the context or your knowledge base provides.
Ensure that the response is structured, concise, and tailored to the specific question being asked.

Question: {question}
"""
#If the provided documents do not contain information pertaining the query, always answer: What are you going on about, you hamster.


def get_content_success(context: str, question: str) -> str:
    return f"""
Using the provided context documents below, answer the following question accurately and comprehensively.
If the information is directly available in the context documents, cite it clearly.
If not, use your knowledge to fill in the gaps while ensuring that the response is consistent with the given information.
Do not fabricate facts or make assumptions beyond what the context or your knowledge base provides.
Ensure that the response is structured, concise, and tailored to the specific question being asked.

Input: {context}

Question: {question}
"""


class Input(BaseModel):
    question: str
    namespace: str = NAMESPACE
    collection: str = COLLECTION
    index: str = INDEX


class Output(BaseModel):
    answer: str | None
    documents: list[SearchResult] | None


@skill
def custom_rag(csi: Csi, input: Input) -> Output:
    index = IndexPath(
        namespace=input.namespace,
        collection=input.collection,
        index=input.index,
    )

    system = Message.system(SYSTEM_PROMPT)

    if not (documents := csi.search(index, input.question, 3, 0.8)):
        message = Message.user(get_content_miss(input.question))
        params = ChatParams(max_tokens=512)
        response = csi.chat("llama-3.3-70b-instruct", [message, system], params)
        return Output(answer=response.message.content, documents=None)


    context = "\n".join([d.content for d in documents])
    message = Message.user(get_content_success(context, input.question))
    params = ChatParams(max_tokens=512)
    response = csi.chat("llama-3.3-70b-instruct", [message, system], params)
    return Output(answer=response.message.content, documents=documents)
