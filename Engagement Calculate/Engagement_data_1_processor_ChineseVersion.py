#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理脚本 - 处理特朗普政策分析的互动数据
根据 Header_explaination.csv 中的定义创建正确的表头并计算相应指标
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import os

def load_and_process_data():
    """
    加载原始数据并根据表头说明文件处理数据
    """
    # 文件路径
    raw_data_path = "Engagement_data_raw.csv"
    header_explanation_path = "Header_explaination.csv"
    output_path = "Engagement_data_processed.csv"
    
    print("正在加载原始数据...")
    # 加载原始数据
    df_raw = pd.read_csv(raw_data_path)
    
    print(f"原始数据包含 {len(df_raw)} 行记录")
    print(f"涵盖的平台: {df_raw['Platform'].unique()}")
    print(f"涵盖的类别: {df_raw['Category_id'].unique()}")
    
    # 按 Tag_id 分组计算各项指标
    print("\n正在计算各项指标...")
    
    # 创建结果字典
    results = []
    
    # 定义所有预期的标签（基于源文件结构）
    all_expected_tags = [
        'A1', 'A2', 'A3', 'A4', 'A5', 'A6',
        'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 
        'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8'
    ]
    
    # 获取原始数据中实际存在的标签
    actual_tags_in_data = df_raw['Tag_id'].unique()
    total_records = len(df_raw)  # 总记录数用于计算频率百分比
    
    print(f"预期标签总数: {len(all_expected_tags)}")
    print(f"实际数据中的标签: {len(actual_tags_in_data)}")
    
    # 遍历所有预期的标签，确保每个标签都有记录
    for tag_id in all_expected_tags:
        # 确定类别ID
        category_id = tag_id[0]  # A1 -> A, B2 -> B, C3 -> C
        
        # 检查该标签是否在原始数据中存在
        tag_data = df_raw[df_raw['Tag_id'].str.contains(tag_id, na=False)]
        
        if len(tag_data) > 0:
            # 有数据的标签 - 计算实际值
            # 1. Frequency (Count) - 提及次数（原始计数）
            frequency_count = len(tag_data)
            
            # 2. Frequency (%) - 频率占比
            frequency_percent = (frequency_count / total_records) * 100
            
            # 3. Total_Likes - 总点赞数
            total_likes = tag_data['Likes'].sum()
            
            # 4. Total_Reposts - 总转发数
            total_reposts = tag_data['Repost'].sum()
            
            # 5. Total_Comments - 总评论数（这里使用Replies列）
            total_comments = tag_data['Replies'].sum()
            
            # 6. Total_Engagement - 总互动量
            total_engagement = total_likes + total_reposts + total_comments
            
            # 7. X_Total_Engagement - X平台总互动量
            x_data = tag_data[tag_data['Platform'] == 'X']
            x_total_engagement = (x_data['Likes'].sum() + 
                                 x_data['Repost'].sum() + 
                                 x_data['Replies'].sum()) if len(x_data) > 0 else 0
            
            # 8. Truth_Total_Engagement - Truth Social平台总互动量
            truth_data = tag_data[tag_data['Platform'] == 'Truth Social']
            truth_total_engagement = (truth_data['Likes'].sum() + 
                                     truth_data['Repost'].sum() + 
                                     truth_data['Replies'].sum()) if len(truth_data) > 0 else 0
            
            # 9. Average_Engagement - 平均互动量
            average_engagement = total_engagement / frequency_count if frequency_count > 0 else 0
            
            # 10. X_Average_Engagement - X平台平均互动量
            x_frequency_count = len(x_data) if len(x_data) > 0 else 0
            x_average_engagement = x_total_engagement / x_frequency_count if x_frequency_count > 0 else 0
            
            # 11. Truth_Average_Engagement - Truth Social平台平均互动量
            truth_frequency_count = len(truth_data) if len(truth_data) > 0 else 0
            truth_average_engagement = truth_total_engagement / truth_frequency_count if truth_frequency_count > 0 else 0
            
        else:
            # 没有数据的标签 - 全部设为0
            frequency_count = 0
            frequency_percent = 0.0
            total_likes = 0
            total_reposts = 0
            total_comments = 0
            total_engagement = 0
            x_total_engagement = 0
            truth_total_engagement = 0
            average_engagement = 0.0
            x_average_engagement = 0.0
            truth_average_engagement = 0.0
        
        # 添加到结果列表
        results.append({
            'Tag_id': tag_id,
            'Category_id': category_id,
            'Frequency (Count)': frequency_count,
            'Frequency (%)': round(frequency_percent, 2),
            'Total_Likes': total_likes,
            'Total_Reposts': total_reposts,
            'Total_Comments': total_comments,
            'Total_Engagement': total_engagement,
            'X_Total_Engagement': x_total_engagement,
            'Truth_Total_Engagement': truth_total_engagement,
            'Average_Engagement': round(average_engagement, 2),
            'X_Average_Engagement': round(x_average_engagement, 2),
            'Truth_Average_Engagement': round(truth_average_engagement, 2)
        })
    
    # 创建DataFrame
    df_processed = pd.DataFrame(results)
    
    # 按Category_id和Tag_id排序
    df_processed = df_processed.sort_values(['Category_id', 'Tag_id'])
    
    # 保存处理后的数据
    df_processed.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"\n数据处理完成！")
    print(f"处理后的数据已保存到: {output_path}")
    print(f"共处理了 {len(df_processed)} 个不同的政策标签")
    
    # 显示统计信息
    print(f"\n数据统计:")
    print(f"- 总提及次数: {df_processed['Frequency (Count)'].sum()}")
    print(f"- 总互动量: {df_processed['Total_Engagement'].sum():,}")
    print(f"- 平均每个标签的互动量: {df_processed['Average_Engagement'].mean():.2f}")
    
    # 显示前几行数据预览
    print(f"\n处理后数据预览:")
    print(df_processed.head())
    
    return df_processed

def display_header_explanations():
    """
    显示表头说明信息
    """
    header_explanation_path = "Header_explaination.csv"
    
    if os.path.exists(header_explanation_path):
        print("=" * 80)
        print("表头说明 (根据 Header_explaination.csv):")
        print("=" * 80)
        
        df_headers = pd.read_csv(header_explanation_path)
        for _, row in df_headers.iterrows():
            if pd.notna(row['Header']) and row['Header'] != '':
                print(f"\n【{row['Header']}】")
                print(f"中文名称: {row['中文解释']}")
                print(f"说明: {row['在研究中的作用和意义']}")
        print("=" * 80)

if __name__ == "__main__":
    print("特朗普政策分析 - 互动数据处理脚本")
    print("=" * 50)
    
    # 显示表头说明
    display_header_explanations()
    
    # 处理数据
    try:
        processed_data = load_and_process_data()
        print("\n数据处理成功完成！")
        
        # 提供一些额外的分析信息
        print(f"\n快速分析:")
        top_engagement = processed_data.nlargest(5, 'Average_Engagement')[['Tag_id', 'Average_Engagement']]
        print(f"\n平均互动量最高的5个政策标签:")
        for _, row in top_engagement.iterrows():
            print(f"  {row['Tag_id']}: {row['Average_Engagement']:.2f}")
            
        most_frequent = processed_data.nlargest(5, 'Frequency (Count)')[['Tag_id', 'Frequency (Count)']]
        print(f"\n提及次数最多的5个政策标签:")
        for _, row in most_frequent.iterrows():
            print(f"  {row['Tag_id']}: {row['Frequency (Count)']} 次")
            
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        print("请检查文件路径和数据格式是否正确。")
