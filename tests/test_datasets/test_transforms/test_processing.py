import os.path as osp
from unittest import TestCase

import numpy as np
import torch
import torchvision
from mmengine.dataset.base_dataset import Compose
from mmengine.utils import digit_version
from PIL import Image
from torchvision import transforms

from diffengine.datasets.transforms.processing import VISION_TRANSFORMS
from diffengine.registry import TRANSFORMS


class TestVisionTransformWrapper(TestCase):

    def test_register(self):
        for t in VISION_TRANSFORMS:
            self.assertIn('torchvision/', t)
            self.assertIn(t, TRANSFORMS)

    def test_transform(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        data = {'img': Image.open(img_path)}

        # test normal transform
        vision_trans = transforms.RandomResizedCrop(224)
        vision_transformed_img = vision_trans(data['img'])
        trans = TRANSFORMS.build(
            dict(type='torchvision/RandomResizedCrop', size=224))
        transformed_img = trans(data)['img']
        np.equal(np.array(vision_transformed_img), np.array(transformed_img))

        # test convert type dtype
        data = {'img': torch.randn(3, 224, 224)}
        vision_trans = transforms.ConvertImageDtype(torch.float)
        vision_transformed_img = vision_trans(data['img'])
        trans = TRANSFORMS.build(
            dict(type='torchvision/ConvertImageDtype', dtype='float'))
        transformed_img = trans(data)['img']
        np.equal(np.array(vision_transformed_img), np.array(transformed_img))

        # test transform with interpolation
        data = {'img': Image.open(img_path)}
        if digit_version(torchvision.__version__) > digit_version('0.8.0'):
            from torchvision.transforms import InterpolationMode
            interpolation_t = InterpolationMode.NEAREST
        else:
            interpolation_t = Image.NEAREST
        vision_trans = transforms.Resize(224, interpolation_t)
        vision_transformed_img = vision_trans(data['img'])
        trans = TRANSFORMS.build(
            dict(type='torchvision/Resize', size=224, interpolation='nearest'))
        transformed_img = trans(data)['img']
        np.equal(np.array(vision_transformed_img), np.array(transformed_img))

        # test compose transforms
        data = {'img': Image.open(img_path)}
        vision_trans = transforms.Compose([
            transforms.Resize(176),
            transforms.RandomHorizontalFlip(),
            transforms.PILToTensor(),
            transforms.ConvertImageDtype(torch.float),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        vision_transformed_img = vision_trans(data['img'])

        pipeline_cfg = [
            dict(type='torchvision/Resize', size=176),
            dict(type='RandomHorizontalFlip'),
            dict(type='torchvision/PILToTensor'),
            dict(type='torchvision/ConvertImageDtype', dtype='float'),
            dict(
                type='torchvision/Normalize',
                mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225),
            )
        ]
        pipeline = [TRANSFORMS.build(t) for t in pipeline_cfg]
        pipe = Compose(transforms=pipeline)
        transformed_img = pipe(data)['img']
        np.equal(np.array(vision_transformed_img), np.array(transformed_img))


class TestSaveImageShape(TestCase):

    def test_register(self):
        self.assertIn('SaveImageShape', TRANSFORMS)

    def test_transform(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        data = {'img': Image.open(img_path)}
        ori_img_shape = [data['img'].height, data['img'].width]

        # test transform
        trans = TRANSFORMS.build(dict(type='SaveImageShape'))
        data = trans(data)
        self.assertListEqual(data['ori_img_shape'], ori_img_shape)


class TestComputeTimeIds(TestCase):

    def test_register(self):
        self.assertIn('ComputeTimeIds', TRANSFORMS)

    def test_transform(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        img = Image.open(img_path)
        data = {'img': img, 'ori_img_shape': [32, 32], 'crop_top_left': [0, 0]}

        # test transform
        trans = TRANSFORMS.build(dict(type='ComputeTimeIds'))
        data = trans(data)
        self.assertListEqual(data['time_ids'],
                             [32, 32, 0, 0, img.height, img.width])


class TestRandomCrop(TestCase):
    crop_size = 32

    def test_register(self):
        self.assertIn('RandomCrop', TRANSFORMS)

    def test_transform(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        data = {'img': Image.open(img_path)}

        # test transform
        trans = TRANSFORMS.build(dict(type='RandomCrop', size=self.crop_size))
        data = trans(data)
        self.assertIn('crop_top_left', data)
        assert len(data['crop_top_left']) == 2
        assert data['img'].height == data['img'].width == self.crop_size
        upper, left = data['crop_top_left']
        lower, right = data['crop_bottom_right']
        assert lower == upper + self.crop_size
        assert right == left + self.crop_size
        np.equal(
            np.array(data['img']),
            np.array(Image.open(img_path).crop((left, upper, right, lower))))

    def test_transform_multiple_keys(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        data = {
            'img': Image.open(img_path),
            'condition_img': Image.open(img_path)
        }

        # test transform
        trans = TRANSFORMS.build(
            dict(
                type='RandomCrop',
                size=self.crop_size,
                keys=['img', 'condition_img']))
        data = trans(data)
        self.assertIn('crop_top_left', data)
        assert len(data['crop_top_left']) == 2
        assert data['img'].height == data['img'].width == self.crop_size
        upper, left = data['crop_top_left']
        lower, right = data['crop_bottom_right']
        assert lower == upper + self.crop_size
        assert right == left + self.crop_size
        np.equal(
            np.array(data['img']),
            np.array(Image.open(img_path).crop((left, upper, right, lower))))
        np.equal(np.array(data['img']), np.array(data['condition_img']))


class TestCenterCrop(TestCase):
    crop_size = 32

    def test_register(self):
        self.assertIn('CenterCrop', TRANSFORMS)

    def test_transform(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        data = {'img': Image.open(img_path)}

        # test transform
        trans = TRANSFORMS.build(dict(type='CenterCrop', size=self.crop_size))
        data = trans(data)
        self.assertIn('crop_top_left', data)
        assert len(data['crop_top_left']) == 2
        assert data['img'].height == data['img'].width == self.crop_size
        upper, left = data['crop_top_left']
        lower, right = data['crop_bottom_right']
        assert lower == upper + self.crop_size
        assert right == left + self.crop_size
        np.equal(
            np.array(data['img']),
            np.array(Image.open(img_path).crop((left, upper, right, lower))))

    def test_transform_multiple_keys(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        data = {
            'img': Image.open(img_path),
            'condition_img': Image.open(img_path)
        }

        # test transform
        trans = TRANSFORMS.build(
            dict(
                type='CenterCrop',
                size=self.crop_size,
                keys=['img', 'condition_img']))
        data = trans(data)
        self.assertIn('crop_top_left', data)
        assert len(data['crop_top_left']) == 2
        assert data['img'].height == data['img'].width == self.crop_size
        upper, left = data['crop_top_left']
        lower, right = data['crop_bottom_right']
        assert lower == upper + self.crop_size
        assert right == left + self.crop_size
        np.equal(
            np.array(data['img']),
            np.array(Image.open(img_path).crop((left, upper, right, lower))))
        np.equal(np.array(data['img']), np.array(data['condition_img']))


class TestRandomHorizontalFlip(TestCase):

    def test_register(self):
        self.assertIn('RandomHorizontalFlip', TRANSFORMS)

    def test_transform(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        data = {
            'img': Image.open(img_path),
            'crop_top_left': [0, 0],
            'crop_bottom_right': [10, 10]
        }

        # test transform
        trans = TRANSFORMS.build(dict(type='RandomHorizontalFlip', p=1.))
        data = trans(data)
        self.assertIn('crop_top_left', data)
        assert len(data['crop_top_left']) == 2
        self.assertListEqual(data['crop_top_left'],
                             [0, data['img'].width - 10])

        np.equal(
            np.array(data['img']),
            np.array(Image.open(img_path).transpose(Image.FLIP_LEFT_RIGHT)))

        # test transform p=0.0
        data = {
            'img': Image.open(img_path),
            'crop_top_left': [0, 0],
            'crop_bottom_right': [10, 10]
        }
        trans = TRANSFORMS.build(dict(type='RandomHorizontalFlip', p=0.))
        data = trans(data)
        self.assertIn('crop_top_left', data)
        self.assertListEqual(data['crop_top_left'], [0, 0])

        np.equal(np.array(data['img']), np.array(Image.open(img_path)))

    def test_transform_multiple_keys(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        data = {
            'img': Image.open(img_path),
            'condition_img': Image.open(img_path),
            'crop_top_left': [0, 0],
            'crop_bottom_right': [10, 10]
        }

        # test transform
        trans = TRANSFORMS.build(
            dict(
                type='RandomHorizontalFlip',
                p=1.,
                keys=['img', 'condition_img']))
        data = trans(data)
        self.assertIn('crop_top_left', data)
        assert len(data['crop_top_left']) == 2
        self.assertListEqual(data['crop_top_left'],
                             [0, data['img'].width - 10])

        np.equal(
            np.array(data['img']),
            np.array(Image.open(img_path).transpose(Image.FLIP_LEFT_RIGHT)))
        np.equal(np.array(data['img']), np.array(data['condition_img']))


class TestMultiAspectRatioResizeCenterCrop(TestCase):
    sizes = [(32, 32), (16, 48)]

    def test_register(self):
        self.assertIn('MultiAspectRatioResizeCenterCrop', TRANSFORMS)

    def test_transform(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        data = {'img': Image.open(img_path).resize((32, 36))}

        # test transform
        trans = TRANSFORMS.build(
            dict(type='MultiAspectRatioResizeCenterCrop', sizes=self.sizes))
        data = trans(data)
        self.assertIn('crop_top_left', data)
        assert len(data['crop_top_left']) == 2
        self.assertTupleEqual((data['img'].height, data['img'].width),
                              self.sizes[0])
        upper, left = data['crop_top_left']
        lower, right = data['crop_bottom_right']
        assert lower == upper + self.sizes[0][0]
        assert right == left + self.sizes[0][1]
        np.equal(
            np.array(data['img']),
            np.array(
                Image.open(img_path).resize((32, 36)).crop(
                    (left, upper, right, lower))))

        # test 2nd size
        data = {'img': Image.open(img_path).resize((55, 16))}
        data = trans(data)
        self.assertIn('crop_top_left', data)
        assert len(data['crop_top_left']) == 2
        self.assertTupleEqual((data['img'].height, data['img'].width),
                              self.sizes[1])
        upper, left = data['crop_top_left']
        lower, right = data['crop_bottom_right']
        assert lower == upper + self.sizes[1][0]
        assert right == left + self.sizes[1][1]
        np.equal(
            np.array(data['img']),
            np.array(
                Image.open(img_path).resize((55, 16)).crop(
                    (left, upper, right, lower))))

    def test_transform_multiple_keys(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        data = {
            'img': Image.open(img_path).resize((32, 36)),
            'condition_img': Image.open(img_path).resize((32, 36))
        }

        # test transform
        trans = TRANSFORMS.build(
            dict(
                type='MultiAspectRatioResizeCenterCrop',
                sizes=self.sizes,
                keys=['img', 'condition_img']))
        data = trans(data)
        self.assertIn('crop_top_left', data)
        assert len(data['crop_top_left']) == 2
        self.assertTupleEqual((data['img'].height, data['img'].width),
                              self.sizes[0])
        upper, left = data['crop_top_left']
        lower, right = data['crop_bottom_right']
        assert lower == upper + self.sizes[0][0]
        assert right == left + self.sizes[0][1]
        np.equal(
            np.array(data['img']),
            np.array(
                Image.open(img_path).resize((32, 36)).crop(
                    (left, upper, right, lower))))
        np.equal(np.array(data['img']), np.array(data['condition_img']))


class TestCLIPImageProcessor(TestCase):

    def test_register(self):
        self.assertIn('CLIPImageProcessor', TRANSFORMS)

    def test_transform(self):
        img_path = osp.join(osp.dirname(__file__), '../../testdata/color.jpg')
        data = {
            'img': Image.open(img_path),
        }

        # test transform
        trans = TRANSFORMS.build(dict(type='CLIPImageProcessor'))
        data = trans(data)
        self.assertIn('clip_img', data)
        self.assertEqual(type(data['clip_img']), torch.Tensor)
        self.assertEqual(data['clip_img'].size(), (3, 224, 224))


class TestRandomTextDrop(TestCase):

    def test_register(self):
        self.assertIn('RandomTextDrop', TRANSFORMS)

    def test_transform(self):
        data = {
            'text': 'a dog',
        }

        # test transform
        trans = TRANSFORMS.build(dict(type='RandomTextDrop', p=1.))
        data = trans(data)
        assert data['text'] == ''

        # test transform p=0.0
        data = {
            'text': 'a dog',
        }
        trans = TRANSFORMS.build(dict(type='RandomTextDrop', p=0.))
        data = trans(data)
        assert data['text'] == 'a dog'
