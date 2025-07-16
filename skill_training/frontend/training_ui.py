import streamlit as st
import base64
import sys
import os
from streamlit_pdf_viewer import pdf_viewer

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from skill_training.backend.skill_manager import SkillManager

class TrainingUI:
    def __init__(self):
        self.manager = SkillManager()
        
    def render_file_upload_section(self):
        """渲染文件上传区域"""
        st.subheader("📚 上传新书籍")
        
        uploaded_books = []
        book_cover = st.file_uploader("上传书籍封面（JPEG/PNG）", type=["jpg", "jpeg", "png"])
        book_pdf = st.file_uploader("上传书籍PDF文件", type=["pdf"])

        if book_cover and book_pdf:
            book_info = self.manager.save_uploaded_book(book_cover, book_pdf)
            uploaded_books.append(book_info)
            st.success("书籍上传成功！")
            
        return uploaded_books
        
    def render_book_list(self):
        """渲染书籍列表"""
        st.subheader("📚 已有书籍")
        
        books = self.manager.get_available_books()
        
        if books:
            cols = st.columns(3)
            for i, book in enumerate(books):
                with cols[i % 3]:
                    with st.container():
                        # 显示书籍封面
                        if book['cover']:
                            st.image(book['cover'], use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/200x300/cccccc/666666?text=No+Cover", 
                                   use_container_width=True)
                        
                        # 书籍信息
                        st.markdown(f"**{book['title']}**")
                        st.markdown(f"📄 {book['pages']} 页")
                        
                        # 选择按钮
                        if st.button(f"📖 阅读", key=f"read_{i}", use_container_width=True):
                            st.session_state["selected_pdf"] = book['pdf_path']
                            st.rerun()
        else:
            st.info("暂无可用书籍，请先上传一些书籍。")
    
    def render_pdf_viewer(self):
        """渲染PDF查看器 - 使用streamlit-pdf-viewer组件"""
        selected_pdf = st.session_state.get("selected_pdf", None)
        
        if selected_pdf:
            st.subheader(f"📖 正在阅读: {selected_pdf.split('/')[-1]}")
            
            try:
                # 检查文件是否存在
                if os.path.exists(selected_pdf):
                    # 使用streamlit-pdf-viewer组件渲染PDF
                    with open(selected_pdf, "rb") as pdf_file:
                        pdf_viewer(
                            input=pdf_file.read(),
                            width=700,
                            height=600,
                            annotations=True,  # 启用注释功能
                            pages_vertical_spacing=2,  # 页面间距
                            annotation_outline_size=1,  # 注释边框大小
                        )
                else:
                    st.error("PDF文件不存在，请重新选择书籍")
                    # 清除无效的选择
                    if "selected_pdf" in st.session_state:
                        del st.session_state["selected_pdf"]
                        
            except Exception as e:
                st.error(f"PDF文件加载失败: {str(e)}")
                st.info("请确保PDF文件格式正确且未损坏")
        else:
            st.info("请从上方选择一本书籍开始学习")

    def render(self):
        """渲染完整的技能培训界面"""
        st.title("💪 技能培训系统")
        
        # 创建标签页 - 只保留书籍库和在线阅读
        tab1, tab2 = st.tabs(["📚 书籍库", "📖 在线阅读"])
        
        with tab1:
            # 上传区域
            uploaded_books = self.render_file_upload_section()
            
            # 书籍列表显示
            self.render_book_list()
        
        with tab2:
            self.render_pdf_viewer()

def skill_training_page():
    """技能培训页面入口函数"""
    ui = TrainingUI()
    ui.render() 

# 主程序入口
if __name__ == "__main__":
    skill_training_page() 