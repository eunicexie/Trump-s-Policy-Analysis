#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

def setup_driver():
    """配置并初始化Chrome浏览器"""
    chrome_options = Options()
    # 取消下面注释可以使浏览器在后台运行
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # 添加用户代理以模拟真实浏览器
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
    
    # 推荐使用os.path模块获取当前脚本所在目录，确保路径始终正确
    import os
    driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver")
    service = Service(driver_path)
    
    # 初始化WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    return driver

def parse_date(date_text):
    """将日期文本解析为标准格式"""
    try:
        # 如果日期为空或只是一个点，则返回None
        if not date_text or date_text == '•':
            return None
            
        # Roll Call日期格式: "April 18, 2025 @ 6:28 PM ET"
        # 首先移除ET后缀
        date_text = date_text.replace(' ET', '')
        
        # 处理@符号
        if '@' in date_text:
            date_text = date_text.replace(' @ ', ' ')
        
        formats = [
            '%B %d, %Y %I:%M %p',         # "April 18, 2025 6:28 PM"
            '%b %d, %Y %I:%M %p',         # "Apr 18, 2025 6:28 PM"
        ]
        
        # 尝试直接使用格式列表
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_text.strip(), fmt)
                return date_obj.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
                
        # 如果直接解析失败，尝试正则表达式
        date_pattern = r'([A-Za-z]+)\s+(\d+),\s+(\d{4})\s+(\d{1,2}):(\d{2})\s+([APM]{2})'
        match = re.search(date_pattern, date_text)
        
        if match:
            month, day, year, hour, minute, am_pm = match.groups()
            
            # 将月份转换为数字
            month_dict = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
                'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            month_num = month_dict.get(month.lower(), 1)
            
            # 转换小时为24小时制
            hour = int(hour)
            if am_pm.lower() == 'pm' and hour < 12:
                hour += 12
            elif am_pm.lower() == 'am' and hour == 12:
                hour = 0
                
            # 创建日期对象
            try:
                date_obj = datetime(int(year), month_num, int(day), hour, int(minute))
                return date_obj.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
                
        # 如果所有方法都失败，返回原始文本并记录日志
        print(f"无法解析日期格式: '{date_text}'")
        return date_text
    except Exception as e:
        print(f"日期解析错误: {e}, 日期文本: {date_text}")
        return date_text

def scroll_down(driver, scroll_pause_time=2, max_scrolls=None):
    """滚动页面以加载更多内容"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    
    while True:
        # 滚动到页面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # 等待页面加载
        time.sleep(scroll_pause_time)
        
        # 计算新的滚动高度
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # 如果设置了最大滚动次数并且达到该次数，则中止
        if max_scrolls and scrolls >= max_scrolls:
            print(f"已达到最大滚动次数 {max_scrolls}")
            break
            
        # 如果高度没有变化，说明已经到底部
        if new_height == last_height:
            print("已到达页面底部，无法加载更多内容")
            break
            
        last_height = new_height
        scrolls += 1
        print(f"滚动加载更多内容... (第 {scrolls} 次)")

def extract_card_data(driver, post_elem):
    """从帖子HTML元素中提取信息"""
    data = {
        'published_at_utc': None,
        'source_type': 'Twitter',  # 这个页面都是Twitter内容
        'statement_text': None,
        'source_url': None,
        'post_id': None,
        'image_url': None
    }
    
    try:
        # 使用Selenium直接获取渲染后的内容
        
        # 提取日期 - 使用JavaScript渲染后的内容
        try:
            date_elem = post_elem.find_element(By.CSS_SELECTOR, "span.hidden.md\\:inline")
            if date_elem.is_displayed():
                data['published_at_utc'] = parse_date(date_elem.text.strip())
        except NoSuchElementException:
            print("未找到日期元素")
        
        # 提取文本内容 - 使用JavaScript渲染后的内容
        try:
            text_elem = post_elem.find_element(By.CSS_SELECTOR, "div.text-sm.font-medium.whitespace-pre-wrap")
            if text_elem.is_displayed():
                data['statement_text'] = text_elem.text.strip()
        except NoSuchElementException:
            print("未找到文本内容元素")
        
        # 提取Twitter链接
        try:
            link_elem = post_elem.find_element(By.CSS_SELECTOR, "a[href^='https://x.com/realdonaldtrump/status/']")
            if link_elem:
                data['source_url'] = link_elem.get_attribute("href")
                # 从URL中提取推文ID
                match = re.search(r'status/(\d+)', data['source_url'])
                if match:
                    data['post_id'] = match.group(1)
        except NoSuchElementException:
            print("未找到Twitter链接元素")
        
        # 提取图片URL
        try:
            img_elem = post_elem.find_element(By.CSS_SELECTOR, "img[src^='https://media-cdn.factba.se/realdonaldtrump-twitter/']")
            if img_elem:
                data['image_url'] = img_elem.get_attribute("src")
        except NoSuchElementException:
            print("未找到图片元素")
            
    except Exception as e:
        print(f"提取卡片数据时出错: {e}")
    
    return data

def is_date_in_range(date_str, start_date, end_date):
    """检查日期是否在指定范围内"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return start_date <= date <= end_date
    except (ValueError, TypeError):
        return False

def extract_json_data(driver):
    """尝试从页面中提取JSON数据"""
    try:
        # 执行JavaScript获取Alpine.js存储的数据
        script = """
        try {
            // 尝试获取Alpine.js存储的数据
            const posts = Alpine.store('posts');
            return JSON.stringify(posts.items);
        } catch (e) {
            return null;
        }
        """
        json_data = driver.execute_script(script)
        if json_data:
            return json.loads(json_data)
    except Exception as e:
        print(f"提取JSON数据失败: {e}")
    return None

def scrape_trump_statements():
    """抓取特朗普言论数据的主函数"""
    # 设置日期范围
    start_date = datetime(2025, 1, 20)
    end_date = datetime(2025, 4, 20)
    
    driver = setup_driver()
    all_statements = []
    processed_posts = set()  # 用于跟踪已处理的帖子
    
    try:
        # 访问Twitter内容页面
        url = "https://rollcall.com/factbase-twitter/?platform=twitter&sort=date&sort_order=desc&page=1"
        driver.get(url)
        
        print(f"访问URL: {url}")
        
        # 等待页面加载
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.block.mb-8.rounded-xl"))
            )
        except TimeoutException:
            print("页面加载超时，尝试继续执行...")
        
        # 滚动页面以加载更多内容
        print("开始滚动页面加载更多内容...")
        scroll_down(driver, scroll_pause_time=3, max_scrolls=20)  # 设置适当的滚动次数
        
        # 首先尝试从JavaScript中提取JSON数据
        json_data = extract_json_data(driver)
        if json_data:
            print(f"成功从JavaScript中提取了 {len(json_data)} 条记录")
            
            for item in json_data:
                # 检查是否已处理过该帖子
                if 'id' in item and item['id'] in processed_posts:
                    continue
                    
                if 'id' in item:
                    processed_posts.add(item['id'])
                
                post_data = {
                    'published_at_utc': None,
                    'source_type': 'Twitter',
                    'statement_text': None,
                    'source_url': None,
                    'post_id': None,
                    'image_url': None
                }
                
                # 提取日期
                if 'date' in item:
                    try:
                        date_obj = datetime.fromtimestamp(item['date'] / 1000)  # 假设是毫秒时间戳
                        post_data['published_at_utc'] = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception as e:
                        print(f"解析日期出错: {e}")
                
                # 提取文本内容
                if 'text' in item:
                    post_data['statement_text'] = item['text']
                
                # 提取链接和ID
                if 'post_url' in item:
                    post_data['source_url'] = item['post_url']
                    match = re.search(r'status/(\d+)', post_data['source_url'])
                    if match:
                        post_data['post_id'] = match.group(1)
                
                # 提取图片URL
                if 'image_url' in item:
                    post_data['image_url'] = item['image_url']
                
                # 日期检查
                if post_data['published_at_utc'] and is_date_in_range(post_data['published_at_utc'], start_date, end_date):
                    all_statements.append(post_data)
                    print(f"找到符合日期范围的帖子: {post_data['published_at_utc']}")
        else:
            # 如果无法从JavaScript提取数据，则使用Selenium直接从DOM中提取
            print("无法从JavaScript提取数据，尝试直接从DOM中提取...")
            
            # 获取所有推文卡片
            post_elements = driver.find_elements(By.CSS_SELECTOR, "div.block.mb-8.rounded-xl")
            print(f"找到 {len(post_elements)} 个推文卡片")
            
            for post_elem in post_elements:
                # 提取数据
                post_data = extract_card_data(driver, post_elem)
                
                # 检查是否已处理过该帖子
                if post_data['post_id'] and post_data['post_id'] in processed_posts:
                    continue
                    
                if post_data['post_id']:
                    processed_posts.add(post_data['post_id'])
                
                # 确保提取了关键字段
                if not post_data['statement_text'] and not post_data['image_url']:
                    print("警告：未提取到文本内容或图片")
                    continue
                    
                # 打印提取的数据用于调试
                print(f"提取的数据: 日期={post_data['published_at_utc']}, ID={post_data['post_id']}")
                print(f"内容: {post_data['statement_text'][:50]}..." if post_data['statement_text'] else "无文本内容")
                
                # 日期检查
                if post_data['published_at_utc'] and is_date_in_range(post_data['published_at_utc'], start_date, end_date):
                    all_statements.append(post_data)
                    print(f"找到符合日期范围的帖子: {post_data['published_at_utc']}")
    
    except Exception as e:
        print(f"抓取过程中发生错误: {e}")
    
    finally:
        driver.quit()
    
    # 将数据转换为DataFrame并保存
    df = pd.DataFrame(all_statements)
    
    # 确保关键字段存在
    required_fields = ['published_at_utc', 'source_url', 'statement_text', 'post_id', 'image_url']
    for field in required_fields:
        if field not in df.columns:
            df[field] = None
    
    # 重命名字段，使其更直观
    df = df.rename(columns={
        'published_at_utc': '日期', 
        'source_url': '帖子链接', 
        'statement_text': '文本内容',
        'post_id': '推文ID',
        'image_url': '图片链接'
    })
    
    # 保存CSV，使用UTF-8编码并带BOM标记，以便Excel正确显示中文
    df.to_csv('trump_statements_data_base.csv', index=False, encoding='utf-8-sig')
    print(f"已保存 {len(df)} 条记录到 trump_statements_data_base.csv")

if __name__ == "__main__":
    scrape_trump_statements() 