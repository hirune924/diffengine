model = dict(
    type="StableDiffusion",
    model="segmind/small-sd",
    unet_lora_config=dict(
        type="LoRA",
        r=8,
        lora_alpha=8,
        target_modules=["to_q", "to_v", "to_k", "to_out.0"]))
