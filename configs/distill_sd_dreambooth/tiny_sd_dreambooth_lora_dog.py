_base_ = [
    "../_base_/models/tiny_sd_lora.py",
    "../_base_/datasets/dog_dreambooth.py",
    "../_base_/schedules/stable_diffusion_1k.py",
    "../_base_/default_runtime.py",
]

train_dataloader = {
    "dataset": {
        "class_image_config": {
            "model": {{_base_.model.model}},
        },
    },
}
