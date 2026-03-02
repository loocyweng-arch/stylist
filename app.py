import streamlit as st
import base64
import os
from openai import OpenAI

# 页面配置
st.set_page_config(page_title="Project Mirror - AI Stylist", layout="wide")

st.title("👗 Project Mirror: 你的 AI 时尚大脑")
st.markdown("---")

# 侧边栏设置
st.sidebar.header("输入设置")
city = st.sidebar.text_input("当前城市", "广州")
occasion = st.sidebar.text_input("场合", "商务会议")
uploaded_files = st.sidebar.file_uploader("上传你的衣服图片", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# API 设置 (优先从 Streamlit Secrets 获取，本地则找环境变量)
api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

if st.sidebar.button("生成 OOTD 建议"):
    if not uploaded_files:
        st.warning("请至少上传一张你的衣服图片。")
    elif not api_key:
        st.error("未找到 API Key。请在 Streamlit Secrets 中配置 OPENAI_API_KEY。")
    else:
        client = OpenAI(api_key=api_key)
        with st.spinner('AI 造型师正在分析衣橱并查询天气...'):
            try:
                # 构建 AI 消息
                messages = [
                    {
                        "role": "system",
                        "content": "你是一位顶级的时尚造型师。根据用户上传的图片、城市和场合，提供 OOTD 方案。你需要：1. 模拟该城市今日天气。2. 从上传的图片中挑选单品。3. 提供完美穿搭、妆发建议和造型贴士。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"城市: {city}. 场合: {occasion}. 请根据这些信息和上传的图片，为我建议一套完美的穿搭。"}
                        ]
                    }
                ]
                
                # 处理上传的图片
                for uploaded_file in uploaded_files:
                    encoded = encode_image(uploaded_file)
                    messages[1]["content"].append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded}"
                        }
                    })

                # 调用大模型 (这里用 GPT-4o 以支持视觉分析)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=800
                )
                
                recommendation = response.choices[0].message.content
                
                # 展示结果
                st.markdown("### ✨ 你的专属 OOTD 建议")
                st.markdown(recommendation)
                
                st.divider()
                st.subheader("本次分析的单品")
                cols = st.columns(len(uploaded_files))
                for i, file in enumerate(uploaded_files):
                    cols[i].image(file, use_column_width=True)
                    
            except Exception as e:
                st.error(f"发生错误: {e}")
else:
    st.info("请在左侧上传你的衣物图片，输入城市和场合，然后点击按钮。")
