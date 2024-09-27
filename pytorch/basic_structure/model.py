import torch.nn as nn


class ImageClassifier(nn.Module):
    def __init__(self, input_size, output_size):
        self.input_size = input_size
        self.output_size = output_size

        super().__init__()

        self.layers = nn.Sequential(
            nn.Linear(in_features=input_size, out_features=500),
            nn.LeakyReLU(),
            # BatchNorm1d의 경우 Input과 Output이 (N, C) 또는 (N, C, L)의 형태를 가지고 BatchNorm2d의 경우 Input과 Output이 (N, C, H, W)의 형태를 가집니다. 여기서 N은 Batch의 크기를 말하고 C는 Channel을 말합니다.
            nn.BatchNorm1d(num_features=500),
            nn.Linear(500, 400),
            nn.LeakyReLU(),
            nn.BatchNorm1d(400),
            nn.Linear(400, 300),
            nn.LeakyReLU(),
            nn.BatchNorm1d(300),
            nn.Linear(300, 200),
            nn.LeakyReLU(),
            nn.BatchNorm1d(200),
            nn.Linear(200, 100),
            nn.LeakyReLU(),
            nn.BatchNorm1d(100),
            nn.Linear(100, 50),
            nn.LeakyReLU(),
            nn.BatchNorm1d(50),
            nn.Linear(50, output_size),
            nn.LogSoftmax(dim=-1),  # batch_size * dimension <- softmax only to "dimension"
        )

    def forward(self, x):
        # input: |x| = (batch_size, input_size)
        y = self.layers(x)
        # output: |y| = (batch_size, output_size)
        return y


if __name__ == "__main__":
    model = ImageClassifier(28 * 28, 10)
    print(model.state_dict())
