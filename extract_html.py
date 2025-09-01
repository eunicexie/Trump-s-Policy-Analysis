from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
import json
import traceback

# 全局变量，用于保存浏览器实例
browser_instance = None

def setup_driver():
    """设置并返回Chrome WebDriver"""
    global browser_instance
    
    # 如果已有浏览器实例，则返回它
    if browser_instance:
        return browser_instance
        
    options = Options()
    # 添加更多的浏览器选项来减少被识别为爬虫的可能性
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--window-size=1920,1080")
    
    # 设置用户代理
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    options.add_argument(f'user-agent={user_agent}')
    
    driver = webdriver.Chrome(options=options)
    
    # 修改navigator.webdriver属性以避免被检测
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.maximize_window()
    
    # 保存浏览器实例
    browser_instance = driver
    return driver

def extract_page_html(driver):
    """提取页面HTML结构"""
    try:
        # 检查是否已在目标页面
        current_url = driver.current_url
        if not "worldcat.org" in current_url and not "nexis" in current_url.lower():
            print("正在打开RUG WorldCat页面...")
            driver.get("https://rug.on.worldcat.org/discovery")
            
            # 等待页面加载
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 等待用户手动导航并登录
            print("\n请手动导航到目标页面并登录...")
            input("准备好后请按Enter键继续...")
        else:
            print(f"已经在目标网站上: {current_url}")
        
        # 给页面一些额外的加载时间
        print("等待页面完全加载...")
        time.sleep(3)
        
        # 提取HTML
        print("正在提取页面HTML...")
        
        # 获取主页面HTML并检查是否为None
        html = None
        retry_count = 0
        max_retries = 3
        
        while html is None and retry_count < max_retries:
            try:
                # 尝试不同的方法获取HTML
                if retry_count == 0:
                    html = driver.page_source
                elif retry_count == 1:
                    html = driver.execute_script("return document.documentElement.outerHTML;")
                else:
                    # 最后尝试刷新页面后再获取
                    print("尝试刷新页面...")
                    driver.refresh()
                    time.sleep(5)
                    html = driver.execute_script("return document.documentElement.outerHTML;")
                
                # 检查HTML是否实际包含内容
                if html and len(html.strip()) < 100:
                    print(f"警告: HTML内容过少 ({len(html.strip())} 字符)，可能被反爬")
                    html = None
                    
            except Exception as e:
                print(f"获取HTML时出错: {e}")
                html = None
                
            if html is None:
                retry_count += 1
                print(f"重试获取HTML ({retry_count}/{max_retries})...")
                time.sleep(2)
            
        if html:
            # 保存HTML到文件
            filename = f"page_source_{int(time.time())}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"HTML已保存到 {filename}")
        else:
            print("错误: 无法获取页面源码")
            return False
        
        # 提取各种信息
        extract_elements_data(driver)
        
        print("\n提取完成！")
        return True
        
    except Exception as e:
        print(f"发生错误: {e}")
        traceback.print_exc()
        return False

def extract_elements_data(driver):
    """提取页面上各种元素的数据"""
    # 提取复选框信息
    extract_checkboxes(driver)
    
    # 提取分页导航信息
    extract_pagination(driver)
    
    # 提取可见元素
    extract_visible_elements(driver)

def extract_checkboxes(driver):
    """提取页面上的复选框"""
    print("\n提取复选框信息...")
    try:
        checkboxes = driver.execute_script("""
            var checkboxes = document.querySelectorAll('input[type="checkbox"]');
            var result = [];
            for (var i = 0; i < checkboxes.length; i++) {
                var cb = checkboxes[i];
                result.push({
                    id: cb.id || 'no-id',
                    class: cb.className || 'no-class',
                    name: cb.name || 'no-name',
                    attributes: (function() {
                        var attrs = {};
                        for (var j = 0; j < cb.attributes.length; j++) {
                            var attr = cb.attributes[j];
                            attrs[attr.name] = attr.value;
                        }
                        return attrs;
                    })(),
                    isVisible: cb.offsetParent !== null,
                    isChecked: cb.checked,
                    xpath: generateXPath(cb)
                });
            }
            
            // 辅助函数：生成元素的XPath
            function generateXPath(element) {
                if (element.id !== '')
                    return 'id("' + element.id + '")';
                if (element === document.body)
                    return '//' + element.tagName.toLowerCase();

                var ix = 0;
                var siblings = element.parentNode.childNodes;
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === element)
                        return generateXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                    if (sibling.nodeType === 1 && sibling.tagName.toLowerCase() === element.tagName.toLowerCase())
                        ix++;
                }
            }
            
            return JSON.stringify(result);
        """)
        
        # 保存复选框信息到文件
        if checkboxes:
            timestamp = int(time.time())
            with open(f"checkboxes_info_{timestamp}.json", "w", encoding="utf-8") as f:
                f.write(checkboxes)
            print(f"复选框信息已保存到 checkboxes_info_{timestamp}.json")
            print(f"找到 {checkboxes.count('{')} 个复选框")
        else:
            print("未找到复选框")
    except Exception as e:
        print(f"提取复选框信息时发生错误: {e}")

def extract_pagination(driver):
    """提取分页导航信息"""
    print("\n提取分页导航信息...")
    try:
        pagination = driver.execute_script("""
            var navElements = document.querySelectorAll('nav');
            var result = [];
            for (var i = 0; i < navElements.length; i++) {
                var nav = navElements[i];
                var links = nav.querySelectorAll('a');
                var linkInfo = [];
                
                for (var j = 0; j < links.length; j++) {
                    var link = links[j];
                    linkInfo.push({
                        text: link.textContent.trim(),
                        href: link.getAttribute('href'),
                        class: link.className,
                        html: link.outerHTML,
                        attributes: (function() {
                            var attrs = {};
                            for (var k = 0; k < link.attributes.length; k++) {
                                var attr = link.attributes[k];
                                attrs[attr.name] = attr.value;
                            }
                            return attrs;
                        })()
                    });
                }
                
                result.push({
                    role: nav.getAttribute('role') || 'no-role',
                    class: nav.className || 'no-class',
                    html: nav.outerHTML,
                    links: linkInfo
                });
            }
            return JSON.stringify(result);
        """)
        
        # 保存分页信息到文件
        if pagination:
            timestamp = int(time.time())
            with open(f"pagination_info_{timestamp}.json", "w", encoding="utf-8") as f:
                f.write(pagination)
            print(f"分页导航信息已保存到 pagination_info_{timestamp}.json")
        else:
            print("未找到分页导航")
    except Exception as e:
        print(f"提取分页导航信息时发生错误: {e}")

def extract_visible_elements(driver):
    """提取可见元素"""
    print("\n提取页面上的可见元素...")
    try:
        visible_elements = driver.execute_script("""
            function isVisible(element) {
                if (!element.offsetParent && element.offsetParent !== document.body)
                    return false;
                if (window.getComputedStyle(element).visibility === 'hidden')
                    return false;
                return true;
            }
            
            function getVisibleElements() {
                var all = document.querySelectorAll('*');
                var result = [];
                
                for (var i = 0; i < Math.min(all.length, 1000); i++) {  // 限制数量避免过大
                    var el = all[i];
                    if (el.tagName && isVisible(el) && ['INPUT', 'BUTTON', 'A', 'LI', 'SPAN', 'DIV'].includes(el.tagName)) {
                        var text = el.innerText ? el.innerText.trim() : '';
                        // 只包含有意义的元素
                        if (text || el.tagName === 'INPUT' || el.tagName === 'BUTTON') {
                            result.push({
                                tag: el.tagName.toLowerCase(),
                                id: el.id || '',
                                class: el.className || '',
                                type: el.getAttribute('type') || '',
                                text: text.substring(0, 100),  // 限制文本长度
                                attributes: {
                                    'data-action': el.getAttribute('data-action') || '',
                                    'aria-label': el.getAttribute('aria-label') || '',
                                    'role': el.getAttribute('role') || ''
                                }
                            });
                        }
                    }
                }
                return result;
            }
            
            return JSON.stringify(getVisibleElements());
        """)
        
        # 保存可见元素信息到文件
        if visible_elements:
            timestamp = int(time.time())
            with open(f"visible_elements_{timestamp}.json", "w", encoding="utf-8") as f:
                f.write(visible_elements)
            print(f"可见元素信息已保存到 visible_elements_{timestamp}.json")
        else:
            print("未找到可见元素")
    except Exception as e:
        print(f"提取可见元素信息时发生错误: {e}")

def main_menu(driver=None):
    """主菜单，允许用户选择操作"""
    global browser_instance
    
    if not driver:
        driver = setup_driver()
    
    while True:
        print("\n========== 提取工具菜单 ==========")
        print("1. 提取当前页面HTML和元素信息")
        print("2. 打开WorldCat网站")
        print("3. 刷新当前页面")
        print("4. 退出程序")
        if browser_instance:
            print("5. 关闭浏览器")
        
        choice = input("\n请选择操作 (1-5): ").strip()
        
        if choice == '1':
            extract_page_html(driver)
            
        elif choice == '2':
            driver.get("https://rug.on.worldcat.org/discovery")
            print("已打开WorldCat网站，请手动登录...")
            
        elif choice == '3':
            driver.refresh()
            print("页面已刷新")
            
        elif choice == '4':
            print("退出程序...")
            return
            
        elif choice == '5' and browser_instance:
            browser_instance.quit()
            browser_instance = None
            print("浏览器已关闭")
            return
            
        else:
            print("无效选择，请重试")

if __name__ == "__main__":
    try:
        driver = setup_driver()
        main_menu(driver)
    except Exception as e:
        print(f"程序出错: {e}")
        traceback.print_exc()
        
    # 退出时检查是否要关闭浏览器
    if browser_instance:
        close = input("是否关闭浏览器？(y/n): ").strip().lower()
        if close == 'y':
            browser_instance.quit()
            print("浏览器已关闭")
        else:
            print("浏览器保持打开状态，请手动关闭") 