import streamlit as st
import openai
import tempfile

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="扑克AI手牌分析助手", layout="centered")
st.title("🃏 扑克AI手牌分析助手")

st.markdown("""
请输入一手牌的描述，我们的AI将为你提供分析建议（支持中英文、语音输入）。

**示例输入：**
- 我在CO拿到ATs，加注到2.5bb，BB跟注，翻牌T73，我下注...
- I had AKs in MP, raised to 3bb, BTN called, flop came QJ2 rainbow...
""")

# ========== 音频上传区域 ==========
st.markdown("### 🎙️ 上传语音（支持普通话 / 粤语 / 英文）")
audio_file = st.file_uploader("选择一段语音文件：", type=["mp3", "wav", "m4a"])
transcribed_text = ""

if audio_file is not None:
    with st.spinner("识别语音中，请稍候..."):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(audio_file.read())
            tmp_file_path = tmp_file.name

        try:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=open(tmp_file_path, "rb")
            )
            transcribed_text = transcript["text"]
            st.success("语音识别成功！")
            st.text_area("识别文本：", transcribed_text, height=150)
        except Exception as e:
            st.error(f"语音识别出错: {e}")

# ========== 手动文本输入区域 ==========
st.markdown("### ✍️ 或直接输入文字描述")
user_input = st.text_area("请输入手牌描述：", value=transcribed_text, height=200)

if st.button("提交分析") and user_input.strip():
    with st.spinner("分析中，请稍候..."):
        try:
            prompt = f"""
你是一位专业扑克教练，擅长分析玩家的No Limit Hold'em（无限德州扑克）手牌决策。请根据以下手牌描述给出分析建议：

{user_input.strip()}

请分步骤给出建议，并说明可能的更优选择。
"""

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位扑克策略分析专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )

            result = response['choices'][0]['message']['content']
            st.markdown("### 🧠 分析结果：")
            st.markdown(result)

        except Exception as e:
            st.error(f"发生错误: {e}")
else:
    st.info("请上传语音或输入文字，然后点击提交分析。")
