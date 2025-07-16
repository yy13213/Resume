# 技能培训模块
try:
    from .frontend.training_ui import skill_training_page
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from frontend.training_ui import skill_training_page

__version__ = "1.0.0"
__all__ = ["skill_training_page"] 