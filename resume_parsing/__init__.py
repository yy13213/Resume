# 简历解析模块
try:
    from .frontend.resume_ui import resume_parsing_page
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from frontend.resume_ui import resume_parsing_page

__version__ = "1.0.0"
__all__ = ["resume_parsing_page"] 