import streamlit as st
import pdfplumber
from docx import Document
from openai import OpenAI

# 填入你的大模型API信息
client = OpenAI(
    api_key="你的API密钥",
    base_url="https://api.deepseek.com/v1"
)

# 审核提示词（法务SOP）
SYS_PROMPT = """
你是资深法务，严格按下面步骤审核合同：
1.检查甲乙主体、金额、期限、付款、违约、管辖、生效条款
2.找出所有风险，分高、中、低
3.每条风险必须输出：原文、风险问题、修改建议、法律依据
4.列出合同缺失条款
5.最后给出整体评分0-100
输出清晰易懂的审核报告
"""

# 读取PDF
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as f:
        for page in f.pages:
            text += page.extract_text() or ""
    return text

# 读取DOCX
def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

# AI审核
def check_contract(text):
    res = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role":"system","content":SYS_PROMPT},
            {"role":"user","content":"请审核以下合同：\n"+text}
        ]
    )
    return res.choices[0].message.content

# 网页界面
st.title("AI合同自动审核工具")
upload = st.file_uploader("上传合同PDF/DOCX",type=["pdf","docx"])

if upload:
    with st.spinner("审核中..."):
        if upload.name.endswith("pdf"):
            content = read_pdf(upload)
        else:
            content = read_docx(upload)
        result = check_contract(content)
    st.success("审核完成")
    st.markdown(result)
