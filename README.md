# Regulatory Compliance Q&A with PhariaAi

## Task

Build a **Regulatory Q&A System** that:

1. Accepts a regulatory question in a chat-like input.  
2. Retrieves the most relevant passages from a pre-indexed **ObliQA** structured regulatory document corpus.  
3. Returns a comprehensive answer that synthesizes information from multiple relevant passages, demonstrating the ability to handle questions that require cross-referencing different sections and documents.  
4. **Formats the response clearly** with:
   - A well-structured answer that directly addresses the question
   - **Proper citations** for all referenced passages (Document ID and Passage ID)
   - **Explanations** of how each cited source contributes to the answer
   - Clear delineation between different regulatory requirements or aspects
5. Is exposed to end-users as a **custom application inside Pharia Assistant**.

**Key Challenge**: The system must effectively handle complex questions that require information from multiple chunks and sections across the knowledge base, demonstrating advanced retrieval and synthesis capabilities.

**Deliverables**

- A functioning Pharia Custom Application that runs the Q&A pipeline end-to-end.  
- Benchmarked solution on PhariaStudio demonstrating quality metrics of your choice on the provided test set.
- Present your solution at the end of the workshop.

**Tools & Data Provided**

- Pre-structured ObliQA regulatory documents (JSON format with hierarchical passage structure).  
- A test dataset (`ObliQA_test.json`) containing questions with ground truth passages for evaluation.  
- PhariaAI

---

## Prerequisites

- ✅ Completed **PhariaAcademy Learning** course.  
- ✅ Understand the core components of PhariaAI (PhariaStudio, PhariaKernel, PhariaAssistant).  
- ✅ Finish the technical setup along with the [E2e tutorial](https://github.com/Aleph-Alpha/tutorials/tree/main).  

---

## Data Availability and Access

| Dataset | Contents | Access Method |
|---------|----------|---------------|
| `StructuredRegulatoryDocuments.zip` | 40 structured regulatory documents in JSON format with hierarchical passage IDs | Available as a compressed archive in `/data` directory |
| `ObliQA_test.json` | Test questions with ground truth passages for evaluation | Available in `/data` directory |

### About the ObliQA Dataset

The **ObliQA (Obligation-based Question-Answering) Dataset** is a specialized resource designed for regulatory NLP systems. It leverages regulatory documents from Abu Dhabi Global Markets (ADGM), which set regulations for financial services in the UAE free zones.

For more details about the dataset construction and methodology, see the [ObliQA Dataset GitHub repository](https://github.com/RegNLP/ObliQADataset).

### Data Structure

**Regulatory Documents**: Each document in `StructuredRegulatoryDocuments/` contains:
- `ID`: Unique identifier for the passage
- `DocumentID`: Document number (1-40)
- `PassageID`: Hierarchical passage identifier (e.g., "1.2.1.(a)")
- `Passage`: The actual text content

**Test Data**: Each entry in `ObliQA_test.json` contains:
- `QuestionID`: Unique question identifier
- `Question`: The regulatory question
- `Passages`: Array of relevant passages with DocumentID and PassageID
- `Group`: Question category

---

## Tools

- **Pharia Custom Application template** – quickest way to scaffold the chat UI and connect your flow.  
- **PhariaStudio** – develop, debug and benchmark your solution.  
- **PhariaSearch Document Index** – store document embeddings; experiment with various retrieval strategies to handle multi-passage questions.   
- **PhariaAssistant** – Use the PhariaAssistant to deploy and showcase your solution.

Full documentation lives at [Aleph Alpha Docs](https://docs.aleph-alpha.com/).

---

## Models Available

You may use **any model** visible in your **PhariaStudio Playground** workspace, including:

- Generation Models (e.g., `llama-3.1-8b-instruct`, `llama-3.3-70b-instruct`, etc.)  
- Embedding Models (e.g., `pharia-1-embedding-4608-control`, `pharia-1-embedding-256-control`)

Select the model in your flow configuration or switch interactively in the Playground.



---

## ⚙️ Setup Instructions

### Step 1: Create a PhariaAI Application

Follow the official [Pharia Applications Quick Start Guide](https://docs.aleph-alpha.com/products/pharia-ai/pharia-studio/tutorial/pharia-applications-quick-start/) to create a new application in Pharia Studio.

---

### Step 2: Set Up the Data

Extract and prepare the regulatory documents for indexing:

* Extract the `StructuredRegulatoryDocuments.zip` file from the `/data` directory.
* Review the document structure to understand the hierarchical passage IDs.
* Prepare the documents for indexing into PhariaSearch Document Index.

---

### Step 3: Build a Generation Skill

#### 3.1 Upload Documents to Document Indexing (DI)

* Create a **Collection** and **Index** in DI.
* Upload the structured regulatory documents:
  * Use the `Passage` field as the **document content**.
  * Include `DocumentID` and `PassageID` as **document metadata**.
  * Consider the hierarchical structure when designing your indexing strategy.

#### 3.2 Prompt Engineering

* Design system and user prompts for retrieval-augmented generation.
* Include instructions for:
  * Synthesizing information from multiple passages
  * Proper citation formatting (Document ID and Passage ID)
  * Clear explanation of how each source contributes to the answer

#### 3.3 Evaluate the Skill (DevCsi & Benchmarking)

##### a. Wrap Skill as an Evaluation Task

Instead of querying through the deployed skill, use `DevCsi` to wrap the logic in a `Task`.

```python
from intelligence_layer.core import NoOpTracer, Task, TaskSpan
from pharia_skill.testing import DevCsi
from qa import Input, Output, regulatory_qa

class RegulatoryQATask(Task[Input, Output]):
    def __init__(self) -> None:
        self.dev_csi = DevCsi().with_studio(project=PHARIA_STUDIO_PROJECT_NAME)

    def do_run(self, input: Input, task_span: TaskSpan) -> Output:
        start_time = time.time()
        output = regulatory_qa(self.dev_csi, input)
        duration = time.time() - start_time

        return Output(answer=output.answer, citations=output.citations, duration=duration)
```

##### b. Create Evaluation Dataset

* Use the provided `ObliQA_test.json` test dataset.
* Each entry includes a question and ground truth passages for evaluation.

##### c. Define Evaluation & Aggregation Logic

* Implement metrics to evaluate:
  * Answer quality and completeness
  * Citation accuracy (correct Document IDs and Passage IDs)
  * Retrieval effectiveness (relevant passages found)
* Track additional metrics like generation latency.

##### d. Run Benchmarks

Once the task and evaluation logic are in place, benchmark across:

* Different models.
* Prompt templates and variations.
* Retrieval strategies (number of chunks, similarity thresholds).

---

### Step 4: Deploy the Skill

Ensure you've defined all required environment variables in your `.env` file:

```env
PHARIA_AI_TOKEN=
PHARIA_KERNEL_ADDRESS=

SKILL_REGISTRY=
SKILL_REPOSITORY=
SKILL_REGISTRY_USER=
SKILL_REGISTRY_TOKEN=
```

Then use the `pharia-skill` CLI to:

```bash
pharia-skill build qa
pharia-skill publish qa.wasm --name regulatory-qa
```

Update the `namespace.toml` file with your skill's name. You can now test the deployed skill using the `PhariaKernel` API.

---

### Step 5: Update the UI

Once the skill is live:

* Connect the UI to the skill endpoint.
* Modify the frontend to:
  * Display the **formatted answer** with proper structure.
  * Show **citations** clearly with Document ID and Passage ID.
  * Present **source explanations** for transparency.
  * Handle multi-passage responses effectively.

---

### Step 6: Run Application in Preview Mode

Use the following script to test your application locally:

```bash
npx @aleph-alpha/pharia-ai-cli preview
```

---

### Step 7: Deploy the Application to Pharia Assistant

Before deployment:

* Ensure your `.env` file includes all required credentials and config variables:

```env
PHARIA_AI_TOKEN=
PHARIAOS_MANAGER_URL=

IMAGE_REGISTRY=
IMAGE_REPOSITORY=
IMAGE_REGISTRY_USER=
IMAGE_REGISTRY_PASSWORD=
```

* Build and deploy:

```bash
npx @aleph-alpha/pharia-ai-cli publish
npx @aleph-alpha/pharia-ai-cli deploy
```

---

## 🏁 You're Done!

You now have a working Regulatory Q&A System powered by PhariaAI! Users can submit regulatory questions and receive comprehensive, well-cited answers synthesized from multiple sources.


**Citation:**
```bibtex
@misc{gokhan2024riragregulatoryinformationretrieval,
      title={RIRAG: Regulatory Information Retrieval and Answer Generation}, 
      author={Tuba Gokhan and Kexin Wang and Iryna Gurevych and Ted Briscoe},
      year={2024},
      eprint={2409.05677},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2409.05677}, 
}
```