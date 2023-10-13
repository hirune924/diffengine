train_pipeline = [
    {
        "type": "SaveImageShape",
    },
    {
        "type": "torchvision/Resize",
        "size": 1024,
        "interpolation": "bilinear",
    },
    {
        "type": "RandomCrop",
        "size": 1024,
    },
    {
        "type": "RandomHorizontalFlip",
        "p": 0.5,
    },
    {
        "type": "ComputeTimeIds",
    },
    {
        "type": "torchvision/ToTensor",
    },
    {
        "type": "DumpImage",
        "max_imgs": 10,
        "dump_dir": "work_dirs/dump",
    },
    {
        "type": "torchvision/Normalize",
        "mean": [0.5],
        "std": [0.5],
    },
    {
        "type": "PackInputs",
        "input_keys": ["img", "text", "time_ids"],
    },
]
train_dataloader = {
    "batch_size": 2,
    "num_workers": 4,
    "dataset": {
        "type": "HFDreamBoothDataset",
        "dataset": "google/dreambooth",
        "dataset_sub_dir": "backpack",
        "instance_prompt": "A photo of sks backpack",
        "pipeline": train_pipeline,
        "class_prompt": None,
    },
    "sampler": {
        "type": "InfiniteSampler",
        "shuffle": True,
    },
}

val_dataloader = None
val_evaluator = None
test_dataloader = val_dataloader
test_evaluator = val_evaluator

custom_hooks = [
    {
        "type": "VisualizationHook",
        "prompt": ["A photo of sks backpack in the Grand Canyon"] * 4,
        "by_epoch": False,
        "interval": 100,
        "height": 1024,
        "width": 1024,
    },
    {
        "type": "LoRASaveHook",
    },
]
