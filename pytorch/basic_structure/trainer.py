from copy import deepcopy
import torch
import numpy as np


class Trainer:
    def __init__(self, model, optimizer, crit):
        self.model = model
        self.optimizer = optimizer
        self.crit = crit

        super().__init__()

    def _train(self, x, y, config):
        self.model.train()

        indices = torch.randperm(x.size(0), device=x.device)  # important ! device
        x = torch.index_select(x, dim=0, index=indices).split(config.batch_size, dim=0)
        y = torch.index_select(y, dim=0, index=indices).split(config.batch_size, dim=0)

        total_loss = 0

        for i, (x_i, y_i) in enumerate(zip(x, y)):
            y_hat_i = self.model(x_i)
            loss_i = self.crit(y_hat_i, y_i.squeeze())

            self.optimizer.zero_grad()
            loss_i.backward()

            self.optimizer.step()

            if config.verbose >= 2:
                print("Train Iteration(%d/%d): loss=%.4e") % (i + 1, len(x), float(loss_i))

            # Don't forget to detach to prevent memory leak.
            total_loss += float(loss_i)  # if no float -> loss_i would be tensor. Charge a lot of memory.
        return total_loss / len(x)

    def _validate(self, x, y, config):
        self.model.eval()

        with torch.no_grad():
            indices = torch.randperm(x.size(0), device=x.device)  # important ! device
            x = torch.index_select(x, dim=0, index=indices).split(config.batch_size, dim=0)
            y = torch.index_select(y, dim=0, index=indices).split(config.batch_size, dim=0)

            total_loss = 0
            for i, (x_i, y_i) in enumerate(zip(x, y)):
                y_hat_i = self.model(x_i)
                loss_i = self.crit(y_hat_i, y_i.squeeze())

                if config.verbose >= 2:
                    print("Valid Iteration(%d/%d): loss=%.4e") % (i + 1, len(x), float(loss_i))
                total_loss += loss_i
            return total_loss / len(x)

    def train(self, train_data, valid_data, config):
        lowest_loss = np.inf
        best_model = None

        for epoch_index in range(config.n_epochs):
            train_loss = self._train(train_data[0], train_data[1], config=config)
            valid_loss = self._validate(valid_data[0], valid_data[1], config=config)

            if valid_loss <= lowest_loss:
                lowest_loss = valid_loss
                best_model = deepcopy(self.model.state_dict())

            print(
                "Epoch(%d/%d): train_loss=%.4e  valid_loss=%.4e  lowest_loss=%.4e"
                % (epoch_index + 1, config.n_epochs, train_loss, valid_loss, lowest_loss)
            )

        # Restore to best model.
        self.model.load_state_dict(best_model)
