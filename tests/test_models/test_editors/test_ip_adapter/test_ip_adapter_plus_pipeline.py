from unittest import TestCase

import pytest
import torch
from diffusers import (
    ControlNetModel,
    DiffusionPipeline,
    StableDiffusionXLControlNetPipeline,
)
from diffusers.utils import load_image
from mmengine.optim import OptimWrapper
from torch.optim import SGD

from diffengine.models.archs.ip_adapter import (
    CNAttnProcessor,
    CNAttnProcessor2_0,
    IPAttnProcessor,
    IPAttnProcessor2_0,
)
from diffengine.models.editors import IPAdapterXLPlusPipeline


class TestIPAdapterXL(TestCase):

    def test_infer(self):
        pipeline = DiffusionPipeline.from_pretrained(
            "hf-internal-testing/tiny-stable-diffusion-xl-pipe")
        StableDiffuser = IPAdapterXLPlusPipeline(
            pipeline,
            image_encoder="hf-internal-testing/unidiffuser-diffusers-test")

        assert any(
            isinstance(attn_processor, IPAttnProcessor | IPAttnProcessor2_0)
            for attn_processor in (
                StableDiffuser.pipeline.unet.attn_processors.values()))

        # test infer
        result = StableDiffuser.infer(
            ["an insect robot preparing a delicious meal"],
            ["tests/testdata/color.jpg"],
            height=64,
            width=64)
        assert len(result) == 1
        assert result[0].shape == (64, 64, 3)

        # test device
        assert StableDiffuser.device.type == "cpu"

        # test infer with negative_prompt
        result = StableDiffuser.infer(
            ["an insect robot preparing a delicious meal"],
            ["tests/testdata/color.jpg"],
            negative_prompt="noise",
            height=64,
            width=64)
        assert len(result) == 1
        assert result[0].shape == (64, 64, 3)

        # output_type = 'latent'
        result = StableDiffuser.infer(
            ["an insect robot preparing a delicious meal"],
            ["tests/testdata/color.jpg"],
            output_type="latent",
            height=64,
            width=64)
        assert len(result) == 1
        assert type(result[0]) == torch.Tensor
        assert result[0].shape == (4, 32, 32)

    def test_infer_controlnet(self):
        controlnet = ControlNetModel.from_pretrained(
            "hf-internal-testing/tiny-controlnet-sdxl")
        pipeline = StableDiffusionXLControlNetPipeline.from_pretrained(
            "hf-internal-testing/tiny-stable-diffusion-xl-pipe",
            controlnet=controlnet)
        StableDiffuser = IPAdapterXLPlusPipeline(
            pipeline,
            image_encoder="hf-internal-testing/unidiffuser-diffusers-test")

        assert any(
            isinstance(attn_processor, IPAttnProcessor | IPAttnProcessor2_0)
            for attn_processor in (
                StableDiffuser.pipeline.unet.attn_processors.values()))

        assert any(
            isinstance(attn_processor, CNAttnProcessor | CNAttnProcessor2_0)
            for attn_processor in (
                StableDiffuser.pipeline.controlnet.attn_processors.values()))

        # test infer
        result = StableDiffuser.infer(
            ["an insect robot preparing a delicious meal"],
            ["tests/testdata/color.jpg"],
            image=load_image("tests/testdata/color.jpg").resize((64, 64)),
            height=64,
            width=64)
        assert len(result) == 1
        assert result[0].shape == (64, 64, 3)

    def test_infer_multi_controlnet(self):
        controlnet = ControlNetModel.from_pretrained(
            "hf-internal-testing/tiny-controlnet-sdxl")
        pipeline = StableDiffusionXLControlNetPipeline.from_pretrained(
            "hf-internal-testing/tiny-stable-diffusion-xl-pipe",
            controlnet=[controlnet, controlnet])
        StableDiffuser = IPAdapterXLPlusPipeline(
            pipeline,
            image_encoder="hf-internal-testing/unidiffuser-diffusers-test")

        assert any(
            isinstance(attn_processor, IPAttnProcessor | IPAttnProcessor2_0)
            for attn_processor in (
                StableDiffuser.pipeline.unet.attn_processors.values()))

        for controlnet in StableDiffuser.pipeline.controlnet.nets:
            assert any(
                isinstance(attn_processor, CNAttnProcessor
                           | CNAttnProcessor2_0)
                for attn_processor in (controlnet.attn_processors.values()))

        # test infer
        result = StableDiffuser.infer(
            ["an insect robot preparing a delicious meal"],
            ["tests/testdata/color.jpg"],
            image=[
                load_image("tests/testdata/color.jpg").resize((64, 64)),
                load_image("tests/testdata/color.jpg").resize((64, 64)),
            ],
            height=64,
            width=64)
        assert len(result) == 1
        assert result[0].shape == (64, 64, 3)

    def test_train_step(self):
        pipeline = DiffusionPipeline.from_pretrained(
            "hf-internal-testing/tiny-stable-diffusion-xl-pipe")
        StableDiffuser = IPAdapterXLPlusPipeline(
            pipeline,
            image_encoder="hf-internal-testing/unidiffuser-diffusers-test")

        # test train step
        data = {
            "inputs": {
                "img": [torch.zeros((3, 64, 64))],
                "text": ["a dog"],
                "clip_img": [torch.zeros((3, 32, 32))],
                "time_ids": [torch.zeros((1, 6))],
            },
        }
        optimizer = SGD(StableDiffuser.parameters(), lr=0.1)
        optim_wrapper = OptimWrapper(optimizer)
        with pytest.raises(NotImplementedError, match="train_step is not"):
            StableDiffuser.train_step(data, optim_wrapper)

    def test_val_and_test_step(self):
        pipeline = DiffusionPipeline.from_pretrained(
            "hf-internal-testing/tiny-stable-diffusion-xl-pipe")
        StableDiffuser = IPAdapterXLPlusPipeline(
            pipeline,
            image_encoder="hf-internal-testing/unidiffuser-diffusers-test")

        # test val_step
        with pytest.raises(NotImplementedError, match="val_step is not"):
            StableDiffuser.val_step(torch.zeros((1, )))

        # test test_step
        with pytest.raises(NotImplementedError, match="test_step is not"):
            StableDiffuser.test_step(torch.zeros((1, )))
