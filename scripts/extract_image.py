import os
import sys
import requests
import fitz  # PyMuPDF

def download_pdf(url, filename="temp.pdf"):
    """下载PDF文件到本地"""
    print(f"正在下载PDF: {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("下载完成。")

def extract_images_from_page(pdf_path, page_num):
    """提取指定页码中的所有图片"""
    try:
        doc = fitz.open(pdf_path)
        if page_num < 0 or page_num >= len(doc):
            raise ValueError(f"页码超出范围！PDF共有 {len(doc)} 页，有效范围是 0 到 {len(doc)-1}")
        
        page = doc[page_num]
        # 获取当前页的所有图片对象
        image_list = page.get_images(full=True)
        
        if not image_list:
            print(f"警告: 第 {page_num + 1} 页未找到任何图片对象。")
            sys.exit(0)
            
        print(f"在第 {page_num + 1} 页找到 {len(image_list)} 张图片，开始提取...")
        
        # 遍历并提取每张图片
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # 命名规则：page_{页码}_img_{序号}.{后缀}
            output_name = os.path.join("output",f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}")
            
            with open(output_name, "wb") as image_file:
                image_file.write(image_bytes)
                
            print(f"成功保存: {output_name}")
            
        doc.close()
    except Exception as e:
        print(f"提取图片时发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    pdf_url = os.getenv("PDF_URL")
    page_number_str = os.getenv("PAGE_NUMBER")

    if not pdf_url or not page_number_str:
        print("错误: 缺少 PDF_URL 或 PAGE_NUMBER 环境变量")
        sys.exit(1)

    try:
        page_num = int(page_number_str)
    except ValueError:
        print("错误: 页码必须是整数")
        sys.exit(1)

    pdf_file = download_pdf(pdf_url)
    extract_images_from_page(pdf_file, page_num)
