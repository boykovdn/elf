import unittest
from shutil import rmtree

import numpy as np
from scipy.ndimage import affine_transform
from elf.io import open_file
from elf.util import normalize_index


class TestAffine(unittest.TestCase):
    def tearDown(self):
        try:
            rmtree('tmp.n5')
        except OSError:
            pass

    def _test_2d(self, matrix, chunked=False, sigma=None, **kwargs):
        from elf.transformation import transform_subvolume_affine
        shape = (512, 512)
        x = np.random.rand(*shape)
        exp = affine_transform(x, matrix, **kwargs)

        if chunked:
            f = open_file('tmp.n5')
            x = f.create_dataset('tmp', data=x, chunks=(64, 64))

        bbs = [np.s_[:, :], np.s_[:256, :256], np.s_[37:115, 226:503],
               np.s_[:200, :], np.s_[:, 10:115]]
        for bb in bbs:
            bb, _ = normalize_index(bb, shape)
            res = transform_subvolume_affine(x, matrix, bb, sigma=sigma, **kwargs)
            exp_bb = exp[bb]

            self.assertEqual(res.shape, exp_bb.shape)
            if sigma is None:
                self.assertTrue(np.allclose(res, exp_bb))
            else:
                self.assertTrue(~np.allclose(res, 0))

    def test_affine_subvolume_2d(self):
        from elf.transformation import compute_affine_matrix
        # TODO test more orders once implemented
        orders = [0, 1]
        matrices = [compute_affine_matrix(scale=(2, 2), rotation=(45,)),
                    compute_affine_matrix(scale=(1, 2), rotation=(33,)),
                    compute_affine_matrix(scale=(3, 2), rotation=(137,)),
                    compute_affine_matrix(scale=(.5, 1.5), rotation=(23,),
                                          translation=(23., -14.))]
        for mat in matrices:
            for order in orders:
                self._test_2d(mat, order=order)

    def test_affine_subvolume_2d_chunked(self):
        from elf.transformation import compute_affine_matrix
        mat = compute_affine_matrix(scale=(2, 2), rotation=(45,))
        self._test_2d(mat, order=0, chunked=True)

    def test_presmoothing(self):
        from elf.transformation import compute_affine_matrix
        mat = compute_affine_matrix(scale=(2, 2), rotation=(45,))
        self._test_2d(mat, order=1, chunked=True, sigma=1.)

    def _test_3d(self, matrix, chunked=False, **kwargs):
        from elf.transformation import transform_subvolume_affine
        shape = 3 * (64,)
        x = np.random.rand(*shape)
        exp = affine_transform(x, matrix, **kwargs)

        if chunked:
            f = open_file('tmp.n5')
            x = f.create_dataset('tmp', data=x, chunks=3 * (16,))

        bbs = [np.s_[:, :, :], np.s_[:32, :32, :32], np.s_[1:31, 5:27, 3:13],
               np.s_[4:19, :, 22:], np.s_[1:29], np.s_[:, 15:27, :], np.s_[:, 1:3, 4:14]]
        for bb in bbs:
            bb, _ = normalize_index(bb, shape)
            res = transform_subvolume_affine(x, matrix, bb, **kwargs)
            exp_bb = exp[bb]

            self.assertEqual(res.shape, exp_bb.shape)
            self.assertTrue(np.allclose(res, exp_bb))

    def test_affine_subvolume_3d(self):
        from elf.transformation import compute_affine_matrix
        # TODO test more orders once implemented
        orders = [0, 1]
        matrices = [compute_affine_matrix(scale=(1, 2, 1), rotation=(15, 30, 0)),
                    compute_affine_matrix(scale=(3, 2, .5), rotation=(24, 33, 99)),
                    compute_affine_matrix(scale=(1., 1.3, .79), rotation=(12, -4, 8),
                                          translation=(10.5, 18., -33.2))]
        for mat in matrices:
            for order in orders:
                self._test_3d(mat, order=order)

    def test_affine_subvolume_3d_chunked(self):
        from elf.transformation import compute_affine_matrix
        mat = compute_affine_matrix(scale=(1, 2, 1), rotation=(15, 30, 0))
        self._test_3d(mat, order=0, chunked=True)

    def test_toy(self):
        from elf.transformation import compute_affine_matrix
        from elf.transformation import transform_subvolume_affine
        mat = compute_affine_matrix(scale=(2, 2), rotation=(45,), translation=(-1, 1))
        x = np.random.rand(10, 10)

        bb = np.s_[0:3, 0:3]
        res = transform_subvolume_affine(x, mat, bb, order=1)
        exp = affine_transform(x, mat, order=1)[bb]

        self.assertTrue(np.allclose(res, exp))


if __name__ == '__main__':
    unittest.main()
