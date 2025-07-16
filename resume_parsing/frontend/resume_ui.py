import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from resume_parsing.backend.resume_parser import ResumeParser

class ResumeUI:
    def __init__(self):
        self.parser = ResumeParser()
        
    def apply_custom_styles(self):
        """应用自定义CSS样式"""
        st.markdown("""
            <style>
                .stChatInput {
                    bottom: 20px;
                    position: fixed;
                    width: 85%;
                }
                .stChatMessage {
                    padding: 12px 16px;
                    border-radius: 12px;
                    margin-bottom: 12px;
                }
                .stButton>button {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 8px;
                    padding: 8px 16px;
                }
                .stTextArea textarea {
                    border-radius: 8px;
                    padding: 10px;
                }
                .stFileUploader {
                    margin-bottom: 20px;
                }
            </style>
        """, unsafe_allow_html=True)
        
    def initialize_session_state(self):
        """初始化会话状态 - 使用独立的键名"""
        if "resume_messages" not in st.session_state:
            st.session_state["resume_messages"] = [
                {"role": "assistant",
                 "content": "我是简历分析助手，请上传简历，我将开始分析。\n\n评估标准：\n1. 技能匹配（35分）- 工作是否需要我的关键技术？\n2. 经验匹配（25分）- 我过去的角色与工作职责是否一致？\n3. 行业匹配度（15分）- 该工作是否与我曾工作过的行业相符？\n4. 公司与文化契合度（10分）- 是否符合我的工作风格（远程、敏捷、初创公司等）？\n5. 成长与兴趣（5分）- 这份工作是否让我兴奋或与我的职业目标一致？\n6. 可疑的简历信息。\n\n[开始分析]"}]
        
        if "resume_analyzed_text" not in st.session_state:
            st.session_state["resume_analyzed_text"] = None
    
    def display_chat_history(self):
        """显示聊天历史"""
        for msg in st.session_state.resume_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
    
    def display_streaming_response(self, response_generator):
        """显示流式响应"""
        message_placeholder = st.empty()
        full_response = ""
        
        for chunk in response_generator:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        return full_response
    
    def handle_file_upload(self):
        """处理文件上传"""
        with stylable_container(
                key="file_uploader",
                css_styles="""
                {
                    background-color: #f0f2f6;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
            """
        ):
            st.markdown("###  上传简历")
            resume_file = st.file_uploader(
                "选择简历文件（支持PDF、DOCX、DOC格式）", 
                type=["pdf", "docx", "doc"], 
                label_visibility="collapsed"
            )
            
        if resume_file is not None:
            with st.spinner("正在分析简历..."):
                try:
                    # 显示文件信息
                    
                    # 提取文本
                    text = self.parser.extract_text_from_file(resume_file)
                    
                    # 显示提取结果
                    if text and text.strip():
                        st.success(f"✅ 简历解析完成！提取了 {len(text)} 个字符")
                        # 显示文本预览
                        preview = text[:200] + "..." if len(text) > 200 else text
                        st.info(f"📝 内容预览: {preview}")
                    else:
                        st.warning("⚠️ 文件解析完成，但未提取到文本内容")
                        
                    # 存储文本到session state
                    st.session_state.resume_analyzed_text = text

                    # 显示提取的文本
                    with stylable_container(
                            key="text_area",
                            css_styles="""
                            {
                                border: 1px solid #e1e4e8;
                                border-radius: 10px;
                                padding: 15px;
                                margin-bottom: 20px;
                            }
                        """
                    ):
                        st.markdown("### 📝 简历内容")
                        st.text_area("简历文本内容", value=text, height=300, label_visibility="collapsed")

                    # 分析简历
                    if text:
                        try:
                            st.session_state.resume_analyzed_text = text
                            st.session_state.resume_messages.append({"role": "user", "content": "请分析这份简历"})
                            
                            with st.chat_message("user"):
                                st.write("请分析这份简历")
                            
                            with st.chat_message("assistant"):
                                with st.spinner("正在分析简历..."):
                                    # 获取流式响应
                                    response = self.parser.client.chat.completions.create(
                                        model='generalv3.5',
                                        messages=[
                                            {"role": "user", "content": f"简历内容：{text}\n\n请根据以下标准分析这份简历：\n1. 技能匹配（35分）- 工作是否需要我的关键技术？\n2. 经验匹配（25分）- 我过去的角色与工作职责是否一致？\n3. 行业匹配度（15分）- 该工作是否与我曾工作过的行业相符？\n4. 公司与文化契合度（10分）- 是否符合我的工作风格（远程、敏捷、初创公司等）？\n5. 成长与兴趣（5分）- 这份工作是否让我兴奋或与我的职业目标一致？\n6. 可疑的简历信息。\n\n请给出详细的分析报告和各项评分。"}
                                        ],
                                        stream=True
                                    )
                                    
                                    # 显示流式响应
                                    message_placeholder = st.empty()
                                    full_response = ""
                                    
                                    for chunk in response:
                                        if chunk.choices[0].delta.content is not None:
                                            content = chunk.choices[0].delta.content
                                            full_response += content
                                            message_placeholder.markdown(full_response + "▌")
                                    
                                    message_placeholder.markdown(full_response)
                                    st.session_state.resume_messages.append({"role": "assistant", "content": full_response})
                        except Exception as e:
                            st.error(f"分析失败：{str(e)}")
                except Exception as e:
                    st.error(f"文件处理失败：{str(e)}")
                    st.info("请确保文件格式正确且未损坏。支持的格式：PDF、DOCX、DOC")
    
    def handle_chat_input(self):
        """处理聊天输入 - 流式输出"""
        if prompt := st.chat_input("关于简历分析有什么问题..."):
            try:
                st.session_state.resume_messages.append({"role": "user", "content": prompt})
                
                with st.chat_message("user"):
                    st.write(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("正在思考..."):
                        # 获取流式响应
                        response = self.parser.client.chat.completions.create(
                            model='generalv3.5',
                            messages=st.session_state.resume_messages + [{"role": "user", "content": prompt}],
                            stream=True
                        )
                        
                        # 显示流式响应
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        for chunk in response:
                            if chunk.choices[0].delta.content is not None:
                                content = chunk.choices[0].delta.content
                                full_response += content
                                message_placeholder.markdown(full_response + "▌")
                        
                        message_placeholder.markdown(full_response)
                        st.session_state.resume_messages.append({"role": "assistant", "content": full_response})
                        
            except Exception as e:
                st.error(f"对话失败：{str(e)}")
    
    def render(self):
        """渲染完整的UI"""
        self.apply_custom_styles()
        self.initialize_session_state()
        
        # 创建带颜色的标题
        colored_header(
            label="📄 简历解析",
            description="AI简历分析助手，帮助您评估简历匹配度",
            color_name="blue-70",
        )
        
        # 显示聊天历史
        self.display_chat_history()
        
        # 处理文件上传
        self.handle_file_upload()
        
        # 处理聊天输入
        self.handle_chat_input()

def resume_parsing_page():
    """简历解析页面入口函数"""
    ui = ResumeUI()
    ui.render() 

# 主程序入口
if __name__ == "__main__":
    resume_parsing_page() 