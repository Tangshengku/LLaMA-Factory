import os
import json
import re
import subprocess
from cnocr import CnOcr
from PIL import Image, ImageEnhance, ImageFilter


# 初始化 OCR 引擎
ocr = CnOcr(det_model_name="ch_PP-OCRv5_det", rec_model_name="ch_PP-OCRv5")

def extract_text_from_doc(doc_path):
    """
    专门处理旧版 .doc 文件
    尝试使用 antiword (Linux/macOS) 或 pywin32 (Windows)
    修正 antiword 输出混入问题，并移除 BOM
    """
    import platform
    system = platform.system()

    if system == "Windows":
        try:
            import win32com.client as win32
            word_app = win32.gencache.EnsureDispatch('Word.Application')
            word_app.Visible = False
            doc = word_app.Documents.Open(doc_path)
            text = doc.Range().Text
            doc.Close()
            word_app.Quit()
            # 移除 BOM 和控制字符
            return text.rstrip('\x07\x00').lstrip('\ufeff').strip()
        except ImportError:
            print(f"❌ Windows 环境下未安装 pywin32: pip install pywin32")
            return ""
        except Exception as e:
            print(f"❌ 使用 pywin32 提取 DOC 文件失败: {doc_path}, 错误: {e}")
            return ""

    elif system in ["Linux", "Darwin"]:
        try:
            result = subprocess.run(
                ['antiword', doc_path],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                print(f"⚠️  antiword 运行可能有警告 (退出码 {result.returncode}): {doc_path}")
                if not result.stdout.strip():
                    print(f"   - antiword stderr: {result.stderr}")
                    return ""

            full_output = result.stdout

            # --- 过滤 antiword 的状态行 ---
            lines = full_output.split('\n')
            filtered_lines = []
            for line in lines:
                if line.startswith('convert ') and ' using filter ' in line:
                    continue
                filtered_lines.append(line)

            extracted_text = "\n".join(filtered_lines).strip()
            # 移除 BOM
            return extracted_text.lstrip('\ufeff')

        except FileNotFoundError:
            print(f"❌ 未找到 antiword 程序，请安装: apt install antiword (Linux) 或 brew install antiword (macOS)")
            return ""
        except Exception as e:
            print(f"❌ 提取 DOC 文件失败: {doc_path}, 错误: {e}")
            return ""
    else:
        print(f"❌ 不支持的操作系统: {system}，无法处理 .doc 文件")
        return ""

def extract_text_from_docx(docx_path):
    """
    使用 python-docx 处理 .docx 文件
    """
    try:
        import docx
        doc = docx.Document(docx_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    full_text.append(cell.text)
        text = '\n'.join(full_text).strip()
        # 移除 BOM
        return text.lstrip('\ufeff')
    except Exception as e:
        print(f"❌ 提取 DOCX 文件失败: {docx_path}, 错误: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    """
    从 PDF 文件中提取文本。
    首先尝试 pdfplumber (适用于文字型 PDF)。
    如果失败或文本很少，则回退到 PyMuPDF + CnOCR (适用于扫描版 PDF)。
    """
    print(f"  - 开始处理 PDF: {pdf_path}")
    
    # --- 尝试使用 pdfplumber 提取文本 ---
    try:
        import pdfplumber
        text_lines = []
        with pdfplumber.open(pdf_path) as pdf:
            print(f"    - pdfplumber 成功打开 PDF，共 {len(pdf.pages)} 页")
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_lines.append(text)
                    print(f"      - 从第 {page_num+1} 页提取到 {len(text)} 个字符。")
        
        extracted_text = "\n".join(text_lines).strip()
        print(f"    - pdfplumber 提取完成，总字符数: {len(extracted_text)}")
        
        if len(extracted_text) > 20: 
            print(f"    - 使用 pdfplumber 提取的文本，长度: {len(extracted_text)}")
            # 移除 BOM
            return extracted_text.lstrip('\ufeff')
        else:
            print(f"    - pdfplumber 提取的文本过少或为空，尝试 OCR...")
            return ""
            # 继续执行 OCR 分支
    except ImportError:
        print(f"    - 未安装 pdfplumber，跳过文字提取，直接尝试 OCR: pip install pdfplumber")
    except Exception as e:
        print(f"    - pdfplumber 处理 PDF 失败: {e}")
        # 继续执行 OCR 分支
        return ""


    # --- 回退到 PyMuPDF + CnOCR ---
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text_lines = []
        print(f"    - 使用 PyMuPDF + CnOCR 处理 PDF，共 {doc.page_count} 页")
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)  # 降低 DPI
            img_data = pix.tobytes("png")
            
            if not img_data or len(img_data) == 0:
                print(f"      - 警告: 第 {page_num+1} 页渲染为空图片，跳过。")
                continue
            
            from PIL import Image
            import io
            try:
                image = Image.open(io.BytesIO(img_data))
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                ocr_result = ocr.ocr(image)
                if not ocr_result:
                    print(f"      - 警告: 第 {page_num+1} 页 OCR 结果为空。")
                    continue
                
                page_texts = [item[1] for item in ocr_result if item and len(item) > 1 and item[1]]
                text_lines.extend(page_texts)
                print(f"      - 第 {page_num+1} 页 OCR 完成，提取到 {len(page_texts)} 个文本块。")
            
            except Exception as img_e:
                print(f"      - 处理第 {page_num+1} 页图片时出错: {img_e}")
                continue
        
        doc.close()
        final_text = "\n".join(text_lines).strip()
        print(f"    - OCR 提取完成，总字符数: {len(final_text)}")
        # 移除 BOM
        return final_text.lstrip('\ufeff')
        
    except ImportError:
        print(f"❌ 需要安装 PyMuPDF (fitz) 来处理 PDF: pip install PyMuPDF")
        return ""
    except Exception as e:
        print(f"❌ OCR 识别 PDF 失败: {pdf_path}, 错误: {e}")
        return "" 

def split_text_by_length(text, max_len=2048):
    """将长文本按最大长度拆分为多个片段"""
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_len
        if end < len(text):
            break_point = -1
            for i in range(end, start, -1):
                if text[i] in '.。！？\n\r\t ' and i > start + max_len // 2:
                    break_point = i + 1
                    break
            if break_point != -1:
                end = break_point
        chunk = text[start:end]
        chunks.append(chunk)
        start = end
    return chunks

def process_directory(root_dir, output_jsonl_path="output.jsonl"):
    """遍历目录，处理所有 doc 和 pdf 文件"""
    with open(output_jsonl_path, 'w', encoding='utf-8') as f_out:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                text = ""
                
                if filename.lower().endswith('.doc'):
                    print(f"📄 正在处理旧版 DOC 文件: {filepath}")
                    text = extract_text_from_doc(filepath)
                elif filename.lower().endswith('.docx'):
                    print(f"📄 正在处理 DOCX 文件: {filepath}")
                    text = extract_text_from_docx(filepath)
                elif filename.lower().endswith('.pdf'):
                    print(f"📑 正在处理 PDF 文件: {filepath}")
                    text = extract_text_from_pdf(filepath)
                else:
                    continue  # 忽略其他格式

                if not text:
                    continue

                chunks = split_text_by_length(text, 2048)
                for chunk in chunks:
                    json_line = json.dumps({"text": chunk}, ensure_ascii=False)
                    f_out.write(json_line + '\n')
                    print(f"✅ 已写入一个文本块 (长度: {len(chunk)})")

    print(f"🎉 所有文件处理完成，结果已保存至: {output_jsonl_path}")

if __name__ == "__main__":
    ROOT_DIR = "/nfs/scistore19/alistgrp/stang/LLaMA-Factory/data/chemi_data_uncompressed/law/法律法规-03"
    OUTPUT_FILE = "laws_3rd_part.jsonl"

    if not os.path.exists(ROOT_DIR):
        print(f"❌ 目录不存在: {ROOT_DIR}")
    else:
        process_directory(ROOT_DIR, OUTPUT_FILE)