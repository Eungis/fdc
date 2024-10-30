import torch


def load_mnist(is_train=True, flatten=True):
    from torchvision import datasets, transforms

    dataset = datasets.MNIST(
        root="../data", train=is_train, download=True, transform=transforms.Compose([transforms.ToTensor()])
    )

    x = dataset.data.float() / 255
    y = dataset.targets

    if flatten:
        x = x.view(x.size(0), -1)
    return x, y


if __name__ == "__main__":
    x, y = load_mnist(is_train=True, flatten=True)
    print(x.shape, y.shape)
    print(y)

    indices = torch.randperm(x.size(0), device=x.device)  # important ! device
    x = torch.index_select(x, dim=0, index=indices).split(128, dim=0)
    y = torch.index_select(y, dim=0, index=indices).split(128, dim=0)
    print(x[0].shape)
    print(y[0].shape)
