import torch.nn as nn


class SequenceClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, n_layers=4, dropout_p=0.2):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.n_layers = n_layers
        # RNN cannot use BatchNorm
        self.dropout_p = dropout_p

        super().__init__()

        # |x| = (batch_size, time_step, input_size)
        # |y| = (batch_size, time_step, hidden_size * 2)
        self.rnn = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=n_layers,
            batch_first=True,
            dropout=dropout_p,
            bidirectional=True,
        )

        self.layers = nn.Sequential(
            nn.ReLU(), nn.BatchNorm1d(hidden_size * 2), nn.Linear(hidden_size * 2, output_size), nn.LogSoftmax(dim=-1)
        )

    def forward(self, x):
        # |x| = (batch_size, h, w)

        z, _ = self.rnn(x)
        # |z| = (batch_size, h, hidden_size * 2)

        z = z[:, -1]
        # |z| = (batch_size, hidden_size * 2)

        y = self.layers(z)
        # |y| = (batch_size, output_size)

        return y
