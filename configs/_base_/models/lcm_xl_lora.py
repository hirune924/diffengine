model = dict(
    type="LatentConsistencyModelsXL",
    model="stabilityai/stable-diffusion-xl-base-1.0",
    vae_model="madebyollin/sdxl-vae-fp16-fix",
    loss=dict(type="HuberLoss"),
    pre_compute_text_embeddings=True,
    gradient_checkpointing=True,
    unet_lora_config=dict(
        type="LoRA",
        r=8,
        lora_alpha=1,
        target_modules=[
            "to_q",
            "to_k",
            "to_v",
            "to_out.0",
            "proj_in",
            "proj_out",
            "ff.net.0.proj",
            "ff.net.2",
            "conv1",
            "conv2",
            "conv_shortcut",
            "downsamplers.0.conv",
            "upsamplers.0.conv",
            "time_emb_proj",
        ]))
