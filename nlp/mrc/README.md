# MRC (Machine Reading Comprehension)

## **Project**

<b> Question Answering Project </b>

1. **Type of Question Answering**
>> - Conversational Question Answering
>> - Open-Domain Question Answering
>> - Domain-Specific Question Answering
>> - Multiple Choice Question Answering
>> - <b>Knowledge Base Question Answering (reasoning hop, multi-hop)</b>
>> - Cross-Lingual Question Answering
>> - <b>Visual Question Answering</b>


2. **Type of Datasets**

- PapersWithCode: [link](https://paperswithcode.com/dataset/)
- SQuAD (The Stanford Question Answering Dataset)
    - KorQuAD (Korean)
    - CMRC (The Chinese Machine Reading Comprehension)
    - FQuAD (French)
>> SQuAD 1.0
>> - based on wikipidia documents
>> - represent the answer through `span` of sentences

<br>

>> SQuAD 2.0
>> - Know What You Don't Know: Unanswerable Questions for SQuAD
>> - Add negative 50,000 examples compared to 1.0
>> - [LeaderBoard](https://rajpurkar.github.io/SQuAD-explorer/, "SQuAD 2.0")

<br>

```python
# Example of SQuAD 1.0, 2.0
{
    "answers": {
        "answer_start": [1],
        "text": ["This is a test text"]
    },
    "context": "This is a test context.",
    "id": 1,
    "question": "Is this a test?",
    "title": "train test"
}
```

- MS MARCO (A Human Generated Machine Reading COmprehension Dataset)
    - compared to SQuAD (100,000), it has 10 times more data (1M questions from 8.8M passages).
    - sample questions from the Bing query logs.
    - it does not provide the span inside the datasets.

- Natural Questions (Based on google query data)
    - select wikipidia as the document
    - create diverse types of answer (long, short, yes/no, no answer)

- HotpotQA (A Dataset for Diverse, Explainable Multi-hop Question Answering)
    - bridge entity, answer entity

- NarrativeQA (The NarrativeQA Reading Comprehension Challenge)

- CoQA (A Conversational Question Answering Challenge - Stanford University)
    - representational `conversational` dataset

- CLEVR (Compositional Language and Elementary Visual Reasoning)
    - image, QA pair
    - types of question: identification, count, compare, multiple attention (ex. that is the left of the A thing that is the left of the B)

- VQA (Visual Question Answering)

- `AI Hub` - Korean Dataset

- `KLUE`: Korean Language Understanding Evaluation (Upstage, 2021)
    - Topic Classification (TC)
    - Semantic Textual Similarity (STS)
    - Natural Language Inference (NLI)
    - Named Entity Recognition (NER)
    - Relation Extraction (RE)
    - Dependency Parsing (DP)
    - `Machine Reading Comprehension (MRC)`
    - Dialogue State Tracking (DST)
- KorSciQA: Korean papers MRC dataset (KAIST)

- `KVQA` (Korean Localization of Visual Question Answering for Blind People, SKT Brain)

- `KorQuAD` (The Korean Question Answering Dataset, 2018-2019, LG CNS)
    - Korean Wiki
    - Standard korean question answering dataset
    - KorQuAD 1.0, 2.0
        - 1.0 targets for 1~2 passages, but 2.0 aims to search the answer in the whole wikipedia documents. As a result, 2.0 has to find the answer among the multiple passages.
        - 1.0 uses the data which consists only of the natural language, but 2.0 contains the structurized data such as table or list as well.
        - 2.0 contains longer sentences in the answer dataset, whereas most of the answer in 1.0 consist of several words or short phrases.
        - 2.0 hosts the separate `Latency` leaderboard for checking time performance in data pre-processing and model inference as well as the EM and F1.
    - [LeaderBoard](https://korquad.github.io/)


2. **Model to use**
- BERT (Bidirectional Encoder Representations from Transformer for language understanding)
    - Bert-Base: 12L, 768D, 12N_HEAD = 110M parameters
    - Bert-Large: 24L, 1024D, 16N_HEAD = 340M parameters
    - Embedding Layers:
        - WordPiece Embedding
        - Position Embedding
        - Segment Embedding
    - Trained with two sub-tasks: Next Sentence Prediction and Masked Language Modeling

- ELECTRA (Efficiently Learning an Encoder that classifies Token Replacements Accurately)
    - Introduce RTD (Replaced Token Detection) new pre-training task
    - Problem of Masked Language Modeling (MLM)
        - only 15% of the tokens are masked -> only 15% losses occur -> increase the training cost
        - in reality, no [Mask] token in inference
    - Discriminate real token and fake token
        - all tokens are trained
    - Generator G and Discriminator D share the Transformer Encoder parameters
    - Training with sum of loss from Generator and Discriminator
    - In down-stream task, only fine-tunes the Discriminator
