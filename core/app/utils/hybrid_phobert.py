import torch.nn as nn

from transformers import AutoModel
from transformers.modeling_outputs import SequenceClassifierOutput


class HybridPhoBERTClassifier(nn.Module):

    def __init__(
        self,
        model_name="vinai/phobert-base-v2",
        num_labels=3
    ):
        super().__init__()

        self.bert = AutoModel.from_pretrained(model_name)

        self.dropout = nn.Dropout(0.3)

        self.classifier = nn.Sequential(
            nn.Linear(self.bert.config.hidden_size, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_labels)
        )

    def forward(
        self,
        input_ids,
        attention_mask=None
    ):

        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        sentence_rep = outputs.last_hidden_state[:, 0]

        x = self.dropout(sentence_rep)

        logits = self.classifier(x)

        return SequenceClassifierOutput(
            logits=logits
        )