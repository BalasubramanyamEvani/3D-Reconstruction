import numpy as np
import matplotlib.pyplot as plt

from helper import camera2
from q2_1_eightpoint import eightpoint
from q3_1_essential_matrix import essentialMatrix

# Insert your package here


"""
Q3.2: Triangulate a set of 2D coordinates in the image to a set of 3D points.
    Input:  C1, the 3x4 camera matrix
            pts1, the Nx2 matrix with the 2D image coordinates per row
            C2, the 3x4 camera matrix
            pts2, the Nx2 matrix with the 2D image coordinates per row
    Output: P, the Nx3 matrix with the corresponding 3D points per row
            err, the reprojection error.

    Hints:
    (1) For every input point, form A using the corresponding points from pts1 & pts2 and C1 & C2
    (2) Solve for the least square solution using np.linalg.svd
    (3) Calculate the reprojection error using the calculated 3D points and C1 & C2 (do not forget to convert from 
        homogeneous coordinates to non-homogeneous ones)
    (4) Keep track of the 3D points and projection error, and continue to next point 
    (5) You do not need to follow the exact procedure above. 
"""


def triangulate(C1, pts1, C2, pts2):
    # Replace pass by your implementation
    # ----- TODO -----
    p11 = C1[0, :][:, np.newaxis]
    p12 = C1[1, :][:, np.newaxis]
    p13 = C1[2, :][:, np.newaxis]

    p21 = C2[0, :][:, np.newaxis]
    p22 = C2[1, :][:, np.newaxis]
    p23 = C2[2, :][:, np.newaxis]

    num_points = pts1.shape[0]

    P = np.zeros((num_points, 4))
    err = 0
    Ai = np.zeros((4, 4))
    for i in range(num_points):
        x1i, x2i = pts1[i, :], pts2[i, :]
        Ai[0, :] = x1i[1] * p13.T - p12.T
        Ai[1, :] = p11.T - x1i[0] * p13.T
        Ai[2, :] = x2i[1] * p23.T - p22.T
        Ai[3, :] = p21.T - x2i[0] * p23.T

        u, s, vt = np.linalg.svd(Ai)
        vt = vt[-1] / vt[-1, -1]
        P[i, :] = vt
        vt = vt[:, np.newaxis]

        x1ihat = C1 @ vt
        x1ihat = x1ihat[:-1] / x1ihat[-1]

        x2ihat = C2 @ vt
        x2ihat = x2ihat[:-1] / x2ihat[-1]

        err += (
            np.linalg.norm(x1i - x1ihat.T, ord=2) ** 2
            + np.linalg.norm(x2i - x2ihat.T, ord=2) ** 2
        )

    return P[:, :3], err


"""
Q3.3:
    1. Load point correspondences
    2. Obtain the correct M2
    3. Save the correct M2, C2, and P to q3_3.npz
"""


def findM2(F, pts1, pts2, intrinsics, filename="q3_3.npz"):
    """
    Q2.2: Function to find camera2's projective matrix given correspondences
        Input:  F, the pre-computed fundamental matrix
                pts1, the Nx2 matrix with the 2D image coordinates per row
                pts2, the Nx2 matrix with the 2D image coordinates per row
                intrinsics, the intrinsics of the cameras, load from the .npz file
                filename, the filename to store results
        Output: [M2, C2, P] the computed M2 (3x4) camera projective matrix, C2 (3x4) K2 * M2, and the 3D points P (Nx3)

    ***
    Hints:
    (1) Loop through the 'M2s' and use triangulate to calculate the 3D points and projection error. Keep track
        of the projection error through best_error and retain the best one.
    (2) Remember to take a look at camera2 to see how to correctly reterive the M2 matrix from 'M2s'.
    """
    # ----- TODO -----
    # YOUR CODE HERE
    K1, K2 = intrinsics["K1"], intrinsics["K2"]
    M1 = np.eye(4)[:-1, :]
    E = essentialMatrix(F, K1, K2)
    M2s = camera2(E)
    num_M2s = M2s.shape[-1]
    best_index = -1
    C1 = K1 @ M1
    for i in range(num_M2s):
        C2 = K2 @ M2s[:, :, i]
        P, err = triangulate(C1, pts1, C2, pts2)
        if np.all(P[:, -1]) > 0:
            best_index = i
    M2 = M2s[:, :, best_index]
    C2 = K2 @ M2
    P, err = triangulate(C1, pts1, C2, pts2)

    return M2, C2, P


if __name__ == "__main__":
    correspondence = np.load("data/some_corresp.npz")  # Loading correspondences
    intrinsics = np.load("data/intrinsics.npz")  # Loading the intrinscis of the camera
    K1, K2 = intrinsics["K1"], intrinsics["K2"]
    pts1, pts2 = correspondence["pts1"], correspondence["pts2"]
    im1 = plt.imread("data/im1.png")
    im2 = plt.imread("data/im2.png")

    F = eightpoint(pts1, pts2, M=np.max([*im1.shape, *im2.shape]))

    M2, C2, P = findM2(F, pts1, pts2, intrinsics)

    # Simple Tests to verify your implementation:
    M1 = np.hstack((np.identity(3), np.zeros(3)[:, np.newaxis]))
    C1 = K1.dot(M1)
    C2 = K2.dot(M2)
    P_test, err = triangulate(C1, pts1, C2, pts2)
    assert err < 500
    filename = "q3_3.npz"
    np.savez(filename, M2=M2, C2=C2, P=P)
