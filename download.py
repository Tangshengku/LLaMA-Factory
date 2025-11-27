from huggingface_hub import get_token, whoami, hf_hub_download, snapshot_download
print("Current user:", whoami())
print("Cached token exists:", get_token() is not None)

# 强制使用 token 下载
snapshot_download("Shengkun/chemistry_dataset", local_dir="/nfs/scistore19/alistgrp/stang/LLaMA-Factory/data/chemi_data", repo_type="dataset", token=True)