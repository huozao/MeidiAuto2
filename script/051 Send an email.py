import sys
import os
import glob
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from dotenv import load_dotenv

# ================================
# 文件路径配置
# ================================
default_inventory_folder = os.path.abspath(os.path.join(os.getcwd(), "data"))

if len(sys.argv) >= 2:
    inventory_folder = sys.argv[1]
    print(f"✅ 使用传入路径: {inventory_folder}")
else:
    inventory_folder = default_inventory_folder
    print(f"⚠️ 未传入路径，使用默认路径: {inventory_folder}")

if not os.path.exists(inventory_folder):
    print(f"❌ 文件夹路径不存在: {inventory_folder}")
    exit()

# ================================
# 找到最新图片（美的）
# ================================
image_pattern = os.path.join(inventory_folder, '*美的*.png')
image_files = glob.glob(image_pattern)

latest_image = None
if image_files:
    latest_image = max(image_files, key=os.path.getctime)
    print(f"✅ 找到最新的图片：{latest_image}")
else:
    print("❌ 没有找到符合条件的图片！")

# ================================
# 找到最新Excel（总库存）
# ================================
excel_pattern = os.path.join(inventory_folder, '*总库存*.xlsx')
excel_files = glob.glob(excel_pattern)

if excel_files:
    latest_excel = max(excel_files, key=os.path.getctime)
    print(f"✅ 找到最新的Excel文件：{latest_excel}")
else:
    print("❌ 没有找到符合条件的Excel文件！")
    exit()


# ================================
# 查找最新的 HTML 文件
# ================================
html_pattern = os.path.join(inventory_folder, 'output.html')  # 假设 HTML 文件名为 output.html
html_files = glob.glob(html_pattern)

html_content = None
if html_files:
    latest_html = max(html_files, key=os.path.getctime)  # 获取最新的 HTML 文件
    print(f"✅ 找到最新的 HTML 文件：{latest_html}")
    # 读取 HTML 文件内容
    with open(latest_html, 'r', encoding='utf-8') as file:
        html_content = file.read()
else:
    print("❌ 没有找到符合条件的 HTML 文件！")
    exit()

# 读取 HTML 内容
print(f"✅ 已成功读取 HTML 文件内容")


# ================================
# 邮件配置
# ================================
# 加载 .env 文件中的变量
load_dotenv()

# 从环境变量中读取邮箱和授权码
email_user = os.getenv("EMAIL_ADDRESS_QQ")
email_password = os.getenv("EMAIL_PASSWOR_QQ")  # 注意变量名拼写！

if not email_user or not email_password:
    raise ValueError("❌ 环境变量未正确配置，无法获取邮箱账户或密码！")

# 以下是你原本的逻辑
print("📬 正在使用邮箱:", email_user)

# 多个收件人的邮箱，使用逗号分隔
to_email_list = [ 'ishell@aliyun.com','ishell168@qq.com','zhou345616422@163.com'] #,'1421281576@qq.com'

# 将收件人邮箱列表转换为逗号分隔的字符串git remote set-url origin git@github.com:nihil7/
to_email = ', '.join(to_email_list)

subject = f"物料情况和Excel文件 - {os.path.basename(latest_image) if latest_image else '无图片  '}"


body = f"""
<html>
    <body>
        <p>您好，</p>

        <p>{html_content}</p>  <!-- 在这里插入生成的 HTML 内容 -->

        <p>祝您工作顺利！</p>
        
        <p>附件：<br>
        图片文件: {os.path.basename(latest_image) if latest_image else '无图片'}<br>
        Excel文件: {os.path.basename(latest_excel)}</p>

    </body>
</html>
"""

# ================================
# 构建邮件
# ================================
msg = MIMEMultipart()
msg['From'] = email_user
msg['To'] = to_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'html'))  # 设置邮件正文为 HTML 格式

# ================================
# 添加图片附件 (如果有图片的话)
# ================================
if latest_image:
    with open(latest_image, 'rb') as img_file:
        img_data = img_file.read()
        img = MIMEImage(img_data, name=os.path.basename(latest_image))
        msg.attach(img)

# ================================
# 添加 Excel 附件
# ================================
with open(latest_excel, 'rb') as excel_file:
    excel_data = excel_file.read()
    attachment = MIMEApplication(excel_data)
    attachment.add_header(
        'Content-Disposition',
        'attachment',
        filename=os.path.basename(latest_excel)
    )
    msg.attach(attachment)

# ================================
# 发送邮件
# ================================
try:
    server = smtplib.SMTP('smtp.qq.com', 587)
    server.starttls()
    server.login(email_user, email_password)
    server.send_message(msg)
    server.quit()
    print("✅ 邮件发送成功！")
except Exception as e:
    print(f"❌ 发送邮件时发生错误: {e}")
