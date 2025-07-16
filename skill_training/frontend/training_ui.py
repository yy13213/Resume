import streamlit as st
import base64
import sys
import os

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
    
    def render_book_grid(self, books):
        """渲染书籍网格显示"""
        st.subheader("📖 我的书籍库")
        
        # 存储已选书籍的pdf路径
        selected_pdf = st.session_state.get("selected_pdf", None)
        
        # 显示所有书籍封面
        cols = st.columns(len(books))
        
        for i, book in enumerate(books):
            with cols[i]:
                # 尝试加载图片
                image = self.manager.load_image(book["cover"])
                if image:
                    st.image(image, caption=book["title"], use_container_width=True)
                else:
                    st.write(f"📄 {book['title']}")
                    st.write("(封面加载失败)")
                
                # 选择书籍按钮
                if st.button(f"选择 {book['title']}", key=f"select_{i}"):
                    st.session_state.selected_pdf = book["pdf"]
                    st.success(f"已选择《{book['title']}》")

    def render_pdf_viewer(self):
        """渲染PDF查看器"""
        selected_pdf = st.session_state.get("selected_pdf", None)
        
        if selected_pdf:
            st.subheader(f"📖 正在阅读: {selected_pdf.split('/')[-1]}")
            
            # 生成PDF查看链接
            pdf_link = self.manager.get_pdf_link(selected_pdf)
            if pdf_link:
                st.markdown(f'<iframe src="{pdf_link}" width="100%" height="600px"></iframe>', 
                           unsafe_allow_html=True)
            else:
                st.error("PDF文件不存在或无法加载")
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
            
            # 获取所有书籍
            all_books = self.manager.get_all_books(uploaded_books)
            
            # 书籍网格显示
            if all_books:
                self.render_book_grid(all_books)
            else:
                st.info("暂无书籍，请先上传书籍")
        
        with tab2:
            self.render_pdf_viewer()

def skill_training_page():
    """技能培训页面入口函数"""
    ui = TrainingUI()
    ui.render() 

# 主程序入口
if __name__ == "__main__":
    skill_training_page() 