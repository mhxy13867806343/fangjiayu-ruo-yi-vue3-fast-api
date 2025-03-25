from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config.env import UploadConfig
import os


def mount_staticfiles(app: FastAPI):
    """
    挂载静态文件
    """
    # 确保上传目录存在
    upload_dir = os.path.join(UploadConfig.UPLOAD_PATH, 'upload')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    # 将/profile/upload路径映射到vf_admin/upload_path/upload目录
    app.mount('/profile/upload', StaticFiles(directory=upload_dir), name='profile_upload')
