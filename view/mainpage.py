import gradio as gr

from utils import readFile

with gr.Blocks(title="图片工具") as demo:
    gr.Markdown("# 彩色图转灰度图")

    with gr.Row():
        inp = gr.File(label="上传文件",
        file_types=[".pdf", ".png", ".jpg",".xls"],   # 只允许这些扩展名)
        file_count="multiple",)
        out = gr.Image(label="灰度图")
    btn = gr.Button("开始上传")
    btn.click(fn=readFile.read_file_by_ext, inputs=inp, outputs=out)

demo.launch()
