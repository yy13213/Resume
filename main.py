import streamlit as st
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入各个模块
from learning_path import learning_path_page
from resume_parsing import resume_parsing_page
from skill_training import skill_training_page

def main():
    """主应用入口"""
    st.set_page_config(
        page_title="软件杯AI助手平台",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 侧边栏导航
    st.sidebar.title("🚀 软件杯AI助手平台")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "选择功能模块",
        [ "📄 简历解析","📚 学习路径规划", "🎯 技能培训"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📖 功能说明
                        
    **📄 简历解析** 
    - 智能简历内容分析
    - 关键信息提取
    - 简历优化建议                    
    
    **📚 学习路径规划**
    - AI个性化学习计划制定
    - 智能学习资源推荐
    - 学习进度跟踪
    
    
    **🎯 技能培训**
    - 个人技能评估
    - 培训课程推荐
    - 技能提升路径
    """)
    
    # 根据选择显示对应页面
    if page == "📄 简历解析":
        resume_parsing_page()
    elif page == "📚 学习路径规划":
        learning_path_page()
    elif page == "🎯 技能培训":
        skill_training_page()

if __name__ == "__main__":
    main() 