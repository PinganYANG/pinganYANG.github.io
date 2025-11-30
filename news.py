# %%
import requests
from bs4 import BeautifulSoup
import datetime

today = str(datetime.date.today() - datetime.timedelta(1)).replace('-', '')
url = f"https://cn.govopendata.com/xinwenlianbo/{today}/"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'  # 防止中文乱码

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到所有 article 区块
    articles = soup.find_all("article")
    print(f"共找到 {len(articles)} 条新闻：\n")

    full_article = """"""
    for i, article in enumerate(articles, start=1):
        title = article.find("h2")
        content = article.find("p")

        title_text = title.get_text(strip=True) if title else "[无标题]"
        content_text = content.get_text(strip=True) if content else "[无正文]"

        print(f"【第{i}条】")
        full_article += f"\n标题：{title_text}\n正文：{content_text}"

        print("标题：", title_text)
        print("正文：", content_text)
        print("-" * 80)
else:
    print("网页请求失败，状态码：", response.status_code)


# %%
system_prompt = '''
### **新闻联播深度分析指令（供应链/投资/创业视角）**
**角色设定**：您是中国经济政策分析师+全球供应链研究员+风险投资顾问的复合型专家，擅长从新闻联播中挖掘产业信号、政策红利和供应链变动机遇。

**我的需求**：当我提供新闻联播全文（含标题+正文）时，请按以下框架结构化输出：

#### **0. 总结**
按照
标题-对应简短概括重要内容
的方式首先进行总结，数量一定要对等，不能简略！

#### **1. 关键政策信号提取**
- 🔍 **标题解码**：用`[政策信号]`标注隐含导向（如“乡村振兴”→农村基建投资机会）
- ⚠️ **敏感词预警**：标记`【红利领域】`（如“专精特新”）/`【风险领域】`（如“产能调控”）

#### **2. 三维影响分析**
```markdown
| 维度        | 分析要点                                  | 您的视角适配               |
|-------------|------------------------------------------|---------------------------|
| **供应链**  | 原材料/物流/产能布局变化                 | 跨境替代方案/成本预测     |
| **国内市场**| 消费激励/行业准入/区域经济动向           | 渠道下沉/ToB服务机会      |
| **全球链动**| 关键技术出口管制/国际合作协议            | 海外仓布局/替代供应链国别 |
```

#### **3. 历史事件锚定**
- 📅 **政策连续性**：例：“对比2023年中央经济工作会议，本次新增______表述”
- 👥 **人物关联**：例：“某部长发言延续其在XX会议立场，暗示______领域将加码”

#### **4. 创业机会矩阵**
```diff
! 必含板块 !
+ 低垂果实：3个月内可切入场景（如“老旧小区改造”→社区团购冷链）
+ 长期押注：技术突破方向（如“6G研发”→卫星物联网部件）
```

#### **5. 投资者行动清单**
- ✅ **利好标的**：关联上市公司/细分赛道（例：“农村电商推进”→农产品溯源技术商）
- ⛔ **规避提示**：受冲击行业及替代方案（例：“塑料禁令”→生物材料企业清单）

#### **6. 关键问题生成**
提出1-2个需后续追踪的核心问题（例：“某政策细则未公布→关注XX部委官网窗口期”）

'''

# %%
user_prompt = f''' 

以下是新闻联播全文
{full_article}

最后请你转换纯inline CSS 的很美观的html格式，序号要对，表格要有，不要太简洁，便于我来解析。此外不要使用markdown格式，目标无法解析
此外为了保证合规，请你将习总书记、党等内容替换为可理解的其他更能避免合规审查的内容
'''

# %%

from openai import OpenAI


response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    stream=False
)

print(response.choices[0].message.content)

# %%
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
import traceback

# 邮件配置
smtp_server = 'smtp.163.com'
smtp_port = 465
sender_email = 'cimumuxyz@163.com'
sender_password = ''  # SMTP授权码
receiver_email = 'ping_an0317@163.com'
subject = '当日新闻总结'

# 读取HTML文件内容
html_content = response.choices[0].message.content


# 创建邮件内容
msg = MIMEText(html_content, 'html', 'utf-8')
msg['From'] = Header(sender_email, 'utf-8')
msg['To'] = Header(receiver_email, 'utf-8')
msg['Subject'] = Header(subject, 'utf-8')
msg['Date'] = formatdate(localtime=True)

# 发送邮件并记录日志
log_message = ""
try:
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    log_message = "发送状态: 成功\n发送时间: " + formatdate(localtime=True)
except Exception as e:
    log_message = f"发送状态: 失败\n错误信息: {str(e)}\n堆栈跟踪: {traceback.format_exc()}"
finally:
    with open('邮件发送结果.txt', 'w', encoding='utf-8') as log_file:
        log_file.write(log_message)
    print("邮件发送结果.txt")

# %%



