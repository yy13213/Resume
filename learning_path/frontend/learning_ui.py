import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from learning_path.backend.learning_planner import LearningPlanner

class LearningUI:
    def __init__(self):
        self.planner = LearningPlanner()
        
    def apply_custom_styles(self):
        """应用自定义CSS样式"""
        st.markdown("""
            <style>
                .stTextInput input, .stTextArea textarea, .stSelectbox select {
                    border-radius: 8px !important;
                    padding: 10px !important;
                    border: 1px solid #e1e4e8 !important;
                }
                .stButton>button {
                    background-color: #4CAF50 !important;
                    color: white !important;
                    border-radius: 8px !important;
                    padding: 8px 16px !important;
                    width: 100% !important;
                    transition: all 0.3s !important;
                }
                .stButton>button:hover {
                    background-color: #45a049 !important;
                    transform: scale(1.02) !important;
                }
                .stMarkdown h3 {
                    color: #4a4a4a !important;
                    margin-bottom: 8px !important;
                }
                .streaming-message {
                    white-space: pre-wrap;
                    animation: fadeIn 0.3s ease-in-out;
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
            </style>
        """, unsafe_allow_html=True)
        
    def initialize_session_state(self):
        """初始化会话状态 - 使用独立的键名"""
        if "learning_messages" not in st.session_state:
            st.session_state["learning_messages"] = [
                {"role": "assistant",
                 "content": "📚 欢迎使用AI学习规划助手！\n\n我可以帮助您制定个性化的学习计划。\n\n请填写以下信息，我将为您生成详细的学习方案：\n\n1. 您的目标岗位\n2. 需要学习的内容\n3. 具体的学习目标\n4. 计划投入的时间\n\n填写完成后点击【生成学习计划】按钮"}
            ]
        
        if "learning_plan_generated" not in st.session_state:
            st.session_state["learning_plan_generated"] = False

    def display_chat_history(self):
        """显示聊天历史"""
        for msg in st.session_state.learning_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    def render_input_form(self):
        """渲染输入表单"""
        with stylable_container(
                key="input_form",
                css_styles="""
                {
                    background-color: #f8f9fa;
                    border-radius: 12px;
                    padding: 25px;
                    margin-bottom: 25px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
            """
        ):
            st.markdown("### 🎯 学习信息填写")

            col1, col2 = st.columns(2)
            with col1:
                position = st.text_input("目标岗位", placeholder="请输入您的目标岗位")
                study_content = st.text_area("学习内容", placeholder="请输入您需要学习的具体内容")

            with col2:
                study_goal = st.text_input("学习目标", placeholder="请输入您的具体学习目标")
                time_commitment = st.selectbox(
                    "计划投入时间",
                    options=["1-2小时/天", "3-4小时/天", "5-6小时/天", "7-8小时/天", "全职学习"]
                )

            generate_btn = st.button("✨ 生成学习计划")
            
            return position, study_content, study_goal, time_commitment, generate_btn

    def handle_plan_generation(self, position, study_content, study_goal, time_commitment):
        """处理学习计划生成"""
        if not all([position, study_content, study_goal, time_commitment]):
            st.warning("请填写所有字段后再生成学习计划")
            return

        with st.spinner("🚀 正在生成个性化学习计划..."):
            try:
                # 更新会话状态
                user_input = f"目标岗位: {position}\n学习内容: {study_content}\n学习目标: {study_goal}\n时间投入: {time_commitment}"
                st.session_state.learning_messages.append({"role": "user", "content": user_input})
                
                with st.chat_message("user"):
                    st.write(f"请为我制定学习计划:\n目标: {position}\n内容: {study_content}")
                
                with st.chat_message("assistant"):
                    # 获取流式响应
                    prompt = f"""
                    请根据以下信息为用户制定详细的学习计划：

                    【目标岗位】: {position}
                    【学习内容】: {study_content}
                    【学习目标】: {study_goal}
                    【时间投入】: {time_commitment}

                    要求：
                    1. 制定分阶段的学习路线图
                    2. 推荐具体的学习资源和方法
                    3. 提供时间管理建议
                    4. 给出学习效果评估方法
                    5. 包含可能的挑战及应对策略

                    请用清晰的结构化格式输出，适当使用emoji和标题分级。
                    """
                    
                    response = self.planner.client.chat.completions.create(
                        model='generalv3.5',
                        messages=[{"role": "user", "content": prompt}],
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
                    st.session_state.learning_messages.append({"role": "assistant", "content": full_response})
                    st.session_state.learning_plan_generated = True
                    
            except Exception as e:
                st.error(f"生成学习计划失败：{str(e)}")

    def handle_chat_input(self):
        """处理聊天输入 - 流式输出"""
        if prompt := st.chat_input("关于学习计划有什么问题..."):
            try:
                st.session_state.learning_messages.append({"role": "user", "content": prompt})
                
                with st.chat_message("user"):
                    st.write(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("正在思考..."):
                        # 获取流式响应
                        response = self.planner.client.chat.completions.create(
                            model='generalv3.5',
                            messages=st.session_state.learning_messages + [{"role": "user", "content": prompt}],
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
                        st.session_state.learning_messages.append({"role": "assistant", "content": full_response})
                        
            except Exception as e:
                st.error(f"对话失败：{str(e)}")

    def render(self):
        """渲染完整的UI"""
        self.apply_custom_styles()
        self.initialize_session_state()
        
        # 创建带颜色的标题
        colored_header(
            label="📝 AI学习规划系统",
            description="个性化学习方案生成平台",
            color_name="blue-70",
        )
        
        # 显示聊天历史
        self.display_chat_history()
        
        # 渲染输入表单
        position, study_content, study_goal, time_commitment, generate_btn = self.render_input_form()
        
        # 处理表单提交
        if generate_btn:
            self.handle_plan_generation(position, study_content, study_goal, time_commitment)
        
        # 处理聊天输入
        self.handle_chat_input()

def learning_path_page():
    """学习路径页面入口函数"""
    ui = LearningUI()
    ui.render() 

# 主程序入口
if __name__ == "__main__":
    learning_path_page() 