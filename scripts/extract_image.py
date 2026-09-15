import os
import sys
import requests
import fitz  # PyMuPDF

def download_pdf(url, filename="temp.pdf"):
    """下载PDF文件到本地"""
    print(f"正在下载PDF: {url}")
    
    # 1. 构造完整的浏览器请求头，伪装成正常的 Chrome 浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive"
    }
    
    response = requests.get(url, stream=True, headers=headers)
    response.raise_for_status()
    
    # 2. 增加校验：检查返回的 Content-Type 是否包含 PDF 标识
    content_type = response.headers.get("Content-Type", "")
    print(f"服务器返回的 Content-Type: {content_type}")
    if "pdf" not in content_type.lower() and "octet-stream" not in content_type.lower():
        raise ValueError(f"下载失败！服务器返回的不是PDF文件，可能是被拦截或Token已过期。返回类型: {content_type}")

    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    # 3. 增加校验：检查文件大小，防止下载到空文件或纯文本错误页
    file_size = os.path.getsize(filename)
    print(f"下载完成，文件大小: {file_size} bytes")
    if file_size < 5000:  # 如果小于 5KB，大概率不是正常的教材PDF
        raise ValueError("下载的文件过小，可能不是有效的PDF文件，请检查链接Token是否有效！")
        
    return filename

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
            output_name = os.path.join("output", f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}")
            
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
