_base_ = [
    "../_base_/models/lcm_xl_lora.py",
    "../_base_/datasets/pokemon_blip_xl_pre_compute.py",
    "../_base_/schedules/lcm_xl_50e.py",
    "../_base_/default_runtime.py",
]

train_dataloader = dict(batch_size=2)

optim_wrapper = dict(
    optimizer=dict(lr=1e-5),
    accumulative_counts=2)

custom_hooks = [
    dict(
        type="VisualizationHook",
        prompt=["yoda pokemon"] * 4,
        height=1024,
        width=1024),
    dict(type="PeftSaveHook"),
]
