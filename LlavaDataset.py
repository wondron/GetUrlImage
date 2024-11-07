from dataclasses import dataclass

import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset
from pathlib import Path
from typing import List, Tuple


class LlavaDataset(Dataset):
    def __init__(self, dataset_dir:str) -> None:
        super().__init__()
        self.chat_data, self.image_dir = self.build_dataset(data_dir= dataset_dir)
        
    def build_dataset(self, data_dir:str) -> Tuple[List, Path]:
        data_dir = Path(data_dir)
        chat_file = data_dir.joinpath("chat.json")
        image_dir = data_dir.joinpath("image_dl")
        
        chat_data = pd.read_json(path_or_buf=chat_file).to_dict(orient='records')
        
        return chat_data, image_dir
        
    def __len__(self) -> int:
        return len(self.chat_data)
    
    def __getitem__(self, index) -> tuple[str, str, Path]:
        cur_data = self.chat_data[index]
        
        human_input = cur_data['conversations'][0]['value']
        gpt_input = cur_data['conversations'][1]['value']
        
        image_path = self.image_dir.joinpath(cur_data.get("image"))
        
        return (human_input, gpt_input, image_path)        
    


test_llavadataset = LlavaDataset("dataset")