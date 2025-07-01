from pharia_skill import ChatParams, Csi, IndexPath, Message, skill
from pydantic import BaseModel

NAMESPACE = "Studio"
#COLLECTION = "yellowrag"
COLLECTION = "pharia-tutorial-rag"
#INDEX = "yellowindex"
INDEX = "rag-tutorial-index"


class Input(BaseModel):
    question: str
    namespace: str = NAMESPACE
    collection: str = COLLECTION
    index: str = INDEX


class Output(BaseModel):
    answer: str | None


@skill
def custom_rag(csi: Csi, input: Input) -> Output:
    index = IndexPath(
        namespace=input.namespace,
        collection=input.collection,
        index=input.index,
    )

    if not (documents := csi.search(index, input.question, 3, 0.5)):
        return Output(answer=None)

    context = "\n".join([d.content for d in documents])
    content = f"""Using the provided context documents below, answer the following question accurately and comprehensively. If the information is directly available in the context documents, cite it clearly. If not, use your knowledge to fill in the gaps while ensuring that the response is consistent with the given information. Do not fabricate facts or make assumptions beyond what the context or your knowledge base provides. Ensure that the response is structured, concise, and tailored to the specific question being asked.

Input: {context}

Question: {input.question}
"""
    message = Message.user(content)
    systemprompt = "You are an expert on legal compliance. Your task is to give well-founded answers to user queries. If the provided documents do not contain information pertaining the query, always answer: What are you going on about, you hamster."
    system = Message.system(systemprompt)
    params = ChatParams(max_tokens=512)
    response = csi.chat("llama-3.3-70b-instruct", [message, system], params)
    return Output(answer=response.message.content)
