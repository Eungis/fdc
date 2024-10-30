def get_grad_norm(parameters, norm_type=2):
    parameters = list(filter(lambda p: p.grad is not None, parameters))

    total_norm = 0
    try:
        for p in parameters:
            param_norm = p.data.norm(norm_type)
            total_norm += param_norm**norm_type
        total_norm = total_norm ** (1.0 / norm_type)
    except Exception as e:
        print(e)
    return total_norm


def get_parameters_norm(parameters, norm_type=2):
    # parameters: generator
    # p for p in parameters():
    # p - tensor + required_grad
    # p.data
    # p.grad (IF HASN'T BEEN BACK-PROPAGATED, p.grad = None)
    # p.data.shape = tensor(out_features, in_features) (500, 784)
    # p.grad.shape = tensor(out_features, in_features) (500, 784)
    total_norm = 0
    try:
        for p in parameters:
            param_norm = p.data.norm(norm_type)
            total_norm += param_norm**norm_type
        total_norm = total_norm ** (1.0 / norm_type)
    except Exception as e:
        print(e)
    return total_norm
