import os
import base64
from PIL import Image

class SkillManager:
    def __init__(self):
        self.books_folder = "book"
        self.ensure_book_folder()
        
    def ensure_book_folder(self):
        """确保书籍文件夹存在"""
        if not os.path.exists(self.books_folder):
            os.makedirs(self.books_folder)
    
    def save_uploaded_book(self, cover_file, pdf_file):
        """保存上传的书籍文件"""
        cover_path = os.path.join(self.books_folder, cover_file.name)
        pdf_path = os.path.join(self.books_folder, pdf_file.name)

        with open(cover_path, "wb") as f:
            f.write(cover_file.read())

        with open(pdf_path, "wb") as f:
            f.write(pdf_file.read())

        return {
            "title": pdf_file.name.split(".")[0], 
            "cover": cover_path, 
            "pdf": pdf_path
        }
    
    def get_preset_books(self):
        """获取预设书籍列表"""
        return [
            {"title": "军事理论", "cover": "book/军事理论.png", "pdf": "book/084733-01.pdf"},
            {"title": "数据管理分析", "cover": "book/数据管理.png", "pdf": "book/084733-01.pdf"},
            {"title": "操作系统原理", "cover": "book/f0549ae0dbadb44431d7931c4f6db31.png", "pdf": "book/084733-01.pdf"},
            {"title": "计算机网络", "cover": "book/e0928b4989ad49c1ab22a656927f2df.png", "pdf": "book/084733-01.pdf"},
            {"title": "deepseek", "cover": "book/deepseek.png", "pdf": "book/084733-01.pdf"},
        ]
    
    def get_all_books(self, uploaded_books=None):
        """获取所有书籍（预设+上传）"""
        books = self.get_preset_books()
        if uploaded_books:
            books.extend(uploaded_books)
        return books
    
    def get_pdf_link(self, pdf_path):
        """生成PDF下载链接"""
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            pdf_base64 = base64.b64encode(pdf_data).decode()
            return f"data:application/pdf;base64,{pdf_base64}"
        return None
    
    def load_image(self, image_path):
        """加载图片"""
        try:
            if os.path.exists(image_path):
                return Image.open(image_path)
            else:
                # 返回默认图片或None
                return None
        except Exception as e:
            print(f"加载图片失败: {e}")
            return None 