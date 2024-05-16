import numpy as np
import numpy.linalg as la
import matplotlib.pyplot as plt
import export_to_model


def least_squares(training, labels):
    return np.dot(
        np.dot(
            np.linalg.inv(np.dot(training.transpose(), training)), training.transpose()
        ),
        labels,
    )


def truncated_svd(k_val, y, shape, U, S, Vt):
    w = np.zeros((len(k_val), shape))
    for i, k in enumerate(k_val):
        w[i, :] = (
            np.dot(Vt[0:k, :].T, np.diag(1 / S[0:k])).dot(np.dot(U[:, 0:k].T, y)).T
        )
    return w


X = export_to_model.get_X_features()
y = export_to_model.get_y_labels()
n, p = np.shape(X)

### models

set_count = 100
set_size = 59

### trunc svd

# SVD parameters to test
k_vals = np.arange(9) + 1
param_err_SVD = []
y_hats_svd = []

def truncated_SVD(mat_X):
    for k in k_vals:
        k_error = 0

        # first hold-out
        for h_idx in range(set_count):
            y_hats = []

            w_hats = []
            holdout = np.arange(h_idx * set_size, set_size * h_idx + set_size)

            for h2_idx in range(set_count):
                if h_idx == h2_idx:
                    continue

                holdout2 = np.arange(h2_idx * set_size, set_size * h2_idx + set_size)
                holdout_rows = np.append(holdout, holdout2)

                X_curr = [
                    row for idx, row in enumerate(mat_X) if idx not in holdout_rows
                ]
                y_curr = np.array(
                    [y_val for idx, y_val in enumerate(y) if idx not in holdout_rows]
                )

                U, Sigma, VT = np.linalg.svd(X_curr, full_matrices=False)
                V = VT.T
                Sigma_k_plus = np.reciprocal(Sigma)
                Sigma_k_plus[k:] = 0
                Sigma_k_plus = np.diagflat(Sigma_k_plus)

                w_hat = V @ Sigma_k_plus @ U.T @ y_curr
                y_hat = np.sign(mat_X[holdout2] @ w_hat)
                error = np.count_nonzero(y_hat != y[holdout2])

                w_hats.append((w_hat, error))

            k_w_hat = min(w_hats, key=lambda w: w[1])[0]
            k_y_hat = np.sign(mat_X[holdout] @ k_w_hat)
            y_hats.append(k_y_hat)

            k_error += np.count_nonzero(k_y_hat != y[holdout]) / set_size

        param_err_SVD.append(k_error / (len(k_vals) * set_count))
        y_hats_svd.append(y_hats)

    return np.mean(param_err_SVD)


print(truncated_SVD(X))

try:
    plt.plot(y, c="blue", label="true ped crashes")
    plt.plot(y_hats_svd[0], c="red", label="truncated svd estimate")
    plt.legend()
    plt.show()
except Exception as e:
    print(e)
    pass

### regularized ls

# RLS parameters to test
lambda_vals = np.array([0.125, 0.25, 0.5, 1, 2, 4, 8, 16, 32])
param_err_RLS = []
y_hats_rls = []


def regularized_LS(mat_X, p):
    for l in lambda_vals:
        lambda_error = 0

        for h_idx in range(set_count):
            w_hats = []
            holdout = np.arange(h_idx * set_size, set_size * h_idx + set_size)
            y_hats = []

            for h2_idx in range(set_count):
                if h_idx == h2_idx:
                    continue

                holdout2 = np.arange(h2_idx * set_size, set_size * h2_idx + set_size)
                holdout_rows = np.append(holdout2, holdout)

                X_curr = [
                    row for idx, row in enumerate(mat_X) if idx not in holdout_rows
                ]
                y_curr = np.array(
                    [y_val for idx, y_val in enumerate(y) if idx not in holdout_rows]
                )

                U, S, VT = np.linalg.svd(X_curr, full_matrices=False)
                V = VT.T

                Sigma = np.diagflat(S)

                w_hat = (
                    V
                    @ np.linalg.inv(Sigma.T @ Sigma + l * np.identity(p))
                    @ Sigma.T
                    @ U.T
                    @ y_curr
                )
                y_hat = np.sign(mat_X[holdout2] @ w_hat)
                error = np.count_nonzero(y_hat != y[holdout2])
                w_hats.append((w_hat, error))

            lambda_w_hat = min(w_hats, key=lambda w: w[1])[0]
            lambda_y_hat = np.sign(mat_X[holdout] @ lambda_w_hat)
            y_hats.append(lambda_y_hat)
            lambda_error += np.count_nonzero(lambda_y_hat != y[holdout]) / set_size

        param_err_RLS.append(lambda_error / (len(lambda_vals) * set_count))
        y_hats_rls.append(y_hats)
    return np.mean(param_err_RLS)


print(regularized_LS(X, p))

try:
    plt.plot(y, c="blue", label="true ped crashes")
    plt.plot(y_hats_rls[0], c="red", label="regularized ls estimate")
    plt.legend()
    plt.show()

except Exception as e:
    print(e)
    pass
